import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv()

notion_key = os.getenv('NOTION_API_KEY')
gemini_key = os.getenv('GEMINI_API_KEY')

url = 'https://www.bbc.com/news'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
}

cardClass = 'sc-225578b-0 btdqbl'
headlines = []

def main():
    response = httpx.get(url, headers=headers, follow_redirects=True)
    response.html = response.text

    soup = BeautifulSoup(response.html, 'html.parser')

    headlines = soup.find_all('div', class_=cardClass)

    for headline in headlines:
        try:
            headlineText = headline.find(attrs={'data-testid': 'card-headline'}).text
            headlineDescription = headline.find(attrs={'data-testid': 'card-description'}).text
            headlineElapsedTime = headline.find(attrs={'data-testid': 'card-metadata-lastupdated'}).text
            headlineCategory = headline.find(attrs={'data-testid': 'card-metadata-tag'}).text
            headlineLink = 'https://www.bbc.com' + headline.find(attrs={'data-testid': 'internal-link'}).get('href')
        except:
            continue

        if headlineText not in headlines:
            headlines.append(headlineText)
        else:
            continue
        
        print(headlineText)
        print(headlineDescription)
        print(headlineElapsedTime)
        print(headlineCategory)
        print(headlineLink)
        print('--------------------------------')




if __name__ == '__main__':
    main()
