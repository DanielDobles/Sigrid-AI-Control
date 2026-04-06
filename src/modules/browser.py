# Browser Agent - Web automation with Playwright

import asyncio
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from typing import Optional, Dict, List
from src.config.settings import BROWSER_HEADLESS

class BrowserAgent:
    """Automates web browser interactions using Playwright."""
    
    def __init__(self, headless: bool = None):
        self.headless = headless if headless is not None else BROWSER_HEADLESS
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._initialized = False
        
    async def initialize(self):
        """Initialize the browser."""
        if self._initialized:
            return
            
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=["--start-maximized"] if not self.headless else []
        )
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )
        self.page = await self.context.new_page()
        self._initialized = True
        
    async def close(self):
        """Close the browser and cleanup."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        self._initialized = False
        
    async def navigate(self, url: str, wait_until: str = "networkidle") -> dict:
        """Navigate to a URL."""
        try:
            if not self._initialized:
                await self.initialize()
                
            response = await self.page.goto(url, wait_until=wait_until)
            return {
                "status": "success",
                "action": "navigate",
                "url": url,
                "status_code": response.status if response else None,
                "title": await self.page.title()
            }
        except Exception as e:
            return {"status": "error", "action": "navigate", "error": str(e)}
    
    async def click(self, selector: str) -> dict:
        """Click an element on the page."""
        try:
            await self.page.click(selector)
            return {"status": "success", "action": "click", "selector": selector}
        except Exception as e:
            return {"status": "error", "action": "click", "error": str(e)}
    
    async def fill(self, selector: str, text: str) -> dict:
        """Fill a form field."""
        try:
            await self.page.fill(selector, text)
            return {"status": "success", "action": "fill", "selector": selector, "text": text}
        except Exception as e:
            return {"status": "error", "action": "fill", "error": str(e)}
    
    async def type_text(self, selector: str, text: str, delay: int = 50) -> dict:
        """Type text character by character into an element."""
        try:
            await self.page.type(selector, text, delay=delay)
            return {"status": "success", "action": "type", "selector": selector, "text": text}
        except Exception as e:
            return {"status": "error", "action": "type", "error": str(e)}
    
    async def press_key(self, key: str) -> dict:
        """Press a keyboard key."""
        try:
            await self.page.keyboard.press(key)
            return {"status": "success", "action": "press_key", "key": key}
        except Exception as e:
            return {"status": "error", "action": "press_key", "error": str(e)}
    
    async def get_text(self, selector: str) -> dict:
        """Get text content of an element."""
        try:
            text = await self.page.text_content(selector)
            return {"status": "success", "action": "get_text", "selector": selector, "text": text}
        except Exception as e:
            return {"status": "error", "action": "get_text", "error": str(e)}
    
    async def get_page_content(self) -> dict:
        """Get the full page content as text."""
        try:
            content = await self.page.inner_text("body")
            return {"status": "success", "action": "get_content", "content": content}
        except Exception as e:
            return {"status": "error", "action": "get_content", "error": str(e)}
    
    async def get_page_html(self) -> dict:
        """Get the full page HTML."""
        try:
            html = await self.page.content()
            return {"status": "success", "action": "get_html", "html": html}
        except Exception as e:
            return {"status": "error", "action": "get_html", "error": str(e)}
    
    async def screenshot(self, path: str, full_page: bool = False) -> dict:
        """Take a screenshot of the page."""
        try:
            await self.page.screenshot(path=path, full_page=full_page)
            return {"status": "success", "action": "screenshot", "path": path}
        except Exception as e:
            return {"status": "error", "action": "screenshot", "error": str(e)}
    
    async def wait_for_selector(self, selector: str, timeout: int = 30000) -> dict:
        """Wait for an element to appear on the page."""
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            return {"status": "success", "action": "wait_for_selector", "selector": selector}
        except Exception as e:
            return {"status": "error", "action": "wait_for_selector", "error": str(e)}
    
    async def evaluate(self, javascript: str) -> dict:
        """Execute JavaScript on the page."""
        try:
            result = await self.page.evaluate(javascript)
            return {"status": "success", "action": "evaluate", "result": result}
        except Exception as e:
            return {"status": "error", "action": "evaluate", "error": str(e)}
    
    async def get_all_links(self) -> dict:
        """Get all links on the current page."""
        try:
            links = await self.page.eval_on_selector_all("a[href]", "elements => elements.map(e => e.href)")
            return {"status": "success", "action": "get_links", "links": links, "count": len(links)}
        except Exception as e:
            return {"status": "error", "action": "get_links", "error": str(e)}
    
    async def execute_action(self, action_name: str, **kwargs) -> dict:
        """Execute a browser action by name."""
        action_map = {
            "navigate": self.navigate,
            "click": self.click,
            "fill": self.fill,
            "type_text": self.type_text,
            "press_key": self.press_key,
            "get_text": self.get_text,
            "get_page_content": self.get_page_content,
            "get_page_html": self.get_page_html,
            "screenshot": self.screenshot,
            "wait_for_selector": self.wait_for_selector,
            "evaluate": self.evaluate,
            "get_all_links": self.get_all_links,
        }
        
        if action_name in action_map:
            return await action_map[action_name](**kwargs)
        return {"status": "error", "error": f"Unknown action: {action_name}"}


# Sync wrapper for easier use in non-async contexts
class BrowserAgentSync:
    """Synchronous wrapper for BrowserAgent."""
    
    def __init__(self, headless: bool = None):
        self.headless = headless if headless is not None else BROWSER_HEADLESS
        self._agent = BrowserAgent(headless=self.headless)
        
    def initialize(self):
        asyncio.get_event_loop().run_until_complete(self._agent.initialize())
        
    def close(self):
        asyncio.get_event_loop().run_until_complete(self._agent.close())
        
    def navigate(self, url: str, **kwargs) -> dict:
        return asyncio.get_event_loop().run_until_complete(self._agent.navigate(url, **kwargs))
    
    def click(self, selector: str) -> dict:
        return asyncio.get_event_loop().run_until_complete(self._agent.click(selector))
    
    def fill(self, selector: str, text: str) -> dict:
        return asyncio.get_event_loop().run_until_complete(self._agent.fill(selector, text))
    
    def get_page_content(self) -> dict:
        return asyncio.get_event_loop().run_until_complete(self._agent.get_page_content())
    
    def screenshot(self, path: str, **kwargs) -> dict:
        return asyncio.get_event_loop().run_until_complete(self._agent.screenshot(path, **kwargs))
