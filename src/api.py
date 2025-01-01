import os

from fastapi import FastAPI, BackgroundTasks, Header
from fastapi.middleware.cors import CORSMiddleware
import uuid


from models.request_models import JobScraperPayload, ProfileUpdatePayload
from models.response_models import ScraperResponsePayload
from handlers import (
    LinkedInScrapeActionsHandler,
    LinkedInProfileUpdateHandler,
    OtherDashboardsScrapeHandler,
)

app = FastAPI()
app.secret_key = str(uuid.uuid4())

# Dispatcher service
dispatcher_url = os.getenv("DISPATCHER_SERVICE_URL")

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[dispatcher_url],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)


def process_linkedin_search(request_payload: JobScraperPayload, user_id: str) -> None:
    """Process the LinkedIn search task in the background."""
    handler = LinkedInScrapeActionsHandler(payload=request_payload, user_id=user_id)
    handler.process()

def process_linkedin_scraping(request_payload: JobScraperPayload, user_id: str) -> None:
    """Process the LinkedIn scraping task in the background."""
    handler = LinkedInScrapeActionsHandler(payload=request_payload, user_id=user_id)
    handler.process()

def process_linkedin_profile_update(request_payload: ProfileUpdatePayload, user_id: str) -> None:
    """Process the LinkedIn profile update task in the background."""
    handler = LinkedInProfileUpdateHandler(payload=request_payload, user_id=user_id)
    handler.process()

def process_other_dashboard_scraping(request_payload: JobScraperPayload, user_id: str) -> None:
    """Process the scraping task for other dashboards in the background."""
    handler = OtherDashboardsScrapeHandler(payload=request_payload, user_id=user_id)
    handler.process()

async def initiate_task(request_payload, background_tasks: BackgroundTasks, user_id: str, task_handler) -> ScraperResponsePayload:
    """Initiate a background task and return the initial processing result."""
    background_tasks.add_task(task_handler, request_payload, user_id)
    return ScraperResponsePayload(response="task initiated")

@app.post("/api/linkedin/search", response_model=ScraperResponsePayload)
async def initiate_linkedin_search(request_payload: JobScraperPayload, background_tasks: BackgroundTasks, userId: str = Header(...)):
    """Start the LinkedIn search task and return the initial processing result."""
    return await initiate_task(request_payload, background_tasks, userId, process_linkedin_search)

@app.post("/api/linkedin/scrape", response_model=ScraperResponsePayload)
async def initiate_linkedin_scraping(request_payload: JobScraperPayload, background_tasks: BackgroundTasks, userId: str = Header(...)):
    """Start the LinkedIn scraping task and return the initial processing result."""
    return await initiate_task(request_payload, background_tasks, userId, process_linkedin_scraping)

@app.post("/api/other/scrape", response_model=ScraperResponsePayload)
async def initiate_other_dashboard_scraping(request_payload: JobScraperPayload, background_tasks: BackgroundTasks, userId: str = Header(...)):
    """Start the scraping task on other dashboards and return the initial processing result."""
    return await initiate_task(request_payload, background_tasks, userId, process_other_dashboard_scraping)

@app.post("/api/linkedin/refreshProfile", response_model=ScraperResponsePayload)
async def initiate_linkedin_profile_update(request_payload: ProfileUpdatePayload, background_tasks: BackgroundTasks, userId: str = Header(...)):
    """Start the LinkedIn profile update task and return the initial processing result."""
    return await initiate_task(request_payload, background_tasks, userId, process_linkedin_profile_update)