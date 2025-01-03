import time
from typing import List, Dict, Callable

import requests

from models.request_models import ActionEnum

from models.response_models import (
    SearchResults,
    DetailsResults,
    JobDetails,
)

from data_producers.linkedin_job_search import LinkedInJobSearchScraper
from data_producers.job_details import LinkedInJobPostingScraper, ArbitraryJobPostingScraper
from data_producers.linkedin_profile_updater import LinkedInProfileUpdater
from utils.browser_authorizer import LinkedInAuthorizer, OtherDashboardAuthorizer


class BaseScrapeHandler:
    def __init__(self, payload=None, user_id=None):
        self.payload = payload
        self.user_id = user_id

    def _initialize_linkedin_browser(self):
        session = LinkedInAuthorizer(browser_options=self.payload.browserOptions)
        if self.payload.authorizedUser:
            return session.start_authorized_session(cookies=self.payload.userCookies)
        return session.start_incognito_session()

    def _initialize_other_dashboard_browser(self):
        session = OtherDashboardAuthorizer(browser_options=self.payload.browserOptions)
        return session.start_incognito_session()

    @staticmethod
    def _cleanup_browser(browser) -> None:
        if browser:
            try:
                browser.quit()
            except Exception as e:
                print(f"Error while quitting the browser: {e}")

    def _notify_completion(self, result) -> None:
        if self.payload.callbackUrl:
            payload = result.dict()
            headers = {"userId": self.user_id}
            requests.post(self.payload.callbackUrl, headers=headers, json=payload)

class LinkedInScrapeActionsHandler(BaseScrapeHandler):

    USER_PROCESSING_LIMIT = 100

    LINKEDIN_SEARCH_URL = "https://www.linkedin.com/jobs/search/?"

    def process(self):
        action_handlers: Dict[str, Callable] = {
            ActionEnum.LINKEDIN_JOB_SEARCH: self._handle_linkedin_job_search,
            ActionEnum.LINKEDIN_JOB_DETAILS: self._handle_linkedin_job_details,
        }

        action_handler = action_handlers.get(self.payload.action)
        if action_handler:
            return action_handler()
        raise RuntimeError(f"Not supported action: {self.payload.action}")

    def _handle_linkedin_job_search(self) -> None:
        self._fetch_linkedin_search_endpoints()

    def _handle_linkedin_job_details(self) -> None:
        self._fetch_linkedin_job_details()

    def _fetch_linkedin_search_endpoints(self) -> None:
        browser = self._initialize_linkedin_browser()
        try:
            for entry_point in self.payload.entryPoints:
                self._fetch_search_pages(browser, entry_point)
        finally:
            self._cleanup_browser(browser)

    def _fetch_search_pages(self, browser, entry_point: str) -> None:
        found_urls, start, page_size = 0, 0, 7
        job_search_scraper = LinkedInJobSearchScraper(browser=browser, wait_time=5)

        while found_urls < self.USER_PROCESSING_LIMIT:
            time.sleep(2)

            search_url = f"{entry_point}&start={start}"
            browser.visit(search_url)
            if not self._is_url_visible(browser, search_url):
                raise RuntimeError(f"Unable to navigate to {search_url}")

            if self.payload.authorizedUser:
                new_urls = job_search_scraper.scrape_as_authorized_user()
            else:
                new_urls = job_search_scraper.scrape_as_incognito_user()
            found_urls += len(new_urls)
            if not new_urls:
                break
            start += page_size
            self._notify_completion(SearchResults(urls=new_urls))

    def _fetch_linkedin_job_details(self) -> List[JobDetails]:
        browser = self._initialize_linkedin_browser()
        job_details_scraper = LinkedInJobPostingScraper(browser=browser, wait_time=5)
        job_details_list = []

        try:
            for entry_point in self.payload.entryPoints:
                job_details = self._fetch_job_details(job_details_scraper, entry_point)
                self._notify_completion(job_details)
                job_details_list.append(job_details)
        finally:
            self._cleanup_browser(browser)
        return job_details_list

    def _fetch_job_details(self, job_details_scraper, entry_point: str) -> JobDetails:
        return job_details_scraper.fetch_linkedin_job_details(
            entry_point=entry_point,
            is_authorized_user=self.payload.authorizedUser,
        )

    def _is_url_visible(self, browser, url):
        for attempt in range(5):
            page_html = browser.html
            if "ERR_TOO_MANY_REDIRECTS" in page_html or "HTTP ERROR 429" in page_html:
                browser.visit(url)
                time.sleep(5)
                continue
            elif self.LINKEDIN_SEARCH_URL in browser.url:
                return True
        return False

class OtherDashboardsScrapeHandler(BaseScrapeHandler):
    def process(self):
        action_handlers: Dict[str, Callable] = {
            ActionEnum.ARBITRARY_JOB_DETAILS: self._handle_arbitrary_job_details,
        }

        action_handler = action_handlers.get(self.payload.action)
        if action_handler:
            return action_handler()
        raise RuntimeError(f"Not supported action: {self.payload.action}")

    def _handle_arbitrary_job_details(self) -> DetailsResults:
        job_details = self._fetch_arbitrary_job_details()
        return DetailsResults(jobDetails=job_details)

    def _fetch_arbitrary_job_details(self) -> List[JobDetails]:
        browser = self._initialize_other_dashboard_browser()
        job_details_scraper = ArbitraryJobPostingScraper(browser=browser, wait_time=30)
        job_details_list = []

        try:
            for entry_point in self.payload.entryPoints:
                job_details = self._fetch_details(job_details_scraper, entry_point)
                self._notify_completion(job_details)
                job_details_list.append(job_details)
        finally:
            self._cleanup_browser(browser)
        return job_details_list

    @staticmethod
    def _fetch_details(job_details_scraper, entry_point: str) -> JobDetails:
        return job_details_scraper.fetch_arbitrary_job_details(entry_point=entry_point)

class LinkedInProfileUpdateHandler(BaseScrapeHandler):
    def process(self):
        return self._update_linkedin_user_profile()

    def _update_linkedin_user_profile(self) -> None:
        browser = self._initialize_linkedin_browser()
        try:
            self._perform_headline_update(browser)
        finally:
            self._cleanup_browser(browser)

    def _perform_headline_update(self, browser) -> None:
        profile_updater = LinkedInProfileUpdater(browser=browser, wait_time=5)
        profile_updater.update_headline(new_headline=self.payload.userHeadline)
