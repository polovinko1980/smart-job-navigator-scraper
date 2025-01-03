import logging
import re
import sys
from typing import List

import selenium

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

    def __init__(self, browser, wait_time: int = 5):
        self.browser = browser
        self.wait_time = wait_time


    def scrape_as_authorized_user(self) -> List[str]:
        new_urls = []
        for e in self.browser.find_by_xpath(f"//div[@{self.AUTHORIZED_JOB_CSS_SELECTOR}]"):
            try:
                job_id = e[self.AUTHORIZED_JOB_CSS_SELECTOR]
                if len(job_id) == 10:
                    new_urls.append(self._add_normalized_job_url(job_id))
            except selenium.common.exceptions.StaleElementReferenceException:
                logger.warning(f"Unable to get job id from {e}")

        return new_urls

    def scrape_as_incognito_user(self) -> List[str]:
        self._dismiss_signin_widget()
        new_urls = []
        index = 1
        while self.browser.is_element_present_by_xpath(f"{self.INCOGNITO_JOBS_XPATH_PREFIX}[{index}]"):
            element = self.browser.find_by_xpath(f"{self.INCOGNITO_JOBS_XPATH_PREFIX}[{index}]").first
            job_href = element.find_by_css(self.INCOGNITO_JOB_URL_CSS_SELECTOR, wait_time=self.wait_time).first['href']
            new_urls.append(self._add_normalized_job_url(self._extract_job_id_from_url(job_href)))
            index += 1
        return new_urls

    def _dismiss_signin_widget(self) -> None:
        simulate_click_at_random_coordinates(self.browser)

    @staticmethod
    def _extract_job_id_from_url(job_url: str) -> str:
        pattern = r'(?<=-)(\d+)(?=\?)'
        match = re.search(pattern, job_url)
        return match.group(0) if match else None

    def _add_normalized_job_url(self, job_id) -> str:
        return f"{self.LINKEDIN_JOB_URL_PREFIX}/{job_id}/"
