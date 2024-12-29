from enum import Enum
from typing import List, Union, Optional
from pydantic import BaseModel

from utils.browser_provider import BrowserOptions


class DashboardEnum(str, Enum):
    LINKEDIN = "LINKEDIN"
    OTHER = "OTHER"


class ActionEnum(str, Enum):
    LINKEDIN_JOB_SEARCH = "linkedin_job_search"
    LINKEDIN_JOB_DETAILS = "linkedin_job_details"
    ARBITRARY_JOB_DETAILS = "arbitrary_job_details"

class UserCookie(BaseModel):
    name: str
    value: str
    domain: str
    path: str



class JobScraperPayload(BaseModel):
    jobDashboard: DashboardEnum
    action: ActionEnum
    authorizedUser: bool
    entryPoints: Optional[List[Optional[str]]] = None
    browserOptions: BrowserOptions
    userCookies: Optional[Union[List[UserCookie] | None]]
    callbackUrl: Optional[Union[str | None]]

class ProfileUpdatePayload(BaseModel):
    userHeadline: str
    browserOptions: BrowserOptions
    userCookies: Optional[Union[List[UserCookie] | None]]
    authorizedUser: bool = True
