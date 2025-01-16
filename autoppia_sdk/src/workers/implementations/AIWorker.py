from crewai import Agent, Crew, Process, Task
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from autoppia_ia.src.ai_bootstrap import AIBootstrap
from autoppia_ia.src.assistants.domain.classes import BaseAssistant
from autoppia_ia.src.processes.application.openai.new_message import (
    OpenAINewMessageProccess,
)
from autoppia_ia.src.processes.application.openai.stop_run import OpenAIStopRun
from autoppia_ia.src.processes.application.openai.submit_tools import (
    OpenAISubmitToolsOutputProccess,
)
from autoppia_ia.src.threads.application.openai.openai_assistant import OpenAIAssistant
from autoppia_ia.src.threads.application.openai.thread_manager import (
    OpenAIThreadManager,
)
from autoppia_ia.src.tools.application.all import all_toolkits
from autoppia_ia.src.tools.domain.classes import ToolkitList
from autoppia_ia.src.workers.domain.AIWorkerAdapter import AIWorkerAdapter
from autoppia_ia.src.workers.domain.classes import UserToolkit


class AIWorker:
    def __init__(self, worker_id=None, worker_dto=None):
        self.worker_id = worker_id
        self.ai_worker_adapter = AIWorkerAdapter(worker_id, worker_dto)
        (
            self.user_llm,
            self.vector_store,
            self.user_toolkits,
            self.agent,
        ) = self.ai_worker_adapter.from_backend()
        self.toolkits = None
        self.thread_manager = None
        self.assistant_id = "asst_w0AnuWWxOUYanQNOiQGLJlZR"

    def thread_setup(
        self,
        send_message=None,
        action_message=None,
        chat_session_id=None,
        thread_id=None,
        test_mode=False,
    ):
        # Add Browser toolkit if not already present
        if (
            not any(toolkit.toolkit_name == "Browser" for toolkit in self.user_toolkits)
            and action_message
        ):
            browser_context = {"action_message": action_message}
            browser_instruction = """
                There is execute_browser_action tool, so you should use this tool for browser actions such as clicking, navigate, modify style, fill input etc.
                Before executing browser action you should call get_current_page tool so that you must know about current page html.
            """
            browser_toolkit = UserToolkit(
                toolkit_name="Browser",
                context=browser_context,
                instruction=browser_instruction,
            )
            self.user_toolkits.append(browser_toolkit)

        # Configure Retrieval toolkit if vector_store is not a string
        if not isinstance(self.vector_store, str) and chat_session_id:
            retrieval_context = {
                "vector_store": self.vector_store,
                "filter": {
                    "$or": [
                        {"type": "standard"},
                        {"worker": self.worker_id},
                        {"chat_session": chat_session_id},
                    ]
                },
            }
            retrieval_toolkit = UserToolkit(
                toolkit_name="Retrieval", context=retrieval_context
            )
            self.user_toolkits.append(retrieval_toolkit)

        # Update toolkits list
        user_toolkit_names = [item.toolkit_name for item in self.user_toolkits]
        toolkits = [
            toolkit for toolkit in all_toolkits if toolkit.name in user_toolkit_names
        ]
        self.toolkits = ToolkitList(toolkits, self.user_toolkits)

        # Initialize AI Bootstrap and system prompt
        bootstrap = AIBootstrap()
        self.system_prompt = BaseAssistant.get_instructions_template("toolkit_executor")

        # Select appropriate LLM model
        llm_model_map = {
            "GPT-4": bootstrap.container.gpt4,
            "GPT-4o": bootstrap.container.gpt4o,
        }
        self.llmModel = llm_model_map.get(
            self.user_llm, bootstrap.container.default_model
        )()

        # Construct instructions
        self.instructions = self.system_prompt.get_prompt() + "\n".join(
            self.toolkits.to_instructions()
        )

        if self.agent == "openai":
            # Create or retrieve OpenAIAssistant
            openai_assistant = OpenAIAssistant.get_or_create(
                self.assistant_id,
                "Task Executor",
                self.instructions,
                self.llmModel,
                self.toolkits,
                None,
                True,
                True,
                test_mode,
            )

            # Update assistant with vector_store if it's a string
            if isinstance(self.vector_store, str):
                openai_assistant.update_assistant(self.assistant_id, self.vector_store)

            # Manage thread manager based on thread_id
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
            print("I am here step 1")
            return OpenAINewMessageProccess(thread_id).start(
                message,
                self.thread_manager,
                self.assistant_id,
                self.user_toolkits,
                send_message,
                save_new_messages_in_db,
                save_thread_id_in_db,
                last_uploaded_file,
            )
        elif self.agent == "langchain":
            langchain_tools = self.toolkits.to_langchain_tools(
                send_message, save_new_function_tool_in_db
            )

            # Create the LLM provider
            llm = ChatOpenAI(model="gpt-4o")
            # llm = ChatGroq(model="groq/mixtral-8x7b-32768")

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
            self.langchain_agent = create_tool_calling_agent(
                llm, langchain_tools, prompt
            )

            self.agent_executor = AgentExecutor(
                agent=self.langchain_agent, tools=langchain_tools, verbose=True
            )

            result = self.agent_executor.invoke({"input": message_with_history})
            msg = {
                "role": "assistant",
                "text": result["output"],
                "type": "text",
            }
            save_new_messages_in_db([msg])
            send_message(msg)

            return None, None

        elif self.agent == "crewai":
            langchain_tools = self.toolkits.to_langchain_tools(
                send_message, save_new_function_tool_in_db
            )

            # Create the LLM provider
            # llm = ChatOpenAI(model="gpt-4o")
            # llm = ChatGroq(model="groq/mixtral-8x7b-32768")

            self.crew_agent = Agent(
                role="Assistant",
                goal="Answer the question with calling suitable tools if you need.",
                backstory=self.instructions,
                tools=langchain_tools,
                llm=self.llmModel.get_model(),
                max_iter=15,
                max_rpm=None,
                verbose=True,
                allow_delegation=True,
            )

            self.task = Task(
                description=("Your task is to answer the {question}"),
                expected_output="Answer the question",
                agent=self.crew_agent,
            )

            self.crew = Crew(
                agents=[self.crew_agent],
                tasks=[self.task],
                process=Process.sequential,
                verbose=True,
            )

            self.crew.kickoff({"question": message_with_history})

            task_output = self.task.output
            msg = {
                "role": "assistant",
                "text": task_output.raw,
                "type": "text",
            }
            save_new_messages_in_db([msg])
            send_message(msg)

            return None, None

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

            if (
                isinstance(tool_execution_result, dict)
                and tool_execution_result.get("type") == "screenshot"
            ):
                result = self.toolkits.post_call(
                    function_name, tool_execution_result.get("data")
                )

            elif (
                isinstance(tool_execution_result, dict)
                and tool_execution_result.get("type") == "currentPage"
            ):
                result = self.toolkits.post_call(
                    function_name, tool_execution_result.get("data")
                )
            else:
                result = tool_execution_result

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
