import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
from google import genai
from google.genai import types
from notion_client import Client
import datetime
import re
from datetime import datetime, timedelta

load_dotenv()

notion_key = os.getenv('NOTION_API_KEY')
notion_database_id = os.getenv('NOTION_DATABASE_ID')

def get_article_datetime(elapsed_str):
    now = datetime.now()
    elapsed_str = elapsed_str.lower().strip()
    if "min" in elapsed_str:
        minutes = int(re.search(r"(\d+)\s*min", elapsed_str).group(1))
        return now - timedelta(minutes=minutes)
    elif "hr" in elapsed_str:
        hours = int(re.search(r"(\d+)\s*hr", elapsed_str).group(1))
        return now - timedelta(hours=hours)
    elif "day" in elapsed_str:
        days = int(re.search(r"(\d+)\s*day", elapsed_str).group(1))
        return now - timedelta(days=days)
    else:
        return now

def main():
    client = genai.Client()
    notion = Client(auth=notion_key)

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    page_title = f"News Summary for {date_str}"

    new_page = notion.pages.create(
        parent={"database_id": notion_database_id},
        properties={
            "Name": {
                "title": [
                    {
                        "type": "text",
                        "text": {
                            "content": page_title
                        }
                    }
                ]
            }
        }
    )
    summary_page_id = new_page["id"]
    print(f"Created summary page with ID: {summary_page_id}")

    cardClass = 'sc-225578b-0 btdqbl'
    articleTextBlockClass = 'sc-9a00e533-0 hxuGS'
    parsedArticles = []

    url = 'https://www.bbc.com/news'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
    }

    response = httpx.get(url, headers=headers, follow_redirects=True)
    response.html = response.text

    soup = BeautifulSoup(response.html, 'html.parser')

    headlines = soup.find_all('div', class_=cardClass)

    for headline in headlines:
        try:
            headlineText = headline.find(attrs={'data-testid': 'card-headline'}).text
            headlineBlurb = headline.find(attrs={'data-testid': 'card-description'}).text
            headlineElapsedTime = headline.find(attrs={'data-testid': 'card-metadata-lastupdated'}).text
            headlineCategory = headline.find(attrs={'data-testid': 'card-metadata-tag'}).text
            headlineLink = 'https://www.bbc.com' + headline.find(attrs={'data-testid': 'internal-link'}).get('href')
        except:
            continue

        if headlineText not in parsedArticles:
            parsedArticles.append(headlineText)
        else:
            continue

        articlePage = httpx.get(headlineLink, headers=headers, follow_redirects=True)
        articlePage.html = articlePage.text
        articleSoup = BeautifulSoup(articlePage.html, 'html.parser')
        articleTextBlocks = articleSoup.find_all('p', class_=articleTextBlockClass)
        articleText = ''
        for block in articleTextBlocks:
            articleText += block.text

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are a professional summarizer that condenses news into short, accurate briefs. Always include all key facts and avoid injecting opinions. Avoid Using complex words and sentences. Use simple words and sentences."
                )
            ),
            contents=(
                f"Summarize the following news article in no more than 4 sentences. Include all critical information such as who, what, when, where, why, and how, while preserving factual accuracy. Avoid unnecessary details or commentary. Write in a neutral tone. ARTICLE: {articleText}"
            )
        )

        article_dt = get_article_datetime(headlineElapsedTime)
        date_str = article_dt.strftime("%Y-%m-%d")
        time_str = article_dt.strftime("%H:%M")
        block_content = (
            f"{date_str} {time_str}\n"
            f"Title: {headlineText}\n"
            f"Category: {headlineCategory}\n"
            f"Link: {headlineLink}\n"
            f"Summary: {response.text}"
        )

        try:
            notion.blocks.children.append(
                block_id=summary_page_id,
                children=[
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": block_content
                                    }
                                }
                            ]
                        }
                    }
                ]
            )
            print(f"Added article: {headlineText}")
        except Exception as e:
            print(f"Error appending article: {e}")

if __name__ == '__main__':
    main()
