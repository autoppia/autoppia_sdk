# from crewai import Agent, Crew, Process, Task
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from autoppia_agentic_framework.src.ai_bootstrap import AIBootstrap
from autoppia_agentic_framework.src.processes.application.openai.new_message import (
    OpenAINewMessageProccess,
)
from autoppia_agentic_framework.src.processes.application.openai.stop_run import OpenAIStopRun
from autoppia_agentic_framework.src.processes.application.openai.submit_tools import (
    OpenAISubmitToolsOutputProccess,
)
from autoppia_agentic_framework.src.threads.application.openai.openai_assistant import OpenAIAssistant
from autoppia_agentic_framework.src.threads.application.openai.thread_manager import (
    OpenAIThreadManager,
)
from autoppia_agentic_framework.src.tools.application.all import all_toolkits
from autoppia_agentic_framework.src.tools.domain.classes import ToolkitList
from autoppia_sdk.src.orchestration.workers.adapter import AIWorkerAdapter
from autoppia_sdk.src.standardization.toolkits.interfaces import UserToolkit


class AIWorker:
    def __init__(self, worker_id=None, worker_dto=None):
        self.worker_id = worker_id
        self.ai_worker_adapter = AIWorkerAdapter(worker_id, worker_dto)
        (
            self.user_llm,
            self.vector_store,
            self.user_toolkits,
            self.agent,
            self.instruction,
        ) = self.ai_worker_adapter.from_backend()
        self.toolkits = None
        self.thread_manager = None
        self.assistant_id = "asst_w0AnuWWxOUYanQNOiQGLJlZR"
        self.called_tools = []
        self.retrieval = True
        self.langchain_agent = None
        self.agent_executor = None

    def _configure_browser_toolkit(self, action_message):
        """Configure browser toolkit if needed"""
        if (
            not any(toolkit.toolkit_name == "Browser" for toolkit in self.user_toolkits)
            and action_message
        ):
            browser_toolkit = UserToolkit(
                toolkit_name="Browser",
                context={"action_message": action_message},
                instruction="""
                    There is execute_browser_action tool, so you should use this tool for browser actions such as clicking, navigate, modify style, fill input etc.
                    Before executing browser action you should call get_current_page tool so that you must know about current page html.
                """,
            )
            self.user_toolkits.append(browser_toolkit)

    def _configure_retrieval_toolkit(self, chat_session_id):
        """Configure retrieval toolkit if needed"""
        if not isinstance(self.vector_store, str) and chat_session_id:
            filter_conditions = [{"type": "standard"}, {"worker": self.worker_id}]
            if chat_session_id:
                filter_conditions.append({"chat_session": chat_session_id})

            retrieval_toolkit = UserToolkit(
                toolkit_name="Retrieval",
                context={
                    "vector_store": self.vector_store,
                    "filter": {"$or": filter_conditions},
                },
            )
            self.user_toolkits.append(retrieval_toolkit)
            self.retrieval = False

    def thread_setup(
        self,
        send_message=None,
        action_message=None,
        chat_session_id=None,
        thread_id=None,
        test_mode=False,
    ):
        self._configure_browser_toolkit(action_message)
        self._configure_retrieval_toolkit(chat_session_id)

        # Update toolkits list
        user_toolkit_names = {item.toolkit_name for item in self.user_toolkits}
        toolkits = [
            toolkit for toolkit in all_toolkits if toolkit.name in user_toolkit_names
        ]
        self.toolkits = ToolkitList(toolkits, self.user_toolkits)

        # Initialize AI components
        bootstrap = AIBootstrap()
        self.llmModel = self._get_llm_model(bootstrap)
        self.instructions = self.instruction

        if self.agent == "openai":
            self._setup_openai_assistant(thread_id, test_mode)

    def _get_llm_model(self, bootstrap):
        """Get appropriate LLM model"""
        llm_model_map = {
            "GPT-4": bootstrap.container.gpt4,
            "GPT-4o": bootstrap.container.gpt4o,
        }
        return llm_model_map.get(self.user_llm, bootstrap.container.default_model)()

    def _setup_openai_assistant(self, thread_id, test_mode):
        """Setup OpenAI assistant and thread manager"""
        openai_assistant = OpenAIAssistant.get_or_create(
            self.assistant_id,
            "Task Executor",
            self.instructions,
            self.llmModel,
            self.toolkits,
            None,
            True,
            self.retrieval,
            test_mode,
        )
        if isinstance(self.vector_store, str):
            openai_assistant.update_assistant(self.assistant_id, self.vector_store)

        if thread_id and thread_id != "None":
            self.thread_manager = OpenAIThreadManager.get(thread_id)

    def process_message(
        self,
        thread_id,
        message,
        message_with_history=None,
        send_message=None,
        save_new_messages_in_db=None,
        save_thread_id_in_db=None,
        last_uploaded_file=None,
        save_new_function_tool_in_db=None,
    ):
        if self.agent == "openai":
            return OpenAINewMessageProccess(thread_id).start(
                message,
                self.thread_manager,
                self.assistant_id,
                self.user_toolkits,
                send_message,
                save_new_messages_in_db,
                save_thread_id_in_db,
                last_uploaded_file,
                self.update_tools,
                self.called_tools,
            )
        elif self.agent == "langchain":
            return self._handle_langchain_message(
                message_with_history,
                send_message,
                save_new_messages_in_db,
                save_new_function_tool_in_db,
            )

    def _handle_langchain_message(
        self,
        message_with_history,
        send_message,
        save_new_messages_in_db,
        save_new_function_tool_in_db,
    ):
        """Handle message processing for Langchain agent"""
        if not self.agent_executor:
            self._initialize_langchain_agent(send_message, save_new_function_tool_in_db)

        result = self.agent_executor.invoke({"input": message_with_history})
        msg = {
            "role": "assistant",
            "text": result["output"],
            "type": "text",
        }
        save_new_messages_in_db([msg])
        send_message(msg)

        return result["output"], self.called_tools

    def _initialize_langchain_agent(self, send_message, save_new_function_tool_in_db):
        """Initialize Langchain agent and executor"""
        langchain_tools = self.toolkits.to_langchain_tools(
            send_message, save_new_function_tool_in_db, self.update_tools
        )
        llm = ChatOpenAI(model="gpt-4o")
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are very powerful assistant, but don't know current events",
                ),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )
        self.langchain_agent = create_tool_calling_agent(llm, langchain_tools, prompt)
        self.agent_executor = AgentExecutor(
            agent=self.langchain_agent, tools=langchain_tools, verbose=True
        )

        # elif self.agent == "crewai":
        #     langchain_tools = self.toolkits.to_langchain_tools(
        #         send_message, save_new_function_tool_in_db
        #     )

        #     # Create the LLM provider
        #     # llm = ChatOpenAI(model="gpt-4o")
        #     # llm = ChatGroq(model="groq/mixtral-8x7b-32768")

        #     self.crew_agent = Agent(
        #         role="Assistant",
        #         goal="Answer the question with calling suitable tools if you need.",
        #         backstory=self.instructions,
        #         tools=langchain_tools,
        #         llm=self.llmModel.get_model(),
        #         max_iter=15,
        #         max_rpm=None,
        #         verbose=True,
        #         allow_delegation=True,
        #     )

        #     self.task = Task(
        #         description=("Your task is to answer the {question}"),
        #         expected_output="Answer the question",
        #         agent=self.crew_agent,
        #     )

        #     self.crew = Crew(
        #         agents=[self.crew_agent],
        #         tasks=[self.task],
        #         process=Process.sequential,
        #         verbose=True,
        #     )

        #     self.crew.kickoff({"question": message_with_history})

        #     task_output = self.task.output
        #     msg = {
        #         "role": "assistant",
        #         "text": task_output.raw,
        #         "type": "text",
        #     }
        #     save_new_messages_in_db([msg])
        #     send_message(msg)

        #     return task_output.raw, self.called_tools

    def process_tool_execution_results(
        self,
        thread_id,
        tool_execution_result,
        action_message,
        send_message,
        save_new_messages_in_db,
        last_run,
    ):
        if self.agent == "openai":
            return OpenAISubmitToolsOutputProccess(thread_id=thread_id).start(
                tool_execution_result,
                self.user_toolkits,
                action_message,
                self.vector_store,
                send_message,
                save_new_messages_in_db,
            )
        if self.agent == "langchain":
            function_name = last_run["function_tools"][-1]

            # Handle special tool execution result types
            if isinstance(tool_execution_result, dict):
                result_type = tool_execution_result.get("type")
                if result_type in ["screenshot", "currentPage"]:
                    result = self.toolkits.post_call(
                        function_name, tool_execution_result.get("data")
                    )
                else:
                    result = tool_execution_result
            else:
                result = tool_execution_result

            # Process result through agent and send response
            res = self.agent_executor.invoke({"input": result})
            msg = {
                "role": "assistant",
                "text": res["output"],
                "type": "text",
            }
            save_new_messages_in_db([msg])
            send_message(msg)

    def process_stop_run(self, thread_id):
        OpenAIStopRun(thread_id=thread_id).start()

    def update_tools(self, *args):
        self.called_tools.extend(args)
