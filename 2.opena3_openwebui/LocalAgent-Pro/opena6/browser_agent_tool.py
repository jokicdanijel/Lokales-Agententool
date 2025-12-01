"""
title: Browser Agent - Local Web Automation
author: PORTIER 3.0 System
funding_url: https://github.com/open-webui
version: 1.0.0
license: MIT
"""

import json
import requests
from typing import Callable, Any
from pydantic import BaseModel, Field


class EventEmitter:
    def __init__(self, event_emitter: Callable[[dict], Any] = None):
        self.event_emitter = event_emitter

    async def emit(self, description="Unknown State", status="in_progress", done=False):
        if self.event_emitter:
            await self.event_emitter(
                {
                    "type": "status",
                    "data": {
                        "status": status,
                        "description": description,
                        "done": done,
                    },
                }
            )


class Tools:
    class Valves(BaseModel):
        BROWSER_AGENT_URL: str = Field(
            default="http://localhost:12350",
            description="Browser Agent Server URL",
        )
        TOOL_SERVER_URL: str = Field(
            default="http://localhost:8765",
            description="Tool Server URL",
        )
        BEARER_TOKEN: str = Field(
            default="sk_opena6_browser_v3_production",
            description="Bearer token for authentication",
        )
        TIMEOUT: int = Field(
            default=30,
            description="Request timeout in seconds",
        )

    def __init__(self):
        self.valves = self.Valves()

    async def execute_browser_action(
        self,
        action: str,
        url: str,
        selector: str = "",
        text: str = "",
        wait_ms: int = 500,
        return_format: str = "text",
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Execute a browser automation action via the local Browser Agent.

        :param action: Browser action (open, click, type, extract_text, extract_html, query_selector, screenshot, scroll, wait_for)
        :param url: Target URL
        :param selector: CSS or XPath selector
        :param text: Text to input (for 'type' action)
        :param wait_ms: Wait time in milliseconds
        :param return_format: Return format (text, html, json, raw)
        :param __event_emitter__: Event emitter for status updates
        :return: Action result as JSON string
        """
        emitter = EventEmitter(__event_emitter__)

        # Validate action
        valid_actions = [
            "open",
            "click",
            "type",
            "extract_text",
            "extract_html",
            "query_selector",
            "screenshot",
            "scroll",
            "wait_for",
        ]
        if action not in valid_actions:
            error_msg = f"Invalid action: {action}. Must be one of: {', '.join(valid_actions)}"
            await emitter.emit(
                description=error_msg,
                status="error",
                done=True,
            )
            return json.dumps({"status": "error", "message": error_msg})

        await emitter.emit(f"Executing browser action: {action}")

        try:
            # Prepare request
            payload = {
                "action": action,
                "url": url,
                "wait_ms": wait_ms,
                "return_format": return_format,
            }

            if selector:
                payload["selector"] = selector
            if text:
                payload["text"] = text

            headers = {
                "Authorization": f"Bearer {self.valves.BEARER_TOKEN}",
                "Content-Type": "application/json",
            }

            # Send to Browser Agent
            await emitter.emit(f"Sending request to Browser Agent: {self.valves.BROWSER_AGENT_URL}")

            response = requests.post(
                f"{self.valves.BROWSER_AGENT_URL}/execute",
                json=payload,
                headers=headers,
                timeout=self.valves.TIMEOUT,
            )

            if response.status_code == 200:
                result = response.json()
                await emitter.emit(
                    description=f"Browser action '{action}' completed successfully",
                    status="complete",
                    done=True,
                )
                return json.dumps(result, ensure_ascii=False)
            else:
                error_msg = f"Browser Agent error: {response.status_code}"
                await emitter.emit(
                    description=error_msg,
                    status="error",
                    done=True,
                )
                return json.dumps({"status": "error", "message": error_msg, "details": response.text})

        except requests.exceptions.Timeout:
            error_msg = f"Request timeout (>{self.valves.TIMEOUT}s)"
            await emitter.emit(
                description=error_msg,
                status="error",
                done=True,
            )
            return json.dumps({"status": "error", "message": error_msg})

        except requests.exceptions.ConnectionError:
            error_msg = f"Cannot connect to Browser Agent at {self.valves.BROWSER_AGENT_URL}"
            await emitter.emit(
                description=error_msg,
                status="error",
                done=True,
            )
            return json.dumps({"status": "error", "message": error_msg})

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            await emitter.emit(
                description=error_msg,
                status="error",
                done=True,
            )
            return json.dumps({"status": "error", "message": error_msg})

    async def open_website(
        self,
        url: str,
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Open a website in the browser.

        :param url: Website URL
        :param __event_emitter__: Event emitter for status updates
        :return: Result as JSON string
        """
        return await self.execute_browser_action(
            action="open",
            url=url,
            __event_emitter__=__event_emitter__,
        )

    async def click_element(
        self,
        url: str,
        selector: str,
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Click an element on the webpage.

        :param url: Website URL
        :param selector: CSS or XPath selector for the element
        :param __event_emitter__: Event emitter for status updates
        :return: Result as JSON string
        """
        return await self.execute_browser_action(
            action="click",
            url=url,
            selector=selector,
            __event_emitter__=__event_emitter__,
        )

    async def type_text(
        self,
        url: str,
        selector: str,
        text: str,
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Type text into a form field.

        :param url: Website URL
        :param selector: CSS or XPath selector for the input field
        :param text: Text to type
        :param __event_emitter__: Event emitter for status updates
        :return: Result as JSON string
        """
        return await self.execute_browser_action(
            action="type",
            url=url,
            selector=selector,
            text=text,
            __event_emitter__=__event_emitter__,
        )

    async def extract_text(
        self,
        url: str,
        selector: str,
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Extract text content from a webpage element.

        :param url: Website URL
        :param selector: CSS or XPath selector
        :param __event_emitter__: Event emitter for status updates
        :return: Extracted text as JSON string
        """
        return await self.execute_browser_action(
            action="extract_text",
            url=url,
            selector=selector,
            return_format="text",
            __event_emitter__=__event_emitter__,
        )

    async def extract_html(
        self,
        url: str,
        selector: str,
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Extract HTML content from a webpage element.

        :param url: Website URL
        :param selector: CSS or XPath selector
        :param __event_emitter__: Event emitter for status updates
        :return: Extracted HTML as JSON string
        """
        return await self.execute_browser_action(
            action="extract_html",
            url=url,
            selector=selector,
            return_format="html",
            __event_emitter__=__event_emitter__,
        )

    async def query_dom(
        self,
        url: str,
        selector: str,
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Analyze DOM structure at a selector.

        :param url: Website URL
        :param selector: CSS or XPath selector
        :param __event_emitter__: Event emitter for status updates
        :return: DOM analysis as JSON string
        """
        return await self.execute_browser_action(
            action="query_selector",
            url=url,
            selector=selector,
            return_format="json",
            __event_emitter__=__event_emitter__,
        )

    async def take_screenshot(
        self,
        url: str,
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Take a screenshot of the webpage.

        :param url: Website URL
        :param __event_emitter__: Event emitter for status updates
        :return: Screenshot path as JSON string
        """
        return await self.execute_browser_action(
            action="screenshot",
            url=url,
            __event_emitter__=__event_emitter__,
        )

    async def scroll_page(
        self,
        url: str,
        selector: str = "",
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Scroll the webpage.

        :param url: Website URL
        :param selector: Optional selector to scroll to
        :param __event_emitter__: Event emitter for status updates
        :return: Result as JSON string
        """
        return await self.execute_browser_action(
            action="scroll",
            url=url,
            selector=selector,
            __event_emitter__=__event_emitter__,
        )

    async def wait_for_element(
        self,
        url: str,
        selector: str,
        wait_ms: int = 5000,
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Wait for an element to appear on the page.

        :param url: Website URL
        :param selector: CSS or XPath selector for the element
        :param wait_ms: Maximum wait time in milliseconds
        :param __event_emitter__: Event emitter for status updates
        :return: Result as JSON string
        """
        return await self.execute_browser_action(
            action="wait_for",
            url=url,
            selector=selector,
            wait_ms=wait_ms,
            __event_emitter__=__event_emitter__,
        )
