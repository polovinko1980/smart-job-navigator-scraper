import logging
import re
import sys
import time
from typing import List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

def simulate_click_at_random_coordinates(browser)->None:
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

class LinkedInJobSearchScraper:
    """
    Wrapper for LinkedIn Job Search page using Splinter API.
    """

    LINKEDIN_JOB_URL_PREFIX = 'https://www.linkedin.com/jobs/view'

    AUTHORIZED_JOB_LOCATOR = '[id="results-list__title"]'
    AUTHORIZED_JOB_CSS_SELECTOR = 'data-job-id'

    INCOGNITO_JOB_LOCATOR = '[class="results-context-header__query-search"]'
    INCOGNITO_JOBS_XPATH_PREFIX = "(//ul[@class='jobs-search__results-list']/li)"
    INCOGNITO_JOB_URL_CSS_SELECTOR = '[data-tracking-control-name="public_jobs_jserp-result_search-card"]'

    USER_PROCESSING_LIMIT = 100

    def __init__(self, browser, search_results_url: str, wait_time: int = 5):
        self.browser = browser
        self.entry_point = search_results_url
        self.wait_time = wait_time
        self.job_urls = []

    def fetch_new_job_postings(self, is_authorized_user=True) -> List[str]:
        self._navigate_to_starting_page(is_authorized_user)
        self._scroll_and_collect_job_urls(is_authorized_user)
        logger.info(f"Scraped {len(self.job_urls)} job urls")
        return self.job_urls

    def _navigate_to_starting_page(self, is_authorized_user) -> None:
        locator = self.AUTHORIZED_JOB_LOCATOR if is_authorized_user else self.INCOGNITO_JOB_LOCATOR
        self.browser.visit(self.entry_point)
        time.sleep(self.wait_time)
        search_result_element = self.browser.find_by_css(locator, wait_time=self.wait_time)
        logger.info(f"Scraping LinkedIn search result page for {search_result_element.text}")

    def _scroll_and_collect_job_urls(self, is_authorized_user) -> None:
        if not is_authorized_user:
            self._dismiss_signin_widget()
        self._scrape_search_pages(is_authorized_user)

    def _scrape_search_pages(self, is_authorized_user) -> None:
        i = 0
        while len(self.job_urls) < self.USER_PROCESSING_LIMIT:
            self.browser.visit(f"{self.entry_point}&start={i}")
            logger.info(f"Scraping search page {i //7 + 1}")
            time.sleep(self.wait_time)
            if is_authorized_user:
                new_urls = self._scroll_as_authorized_user()
            else:
                new_urls = self._scroll_as_incognito_user()
            if not new_urls:
                break
            i += 7

    def _scroll_as_authorized_user(self) -> bool:
        new_urls =  [
            self._add_normalized_job_url(e[self.AUTHORIZED_JOB_CSS_SELECTOR])
            for e in
            self.browser.find_by_xpath(f"//div[@{self.AUTHORIZED_JOB_CSS_SELECTOR}]")
            if e[self.AUTHORIZED_JOB_CSS_SELECTOR] != "search"
        ]
        return len(new_urls) > 0

    def _scroll_as_incognito_user(self) -> bool:
        index = 1
        while self.browser.is_element_present_by_xpath(f"{self.INCOGNITO_JOBS_XPATH_PREFIX}[{index}]"):
            element = self.browser.find_by_xpath(f"{self.INCOGNITO_JOBS_XPATH_PREFIX}[{index}]").first
            job_href = element.find_by_css(self.INCOGNITO_JOB_URL_CSS_SELECTOR, wait_time=self.wait_time).first['href']
            self._add_normalized_job_url(self._extract_job_id_from_url(job_href))
            index += 1
        return index > 1

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
