import asyncio
from typing import Optional

from autoppia.automata.client import AutomataClient
from autoppia.automata.utils import BrowserExecutor

class AutomataAgent:
    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
    ) -> None:
        self.client = AutomataClient(api_key=api_key, base_url=base_url)

    async def run_locally(
        self,
        task: str,
        initial_url: Optional[str] = None,
        user_data_dir: Optional[str] = None,
        chrome_path: Optional[str] = None,
        max_steps: int = 50
    ) -> str:
        self.browser_executor = BrowserExecutor()
        await self.browser_executor.initialize(
            initial_url=initial_url,
            use_real_browser=True,
            user_data_dir=user_data_dir,
            chrome_path=chrome_path
        )

        width, height = self.browser_executor.get_dimensions()
        response = await self.client.start_cua(
            task=task,
            provider="openai",
            display_width=width,
            display_height=height
        )
        agent_id = response["agent_id"]

        for _ in range(max_steps):
            computer_calls = [item for item in response["output"] if item["type"] == "computer_call"]
            if not computer_calls:
                messages = [item for item in response["output"] if item["type"] == "message"]
                return messages[0]["content"][0]["text"]

            action = computer_calls[0]["action"]
            await self._handle_action(action)
            await asyncio.sleep(1)

            screenshot = await self.browser_executor.screenshot()
            current_url = self.browser_executor.get_current_url()

            response = await self.client.forward_cua(
                agent_id=agent_id,
                screenshot=screenshot,
                current_url=current_url
            )
        else:
            return f"Can't find result after {max_steps} steps"

    async def close(self):
        await self.browser_executor.close()

    async def _handle_action(self, action: dict):
        action_type = action["type"]
        action_args = {k: v for k, v in action.items() if k != "type"}

        method = getattr(self.browser_executor, action_type, None)
        if method:
            await method(**action_args)





