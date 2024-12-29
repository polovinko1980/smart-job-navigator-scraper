# Smart Job Navigator Scraping Service
Service to scrape job posting dashboards using Splinter, post back job urls or job postings description


## Overview
This is a web scraping service designed to extract data from various websites and provide it through a RESTful API. 
The service is built with Python FastAPI and Splinter WebDriver and is designed to be easy to use and deploy.

It is also stateless and keeping all processing results in memory.

The purpose of having this service was to overcome LinkedIn api limitations
to get access to new job postings. 

This service is part of bigger project for automating job search routines, but can
be used independently for sure or extended to run any web scraping routines.


## Features

- Scrape data from multiple sources
- RESTful API for easy access to scraped data
- Docker support for easy deployment

## Getting Started

### Prerequisites

- [Python](https://www.python.org/)
- [Docker](https://www.docker.com/)

### Local Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/polovinko1980/smart-job-navigator-scraper.git
   cd smart-job-navigator-scraper
   ```

2. Install dependencies:
   ```bash
   pip3 install -r requirements.txt  # For Python
   ```

3. Start the application:
   ```bash
    fastapi run src/api.py
   ```

4. The application should now be running on `http://localhost:8000` (or the port specified in your configuration).

### Dockerized Setup

1. Build the Docker image:
   ```bash
   docker buildx build --platform linux/amd64 -t polovinko1980/sjn-scraper:develop.latest -f DockerFile .
   ```

2. Run the Docker container:
   ```bash
   docker run -d -p 8081:8081--name scraper polovinko1980/sjn-scraper:develop.latest
   ```

3. The application will be accessible at `http://localhost:8081`.

## API Endpoints

### 1. Scrape Data

**Endpoint:** `POST /api/linkedin/search`

**Description:** Initiates a scraping task for getting job urls or job details.

**Request Body:**
```json
{
     "jobDashboard": "LINKEDIN",
     "action": "linkedin_job_search",
     "authorizedUser": true,
     "entryPoints": [
             "https://www.linkedin.com/jobs/search/?currentJobId=4018729848&distance=25&f_E=4&f_SB2=8&f_TPR=r86400&geoId=90000084&keywords=software%20engineer%20in%20test&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true",
             "https://www.linkedin.com/jobs/search/?currentJobId=4018729848&distance=25&f_E=4&f_SB2=8&f_TPR=r86400&geoId=90000084&keywords=software%20engineer%20in%20test&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true",
             "https://www.linkedin.com/jobs/search/?currentJobId=4018729848&distance=25&f_E=4&f_SB2=8&f_TPR=r86400&geoId=90000084&keywords=software%20engineer%20in%20test&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true"
         ],
     "browserOptions": {
         "driverName": "chrome",
         "userAgent": "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
         "headlessMode": false
     },
     "userCookies": [
         {
             "name": "bcookie",
             "value": "\"v=2&eXXXXXXXXX6\"",
             "domain": ".linkedin.com",
             "path": "/"
         },
         {
             "name": "li_at",
             "value": "AQXXXXXXXXXXNCML",
             "domain": ".www.linkedin.com",
             "path": "/"
         }
     ]
}


```


### 2 Update Profile


**Endpoint:** `POST /api/linkedin/refreshProfile`

**Description:** Updates LinkedIn User profile headline.

**Request Body:**
```json
{
    "userHeadline": "Empowering Team Collaboration & Innovation in CI/CD. Passionate about Backend Testing and Microservices for enhanced Performance. Today hint: Cloud computing grew by 35% last year.",
     "browserOptions": {
         "driverName": "chrome",
         "userAgent": "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
         "headlessMode": false
     },
     "userCookies": [
         {
             "name": "bcookie",
             "value": "\"v=2&eXXXXXXXXX6\"",
             "domain": ".linkedin.com",
             "path": "/"
         },
         {
             "name": "li_at",
             "value": "AQXXXXXXXXXXNCML",
             "domain": ".www.linkedin.com",
             "path": "/"
         }
     ]
}


```

Full api spec is available on the running server at docs path:
```
http://localhost:8081/docs
```



## Contributing

If you would like to contribute to the project, please fork the repository and submit a pull request. 

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

