import asyncio
import base64
from typing import List, Dict, Optional
from patchright.async_api import async_playwright, Page

# Optional: key mapping if your model uses "CUA" style keys
CUA_KEY_TO_PLAYWRIGHT_KEY = {
    "/": "Divide",
    "\\": "Backslash",
    "alt": "Alt",
    "arrowdown": "ArrowDown",
    "arrowleft": "ArrowLeft",
    "arrowright": "ArrowRight",
    "arrowup": "ArrowUp",
    "backspace": "Backspace",
    "capslock": "CapsLock",
    "cmd": "Meta",
    "ctrl": "Control",
    "delete": "Delete",
    "end": "End",
    "enter": "Enter",
    "esc": "Escape",
    "home": "Home",
    "insert": "Insert",
    "option": "Alt",
    "pagedown": "PageDown",
    "pageup": "PageUp",
    "shift": "Shift",
    "space": " ",
    "super": "Meta",
    "tab": "Tab",
    "win": "Meta",
}


class BrowserExecutor:
    def __init__(self):
        self.width = 1024
        self.height = 768
    
    def get_dimensions(self):
        return (self.width, self.height)

    def set_dimensions(self, width, height):
        self.width = width
        self.height = height

    async def initialize(
        self, 
        initial_url: str,
        use_real_browser: bool = False,
        user_data_dir: Optional[str] = None,
        chrome_path: Optional[str] = None,
    ):
        self.playwright = await async_playwright().start()
        if use_real_browser:
            self.context = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                executable_path=chrome_path,
                headless=False,
                args=[
                    "--disable-extensions",
                    "--disable-file-system",
                    "--start-maximized"
                ]
            )
        else:            
            width, height = self.get_dimensions()
            self.browser = await self.playwright.chromium.launch(
                headless=False,
                args=[
                    "--disable-extensions",
                    "--disable-file-system",
                ]
            )
            self.context = await self.browser.new_context(
                viewport={"width": width, "height": height},
                locale='en-US',
            )
        self.context.on("page", self._handle_new_page)

        page = await self.context.new_page()
        page.on("close", self._handle_page_close)
        
        viewport_size = page.viewport_size
        self.set_dimensions(viewport_size["width"], viewport_size["height"])

        if initial_url is None:
            initial_url = "https://google.com"
        await page.goto(initial_url)

    async def _handle_new_page(self, page: Page):
        print("New page created")
        self.page = page
        page.on("close", self._handle_page_close)

    async def _handle_page_close(self, page: Page):
        print("Page closed")
        if self.page == page:
            if self.context.pages:
                self.page = self.context.pages[-1]
            else:
                print("Warning: All pages have been closed.")
                self.page = None

    async def close(self):
        if not self.page.is_closed():
            await self.page.close()

        await self.context.close()

        if self.browser:
            await self.browser.close()
        
        await self.playwright.stop()

    def get_current_url(self) -> str:
        return self.page.url

    # --- Common "Computer" actions ---
    async def screenshot(self) -> str:
        """Capture only the viewport (not fullpage)."""
        png_bytes = await self.page.screenshot(full_page=False)
        return base64.b64encode(png_bytes).decode("utf-8")

    async def click(self, x: int, y: int, button: str = "left") -> None:
        match button:
            case "back":
                await self.back()
            case "forward":
                await self.forward()
            case "wheel":
                await self.page.mouse.wheel(x, y)
            case _:
                button_mapping = {"left": "left", "right": "right"}
                button_type = button_mapping.get(button, "left")
                await self.page.mouse.click(x, y, button=button_type)

    async def double_click(self, x: int, y: int) -> None:
        await self.page.mouse.dblclick(x, y)

    async def scroll(self, x: int, y: int, scroll_x: int, scroll_y: int) -> None:
        await self.page.mouse.move(x, y)
        await self.page.evaluate(f"window.scrollBy({scroll_x}, {scroll_y})")

    async def type(self, text: str) -> None:
        await self.page.keyboard.type(text)

    async def wait(self, ms: int = 1000) -> None:
        await asyncio.sleep(ms / 1000)

    async def move(self, x: int, y: int) -> None:
        await self.page.mouse.move(x, y)

    async def keypress(self, keys: List[str]) -> None:
        mapped_keys = [CUA_KEY_TO_PLAYWRIGHT_KEY.get(key.lower(), key) for key in keys]
        for key in mapped_keys:
            await self.page.keyboard.down(key)
        for key in reversed(mapped_keys):
            await self.page.keyboard.up(key)

    async def drag(self, path: List[Dict[str, int]]) -> None:
        if not path:
            return
        await self.page.mouse.move(path[0]["x"], path[0]["y"])
        await self.page.mouse.down()
        for point in path[1:]:
            await self.page.mouse.move(point["x"], point["y"])
        await self.page.mouse.up()

    # --- Extra browser-oriented actions ---
    async def goto(self, url: str) -> None:
        try:
            return await self.page.goto(url)
        except Exception as e:
            print(f"Error navigating to {url}: {e}")

    async def back(self) -> None:
        return await self.page.go_back()

    async def forward(self) -> None:
        return await self.page.go_forward()

