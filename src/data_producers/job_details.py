import logging
import sys
import time

from models.response_models import JobDetails


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


class LinkedInJobPostingScraper:
    LINKEDIN_JOB_URL = 'https://www.linkedin.com/jobs/view'
    CSS_SELECTORS = {
        "show_more": '[data-tracking-control-name="public_jobs_show-more-html-btn"]',
        "position": '[class="top-card-layout__title font-sans text-lg papabear:text-xl font-bold leading-open text-color-text mb-0 topcard__title"]',
        "company": '[data-tracking-control-name="public_jobs_topcard-org-name"]',
        "salary": '[class="salary compensation__salary"]',
        "job_details": '[id="main-content"]',
        "expand_details_authorized": "(//div[@class='job-details-about-the-job-module__description']/div/button)",
        "expand_details_incognito": '[aria-label="Click to see more description"]',
        "job_details_authorized": '[class="job-details-about-the-job-module__description"]',
        "job_details_incognito": '[id="job-details"]',
        "company_from_card": '[class="job-details-jobs-unified-top-card__company-name"]',
        "position_from_card": '[class="t-24 job-details-jobs-unified-top-card__job-title"]',
    }

    def __init__(self, browser, wait_time: int = 5):
        self.job_details = None
        self.browser = browser
        self.wait_time = wait_time

    def fetch_linkedin_job_details(self, entry_point: str, is_authorized_user=True)->JobDetails:
        self.job_details = JobDetails(url=entry_point)
        self._navigate_to_job_page(url=entry_point)
        self._expand_job_details(is_authorized_user)
        self._extract_job_details(is_authorized_user)
        logger.info(f"Retrieved LinkedIn job details: {self.job_details.position}@{self.job_details.companyName}")
        return self.job_details

    def _navigate_to_job_page(self, url):
        self.browser.visit(url)

        if not self._is_job_visible(url):
            raise RuntimeError(f"Unable to navigate to {url}")

    def _expand_job_details(self, is_authorized_user):
        selector = self.CSS_SELECTORS["expand_details_authorized"] if is_authorized_user else self.CSS_SELECTORS["expand_details_incognito"]
        self.browser.find_by_xpath(selector, wait_time=self.wait_time).first.click()

    def _extract_job_details(self, is_authorized_user):
        self.job_details.rawJobDescription = self._get_raw_job_details(is_authorized_user)
        self._extract_job_attributes(is_authorized_user)

    def _get_raw_job_details(self, is_authorized_user):
        css_selector = self.CSS_SELECTORS["job_details_authorized"] if is_authorized_user else self.CSS_SELECTORS["job_details_incognito"]
        return self.browser.find_by_css(css_selector, wait_time=self.wait_time).first.text

    def _extract_job_attributes(self, is_authorized_user):
        if is_authorized_user:
            self._extract_authorized_user_attributes()
        else:
            self._extract_incognito_user_attributes()

    def _extract_authorized_user_attributes(self):
        self.job_details.companyName = self._get_text_from_css(self.CSS_SELECTORS["company_from_card"])
        self.job_details.position = self._get_text_from_css(self.CSS_SELECTORS["position_from_card"])

    def _extract_incognito_user_attributes(self):
        self.job_details.companyName = self._get_text_from_css(self.CSS_SELECTORS["company"])
        self.job_details.position = self._get_text_from_css(self.CSS_SELECTORS["position"])

    def _get_text_from_css(self, css_selector):
        return self.browser.find_by_css(css_selector, wait_time=self.wait_time).first.text

    def _is_job_visible(self, url):
        for attempt in range(5):
            page_html = self.browser.html
            if "ERR_TOO_MANY_REDIRECTS" in page_html or "HTTP ERROR 429" in page_html:
                self.browser.visit(url)
                time.sleep(self.wait_time)
                continue
            elif self.LINKEDIN_JOB_URL in self.browser.url:
                return True
        return False


class ArbitraryJobPostingScraper:

    JOB_DESCRIPTION_LIMIT = 16000

    def __init__(self, browser, wait_time: int = 5):
        self.browser = browser
        self.wait_time = wait_time

    def fetch_arbitrary_job_details(self, entry_point: str)->JobDetails:
        self.browser.visit(entry_point)
        time.sleep(self.wait_time)
        logger.info(f"Visiting arbitrary url: {entry_point}. Current url: {self.browser.url}")
        raw_details = self._get_raw_job_text()
        logger.info(f"Retrieved arbitrary job details: {entry_point} of size {len(raw_details)}")
        return JobDetails(url=entry_point, rawJobDescription=raw_details)

    def _get_raw_job_text(self):
        raw_job_text = self.browser.find_by_xpath("(//body)").first.text[:self.JOB_DESCRIPTION_LIMIT]
        return raw_job_text
