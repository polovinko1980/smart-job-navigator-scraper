import logging
from typing import List

from models.request_models import UserCookie
from utils.browser_provider import BrowserProvider, BrowserOptions

logger = logging.getLogger(__name__)


def simulate_click_at_random_coordinates(browser):
    js_code = """
    function simulateClick(x, y) {
        var clickEvent = new MouseEvent('click', {
            'view': window,
            'bubbles': true,
            'cancelable': true,
            'clientX': x,
            'clientY': y
        });
        document.elementFromPoint(x, y).dispatchEvent(clickEvent);
    }
    simulateClick(100, 200);
    """
    browser.execute_script(js_code)


class AuthorizerBase:
    def __init__(self, browser_options: BrowserOptions):
        self.browser = self.initialize_browser(browser_options)

    @staticmethod
    def initialize_browser(browser_options: BrowserOptions):
        browser_provider = BrowserProvider(browser_options=browser_options)
        return browser_provider.browser

class LinkedInAuthorizer(AuthorizerBase):
    """
    Class to manage browser sessions on the LinkedIn app.
    LinkedIn blocks non-organic browser instances.
    """

    LINKEDIN_BASE_URL = "https://www.linkedin.com/"
    LINKEDIN_AUTHORIZED_USER_REDIRECT_URL = "https://www.linkedin.com/feed/"

    def start_incognito_session(self, target_url: str = LINKEDIN_BASE_URL):
        self.browser.visit(target_url)
        self.ensure_valid_url(target_url)
        return self.browser

    def start_authorized_session(self, cookies: List[UserCookie], target_url: str = LINKEDIN_AUTHORIZED_USER_REDIRECT_URL):
        self.validate_cookies(cookies)
        self.browser.visit(self.LINKEDIN_BASE_URL)
        self.add_cookies_to_browser(cookies)
        self.ensure_valid_url(target_url)
        return self.browser

    @staticmethod
    def validate_cookies(cookies: List[UserCookie]):
        if not cookies:
            raise RuntimeError("Unable to authorize user session without li_at_cookie and b_cookie")

    def add_cookies_to_browser(self, cookies: List[UserCookie]):
        existing_cookie_values = self.get_existing_cookie_values()
        if self.add_new_cookies(cookies, existing_cookie_values):
            self.refresh_browser()

    def get_existing_cookie_values(self):
        webdriver = self.browser.driver
        return {cookie.get("value") for cookie in webdriver.get_cookies()}

    def add_new_cookies(self, cookies: List[UserCookie], existing_cookie_values: set):
        new_cookies_added = False
        webdriver = self.browser.driver
        for cookie in cookies:
            if cookie.value not in existing_cookie_values:
                webdriver.add_cookie(cookie.dict())  # Convert from Pydantic
                new_cookies_added = True
        return new_cookies_added

    def refresh_browser(self):
        self.browser.driver.refresh()

    def ensure_valid_url(self, target_url: str):
        current_url = self.browser.url
        if not self.is_url_valid(current_url, target_url):
            raise RuntimeError(f"Hitting LinkedIn bot protection wall: {current_url}")
        logger.info(f"Created browser session, current url: {current_url}")

    def is_url_valid(self, current_url: str, target_url: str):
        page_html = self.browser.html
        return (
            "ERR_TOO_MANY_REDIRECTS" not in page_html and
            "HTTP ERROR 429" not in page_html and
            current_url in target_url
        )

    def dismiss_widget(self):
        simulate_click_at_random_coordinates(self.browser)

class OtherDashboardAuthorizer(AuthorizerBase):
    """
    Class to manage browser sessions on other dashboards.
    """

    def start_incognito_session(self):
        logger.info("Created browser session for arbitrary URL parsing")
        return self.browser
