"""
Configuration and database connection utilities.
"""

import os
from functools import lru_cache
from dotenv import load_dotenv
from supabase import create_client, Client


def load_env():
    """Load environment variables from .env file."""
    load_dotenv()


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    """Get cached Supabase client instance."""
    load_env()

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not url or not key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in environment")

    return create_client(url, key)


class Config:
    """Default configuration settings."""

    def __init__(self):
        load_env()
        self.DEFAULT_SPECIALTY = os.getenv("DEFAULT_SPECIALTY", "ophthalmology")
        self.OUTPUT_FORMAT = os.getenv("OUTPUT_FORMAT", "png")
        self.IMAGE_SIZE = int(os.getenv("IMAGE_SIZE", "1080"))

        # API credentials
        self.SUPABASE_URL = os.getenv("SUPABASE_URL")
        self.SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")
        self.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

        # Twitter API v2
        self.TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
        self.TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
        self.TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
        self.TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")


config = Config()
