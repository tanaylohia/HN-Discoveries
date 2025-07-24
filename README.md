# HN Discoveries - AI-Powered Startup & Innovation Tracker

An intelligent agent that monitors Hacker News to discover and analyze new startup announcements and technical innovations. Using GPT-4.1, it provides deep insights and automated daily reports.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)

## Features

- 🔍 **Smart Detection**: Uses GPT-4.1 to identify both startups and technical innovations
- 🤖 **AI-Powered Analysis**: Deep analysis of each discovery with innovation scoring
- 📊 **Historical Analysis**: Can analyze up to 60 days of historical HN data on first run
- ⏰ **Scheduled Updates**: Runs daily at 8 AM IST to find new discoveries
- 📈 **Comprehensive Scoring**: Rates discoveries on innovation, technical merit, and impact
- 🌐 **Web Dashboard**: Beautiful web interface to browse discoveries with filtering
- 📄 **JSON API**: Structured JSON output for easy integration
- 💾 **Persistent Storage**: SQLite database tracks processed posts and discoveries

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API keys:**
   - Copy `.env.example` to `.env`
   - Add your Azure OpenAI API key
   - Optionally add DeepSeek API key for alternative model

3. **Run the agent:**
   ```bash
   # Run once and generate report
   python main.py --run-once
   
   # Run historical scan for last 30 days
   python main.py --historical --days 30
   
   # Run as scheduled daemon (8 AM IST daily)
   python main.py --daemon
   
   # Launch web dashboard
   python main.py --dashboard
   ```

## How It Works

1. **Data Collection**: Fetches posts from Hacker News API (top, new, show stories)
2. **AI Classification**: GPT-4.1 classifies each post as:
   - **Startup**: Commercial ventures and companies
   - **Innovation**: Technical projects, research, tools, algorithms
   - **Other**: Neither of the above
3. **Deep Analysis**: For each discovery, AI extracts:
   - Name, category, and development stage
   - Innovation score (0-10) and coolness factor
   - Technical details and key features
   - Why it's interesting and noteworthy
4. **Report Generation**: Creates JSON reports and serves via web dashboard

## Configuration

Edit `config.py` to customize:
- Refresh schedule (default: 8 AM IST)
- Historical lookback period (default: 60 days)
- Minimum score thresholds
- API endpoints and models

## Web Dashboard

The dashboard provides:
- **Real-time view** of all discoveries
- **Filtering** by type (startups vs innovations)
- **Rich cards** with summaries and scores
- **Direct links** to HN discussions and project websites
- **Refresh button** to trigger new scans
- **Auto-refresh** every 5 minutes

## JSON Output Structure

```json
{
  "metadata": {
    "timestamp": "2025-07-24_20-51-32",
    "total_discoveries": 17,
    "total_startups": 5,
    "total_innovations": 12
  },
  "discoveries": [
    {
      "id": 44657727,
      "type": "startup" | "innovation",
      "name": "Project Name",
      "title": "HN Post Title",
      "url": "https://project-url.com",
      "hn_url": "https://news.ycombinator.com/item?id=44657727",
      "innovation_score": 8.5,
      "summary": "Brief description",
      "why_interesting": "Why this matters",
      "category": "AI/ML, Developer Tools",
      "key_features": ["feature1", "feature2"]
    }
  ]
}
```

## Database Schema

- **posts**: All processed HN posts
- **startups**: Detailed analysis of identified startups
- **run_history**: Track agent execution history

## Requirements

- Python 3.8+
- Azure OpenAI API access
- Internet connection for HN API access

## Future Enhancements

- Email notifications for high-score startups
- Web dashboard for browsing discoveries
- Custom search queries
- Trend analysis over time