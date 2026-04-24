"""Configuration settings loaded from environment variables."""

import os

from dotenv import load_dotenv

load_dotenv()
load_dotenv(".env.local", override=True)

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "morningpulse_bot/1.0")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")
NEWSAPI_COUNTRY = os.getenv("NEWSAPI_COUNTRY", "us")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))

TOP_HN_STORIES = int(os.getenv("TOP_HN_STORIES", "15"))
TOP_NEWS_HEADLINES = int(os.getenv("TOP_NEWS_HEADLINES", "8"))
NEWSAPI_CATEGORIES = ["technology", "business", "general"]

KEYWORDS = [
    "EdTech",
    "school management",
    "teacher tools",
    "LMS",
    "gradebook",
    "classroom software",
    "learning management",
    "student information system",
    "school app",
    "canvas lms",
    "google classroom",
    "schoology",
    "classdojo",
    "powerschool",
]

COMPETITOR_NAMES = [
    "ClassDojo",
    "Google Classroom",
    "Canvas",
    "Schoology",
    "PowerSchool",
    "Blackboard",
    "Seesaw",
    "Edmodo",
    "Remind",
]

HOURS_LOOKBACK = 48
SCHEDULE_HOUR = 8
SCHEDULE_MINUTE = 0
OUTPUT_DIR = "outputs/"
MAX_POSTS = 60
GEMINI_MODEL = "gemini-flash-latest"
