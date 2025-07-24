import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pytz

# AIDEV-NOTE: Configuration file for Hacker News Agent
# Contains all settings, API endpoints, and constants

load_dotenv()

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_DEEPSEEK_API_KEY = os.getenv("AZURE_DEEPSEEK_API_KEY")

# API Endpoints (from CLAUDE.md)
AZURE_OPENAI_ENDPOINT = os.getenv(
    "AZURE_OPENAI_ENDPOINT", 
    "https://mandrakebioworkswestus.openai.azure.com/"
)
AZURE_DEEPSEEK_ENDPOINT = os.getenv(
    "AZURE_DEEPSEEK_ENDPOINT",
    "https://mandrake-resource.services.ai.azure.com/models"
)

# Model Configuration
GPT_4_1_DEPLOYMENT = "gpt-4.1"
GPT_O4_MINI_DEPLOYMENT = "o4-mini"
DEEPSEEK_MODEL = "DeepSeek-R1-0528"
API_VERSION = "2024-12-01-preview"

# Hacker News API
HN_API_BASE = "https://hacker-news.firebaseio.com/v0"
HN_WEB_BASE = "https://news.ycombinator.com"

# Time Settings
TIMEZONE = pytz.timezone('Asia/Kolkata')  # IST
REFRESH_TIME = "08:00"  # 8 AM IST
LOOKBACK_DAYS = 60  # Initial historical data fetch

# Database
DB_PATH = "hn_startups.db"

# Startup Detection Keywords
STARTUP_KEYWORDS = [
    "Show HN:", "Launch HN:", "startup", "founder", "co-founder",
    "we built", "we launched", "introducing", "announcing",
    "YC", "Y Combinator", "funding", "raised", "seed round",
    "Series A", "MVP", "beta", "early access", "waitlist"
]

# Technical Innovation Keywords
INNOVATION_KEYWORDS = [
    "Show HN:", "built", "created", "implemented", "developed",
    "open source", "open-source", "library", "framework", "tool",
    "algorithm", "technique", "breakthrough", "research", "paper",
    "performance", "optimization", "faster", "efficient", "novel",
    "AI", "ML", "machine learning", "neural", "quantum", "rust",
    "golang", "compiler", "interpreter", "database", "distributed",
    "protocol", "standard", "RFC", "proof of concept", "experiment"
]

# Filtering thresholds
MIN_SCORE = 10  # Minimum HN score to consider
MIN_COMMENTS = 5  # Minimum comments for engagement
MAX_AGE_DAYS = 7  # For daily updates, ignore posts older than this

# Output settings
REPORT_DIR = "reports"
REPORT_FORMAT = "markdown"  # or "json", "html"