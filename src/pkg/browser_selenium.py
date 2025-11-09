"""
Browser Automation Module using Selenium
"""

import asyncio
import logging
from typing import Optional, List, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import base64
import json

logger = logging.getLogger(__name__)


class BrowserAutomation:
    """Selenium-based browser automation wrapper"""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self._driver: Optional[webdriver.Chrome] = None

    async def init(self) -> bool:
        """Initialize Chrome WebDriver"""
        try:
            options = webdriver.ChromeOptions()
            
            if self.headless:
                options.add_argument("--headless")
            
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36")
            
            self._driver = webdriver.Chrome(options=options)
            logger.info("✅ Chrome WebDriver initialized")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize WebDriver: {e}")
            return False

    async def navigate(self, url: str, wait_time: int = 10) -> bool:
        """Navigate to URL and wait for page load"""
        if not self._driver:
            raise RuntimeError("WebDriver not initialized")
        
        try:
            self._driver.get(url)
            WebDriverWait(self._driver, wait_time).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            logger.info(f"✅ Navigated to {url}")
            return True
        except TimeoutException:
            logger.error(f"❌ Page load timeout: {url}")
            return False
        except Exception as e:
            logger.error(f"❌ Navigation failed: {e}")
            return False

    async def wait_for_element(self, selector: str, by: By = By.CSS_SELECTOR, timeout: int = 10) -> bool:
        """Wait for element to be present"""
        if not self._driver:
            raise RuntimeError("WebDriver not initialized")
        
        try:
            WebDriverWait(self._driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            logger.info(f"✅ Element found: {selector}")
            return True
        except TimeoutException:
            logger.error(f"❌ Element timeout: {selector}")
            return False

    async def click_element(self, selector: str, by: By = By.CSS_SELECTOR) -> bool:
        """Click on element"""
        if not self._driver:
            raise RuntimeError("WebDriver not initialized")
        
        try:
            element = self._driver.find_element(by, selector)
            self._driver.execute_script("arguments[0].scrollIntoView(true);", element)
            element.click()
            logger.info(f"✅ Clicked: {selector}")
            return True
        except NoSuchElementException:
            logger.error(f"❌ Element not found: {selector}")
            return False
        except Exception as e:
            logger.error(f"❌ Click failed: {e}")
            return False

    async def fill_form(self, fields: Dict[str, str]) -> bool:
        """Fill form fields"""
        if not self._driver:
            raise RuntimeError("WebDriver not initialized")
        
        try:
            for selector, value in fields.items():
                element = self._driver.find_element(By.CSS_SELECTOR, selector)
                element.clear()
                element.send_keys(value)
            
            logger.info(f"✅ Filled {len(fields)} form fields")
            return True
        except Exception as e:
            logger.error(f"❌ Form fill failed: {e}")
            return False

    async def get_screenshot(self, filename: Optional[str] = None) -> Optional[str]:
        """Take screenshot and return base64 or save to file"""
        if not self._driver:
            raise RuntimeError("WebDriver not initialized")
        
        try:
            screenshot_data = self._driver.get_screenshot_as_png()
            
            if filename:
                with open(filename, 'wb') as f:
                    f.write(screenshot_data)
                logger.info(f"✅ Screenshot saved: {filename}")
                return filename
            else:
                b64 = base64.b64encode(screenshot_data).decode('utf-8')
                logger.info("✅ Screenshot captured (base64)")
                return b64
        except Exception as e:
            logger.error(f"❌ Screenshot failed: {e}")
            return None

    async def get_page_source(self) -> str:
        """Get full page HTML"""
        if not self._driver:
            raise RuntimeError("WebDriver not initialized")
        
        try:
            source = self._driver.page_source
            logger.info(f"✅ Page source retrieved ({len(source)} bytes)")
            return source
        except Exception as e:
            logger.error(f"❌ Failed to get page source: {e}")
            return ""

    async def execute_script(self, script: str) -> any:
        """Execute JavaScript"""
        if not self._driver:
            raise RuntimeError("WebDriver not initialized")
        
        try:
            result = self._driver.execute_script(script)
            logger.info(f"✅ Script executed")
            return result
        except Exception as e:
            logger.error(f"❌ Script execution failed: {e}")
            return None

    async def get_cookies(self) -> List[Dict]:
        """Get all cookies"""
        if not self._driver:
            raise RuntimeError("WebDriver not initialized")
        
        try:
            cookies = self._driver.get_cookies()
            logger.info(f"✅ Retrieved {len(cookies)} cookies")
            return cookies
        except Exception as e:
            logger.error(f"❌ Failed to get cookies: {e}")
            return []

    async def set_cookie(self, name: str, value: str, domain: str = None) -> bool:
        """Set cookie"""
        if not self._driver:
            raise RuntimeError("WebDriver not initialized")
        
        try:
            cookie_dict = {"name": name, "value": value}
            if domain:
                cookie_dict["domain"] = domain
            
            self._driver.add_cookie(cookie_dict)
            logger.info(f"✅ Cookie set: {name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to set cookie: {e}")
            return False

    async def close(self):
        """Close browser"""
        if self._driver:
            self._driver.quit()
            self._driver = None
            logger.info("✅ Browser closed")

    def is_initialized(self) -> bool:
        """Check if driver is initialized"""
        return self._driver is not None


# Global instance
_browser_instance: Optional[BrowserAutomation] = None


async def get_browser() -> BrowserAutomation:
    """Get or create browser instance"""
    global _browser_instance
    if _browser_instance is None:
        raise RuntimeError("Browser instance not initialized")
    return _browser_instance


async def init_browser(headless: bool = True) -> BrowserAutomation:
    """Initialize browser instance"""
    global _browser_instance
    _browser_instance = BrowserAutomation(headless=headless)
    if not await _browser_instance.init():
        raise RuntimeError("Failed to initialize browser")
    return _browser_instance
