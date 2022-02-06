import datetime as dt
from typing import List, Optional
from pydantic import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    APP_NAME: str
    BASE_URL: str
    CATEGORY_URL_PARTS: List[str]
    DATE_FORMAT: str
    DATE_STOP: Optional[dt.datetime] = dt.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - dt.timedelta(days=30)
    PAGE_URL_PART: str
    STARTING_PAGE: int
    DATE_FORMAT: str
    CSV_PATH: str
    CSV_FILENAME: str
    AD_TYPES: List[str]
    API_TIME_BETWEEN_REQUESTS_SECONDS: float
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

            
    
settings = Settings()

