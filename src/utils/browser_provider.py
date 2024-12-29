from enum import Enum
from pydantic import BaseModel
from selenium.webdriver import ChromeOptions
from splinter import Browser


class SupportedDriverEnum(str, Enum):
    CHROME_DRIVER = "chrome"


class BrowserOptions(BaseModel):
    driverName: SupportedDriverEnum
    userAgent: str
    headlessMode: bool


class BrowserProvider:

    def __init__(self, browser_options: BrowserOptions):
        self._browser_instance = None
        self._browser_options = browser_options

    @property
    def browser(self):
        if self._browser_instance is None:
            self._browser_instance = self._create_browser_instance()
        return self._browser_instance

    def _create_browser_instance(self):
        chrome_options = self._setup_chrome_options()
        return Browser(
            self._browser_options.driverName,
            headless=self._browser_options.headlessMode,
            options=chrome_options,
        )


    def _setup_chrome_options(self):
        options = ChromeOptions()
        self._apply_basic_chrome_options(options)
        self._set_user_agent(options)
        return options

    @staticmethod
    def _apply_basic_chrome_options(options):
        basic_options = [
            "--enable-experimental-cookie-features",
            "--incognito",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--window-size=1920x1080",
            "--disable-gpu",
            "--disable-extensions",
            "--disable-renderer-backgrounding",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-client-side-phishing-detection",
            "--disable-crash-reporter",
            "--disable-oopr-debug-crash-dump",
            "--no-crash-upload",
            "--disable-low-res-tiling",
            "--log-level=3",
            "--silent",
            "--start-maximized"
        ]
        for option in basic_options:
            options.add_argument(option)

    def _set_user_agent(self, options):
        options.add_argument(self._browser_options.userAgent)
