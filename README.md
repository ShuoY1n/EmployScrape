# AutoNews

A web scraping project that extracts news articles from BBC News, summarizes them using Google's Gemini AI, and stores the results in Notion.

## What it does

- Scrapes the latest 5 news headlines from BBC News
- Extracts article content and metadata
- Uses Google Gemini AI to generate concise summaries
- Automatically creates daily summary pages in Notion
- Organizes articles with categories, timestamps, and links

## Motivation

I wanted to explore web scraping technologies and see how they could be combined with AI tools to automate content curation and summarization workflows.

## Technologies Used

- **Web Scraping**: httpx, BeautifulSoup4
- **AI**: Google Gemini API
- **Database**: Notion API
- **Environment**: Python with dotenv

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Set up environment variables for Notion and Google API keys
3. Run: `python scraper.py`
