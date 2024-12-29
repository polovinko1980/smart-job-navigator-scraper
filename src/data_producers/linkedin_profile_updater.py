import logging
import sys
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


class LinkedInProfileUpdater:
    LINKEDIN_FEED_URL = "https://www.linkedin.com/feed/"

    # Main Page locators
    VIEW_PROFILE_PARTIAL_LINK = "View Profile"
    PROFILE_LINK_CSS = (
        '[class="global-nav__primary-link '
        'global-nav__primary-link-me-menu-trigger '
        'artdeco-dropdown__trigger '
        'artdeco-dropdown__trigger--placement-bottom ember-view"]'
    )
    CLOSE_SIGN_IN_MODAL_CSS = '[aria-label="Dismiss"]'
    CLOSE_SIGN_IN_MODAL_XPATH = "(//svg)[1]"

    # User profile locators
    HEADLINE_TEXT_INPUT_CSS = '[class="text-body-medium break-words"]'
    EDIT_HEADLINE_CSS = '[aria-label="Edit intro"]'
    EDITABLE_HEADLINE_CSS = (
        '[class="fb-gai-text__textarea  '
        'artdeco-text-input--input '
        'artdeco-text-input__textarea '
        'artdeco-text-input__textarea--align-top"]'
    )
    SAVE_PROFILE_CSS = '[data-view-name="profile-form-save"]'
    CLOSE_SAVE_PROFILE_CSS = '[data-test-icon="close-medium"]'
    UPDATED_PROFILE_CSS = '[class="text-body-medium break-words"]'

    def __init__(self, browser, wait_time: int = 5):
        self.browser = browser
        self.wait_time = wait_time

    def update_headline(self, new_headline) -> None:
        self._navigate_to_profile()
        current_headline = self._get_current_headline()
        self._edit_headline(new_headline)
        self._save_profile()
        self._close_save_profile()
        updated_headline = self._get_updated_headline()
        logger.info(f"Updated headline from: {current_headline} to: {updated_headline}")


    def _navigate_to_profile(self) -> None:
        self.browser.visit(self.LINKEDIN_FEED_URL)
        self.browser.find_by_css(self.PROFILE_LINK_CSS).click()
        time.sleep(self.wait_time)
        self.browser.links.find_by_partial_text(self.VIEW_PROFILE_PARTIAL_LINK).click()

    def _get_current_headline(self) -> str:
        return self.browser.find_by_css(self.HEADLINE_TEXT_INPUT_CSS, wait_time=self.wait_time).first.text

    def _edit_headline(self, new_headline) -> None:
        self.browser.find_by_css(self.EDIT_HEADLINE_CSS).click()
        self.browser.find_by_css(self.EDITABLE_HEADLINE_CSS, wait_time=self.wait_time).fill(new_headline)

    def _save_profile(self) -> None:
        self.browser.find_by_css(self.SAVE_PROFILE_CSS).click()
        time.sleep(self.wait_time)

    def _close_save_profile(self) -> None:
        self.browser.find_by_css(self.CLOSE_SAVE_PROFILE_CSS).click()

    def _get_updated_headline(self) -> str:
        return self.browser.find_by_css(self.UPDATED_PROFILE_CSS, wait_time=self.wait_time).first.text
