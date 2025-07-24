import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
from google import genai
from google.genai import types
from notion_client import Client
import datetime

load_dotenv()

notion_key = os.getenv('NOTION_API_KEY')
notion_database_id = os.getenv('NOTION_DATABASE_ID')

def main():
    client = genai.Client()
    notion = Client(auth=notion_key)
    
    cardClass = 'sc-225578b-0 btdqbl'
    articleTextBlockClass = 'sc-9a00e533-0 hxuGS'
    headlines = []

    url = 'https://www.bbc.com/news'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
    }
    
    response = httpx.get(url, headers=headers, follow_redirects=True)
    response.html = response.text

    soup = BeautifulSoup(response.html, 'html.parser')

    headlines = soup.find_all('div', class_=cardClass)

    count = 0

    for headline in headlines:
        count += 1
        if count > 1:
            break

        try:
            headlineText = headline.find(attrs={'data-testid': 'card-headline'}).text
            headlineBlurb = headline.find(attrs={'data-testid': 'card-description'}).text
            headlineElapsedTime = headline.find(attrs={'data-testid': 'card-metadata-lastupdated'}).text
            headlineCategory = headline.find(attrs={'data-testid': 'card-metadata-tag'}).text
            headlineLink = 'https://www.bbc.com' + headline.find(attrs={'data-testid': 'internal-link'}).get('href')
        except:
            continue

        if headlineText not in headlines:
            headlines.append(headlineText)
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

        try:
            new_page = notion.pages.create(
                parent={"database_id": notion_database_id},
                properties={
                    "Name": {
                        "title": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "News Summary for " + datetime.datetime.now().strftime("%Y-%m-%d")
                                }
                            }
                        ]
                    }
                },
                children=[
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": response.text
                                    }
                                }
                            ]
                        }
                    }
                ]
            )
            print(f"Page created successfully! ID: {new_page['id']}")
            
        except Exception as e:
            print(f"Error creating page: {e}")




if __name__ == '__main__':
    main()
