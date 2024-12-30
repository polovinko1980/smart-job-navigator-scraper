import logging
import re
import sys
import time
import traceback
from typing import List

from splinter.exceptions import ElementDoesNotExist
from utils.browser_authorizer import simulate_click_at_random_coordinates

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

class LinkedInJobSearchScraper:
    """
    Wrapper for LinkedIn Job Search page using Splinter API.
    """

    LINKEDIN_JOB_URL_PREFIX = 'https://www.linkedin.com/jobs/view'

    JOB_ID_KEY = 'data-occludable-job-id'
    AUTHORIZED_JOB_LOCATOR = '[id="results-list__title"]'
    INCOGNITO_JOB_LOCATOR = '[class="results-context-header__query-search"]'
    JOBS_XPATH_PREFIX = "(//main/div/div/div/div/ul/li)"
    INCOGNITO_JOBS_XPATH_PREFIX = "(//ul[@class='jobs-search__results-list']/li)"
    JOB_URL_CSS_SELECTOR = '[data-tracking-control-name="public_jobs_jserp-result_search-card"]'
    USER_PROCESSING_LIMIT = 100

    def __init__(self, browser, search_results_url: str, wait_time: int = 5):
        self.browser = browser
        self.entry_point = search_results_url
        self.wait_time = wait_time
        self.job_urls = []

    def fetch_new_job_postings(self, is_authorized_user=True) -> List[str]:
        self._navigate_to_job_search_page(is_authorized_user)
        self._scroll_and_collect_job_urls(is_authorized_user)
        logger.info(f"Found {len(self.job_urls)} job urls")
        return self.job_urls

    def _navigate_to_job_search_page(self, is_authorized_user) -> None:
        locator = self.AUTHORIZED_JOB_LOCATOR if is_authorized_user else self.INCOGNITO_JOB_LOCATOR
        self.browser.visit(self.entry_point)
        time.sleep(self.wait_time)
        search_result_element = self.browser.find_by_css(locator, wait_time=self.wait_time)
        logger.info(f"Parsing LinkedIn search result page for {search_result_element.text}")

    def _scroll_and_collect_job_urls(self, is_authorized_user) -> None:
        if is_authorized_user:
            self._scroll_as_authorized_user()
        else:
            self._dismiss_signin_widget()
            self._scroll_as_incognito_user()

    def _scroll_as_authorized_user(self):
        index = 1
        page = 1

        while len(self.job_urls) < self.USER_PROCESSING_LIMIT:
            job_card_xpath = f"{self.JOBS_XPATH_PREFIX}[{index}]"
            try:
                job_card = self.browser.find_by_xpath(job_card_xpath).first
                job_card.click()
                self._add_normalized_job_url(job_card[self.JOB_ID_KEY])
                index += 1
            except ElementDoesNotExist:
                if self._last_page(page):
                    logger.warning(f"No more pages available. Last processed job url index: {index - 1} on page {page}.")
                    return
                index = 1
                page += 1
            except Exception as e:
                logger.error(f"Unexpected exception: {e}. {traceback.format_exc()}")
                return

    def _last_page(self, current_page) -> bool:
        next_page = current_page + 1
        css_locator = f'[aria-label="Page {next_page}"]'
        try:
            self.browser.find_by_css(css_locator).first.click()
            logger.info(f"Navigating to the next page {next_page}")
            time.sleep(self.wait_time)
            return False
        except ElementDoesNotExist:
            return True

    def _scroll_as_incognito_user(self) -> None:
        index = 1
        while self.browser.is_element_present_by_xpath(f"{self.INCOGNITO_JOBS_XPATH_PREFIX}[{index}]"):
            element = self.browser.find_by_xpath(f"{self.INCOGNITO_JOBS_XPATH_PREFIX}[{index}]").first
            job_href = element.find_by_css(self.JOB_URL_CSS_SELECTOR, wait_time=self.wait_time).first['href']
            self._add_normalized_job_url(self._extract_job_id_from_url(job_href))
            index += 1
        logger.info(f"Search as unauthorized user returned {len(self.job_urls)} job postings for processing")

    def _dismiss_signin_widget(self) -> None:
        simulate_click_at_random_coordinates(self.browser)

    @staticmethod
    def _extract_job_id_from_url(job_url: str) -> str:
        pattern = r'(?<=-)(\d+)(?=\?)'
        match = re.search(pattern, job_url)
        return match.group(0) if match else None

    def _add_normalized_job_url(self, job_id) -> None:
        if job_id:
            self.job_urls.append(f"{self.LINKEDIN_JOB_URL_PREFIX}/{job_id}/")
