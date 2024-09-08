from os import major
import httpx
from bs4 import BeautifulSoup

url = 'https://www.bbc.com/news'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
}

def main():
    response = httpx.get(url, headers=headers, follow_redirects=True)
    response.html = response.text

    soup = BeautifulSoup(response.html, 'html.parser')

    majorHeadline = soup.find('div', class_='sc-666b6d83-0 hWNlku')

    majorHeadlineText = majorHeadline.find(attrs={'data-testid': 'card-headline'}).text
    majorHeadlineDescription = majorHeadline.find(attrs={'data-testid': 'card-description'}).text
    majorHeadlineElapsedTime = majorHeadline.find(attrs={'data-testid': 'card-metadata-lastupdated'}).text
    majorHeadlineLocation = majorHeadline.find(attrs={'data-testid': 'card-metadata-tag'}).text


    majorHeadlineLink = 'https://www.bbc.com' + majorHeadline.find(attrs={'data-testid': 'internal-link'}).get('href')

    print(majorHeadlineText)
    print(majorHeadlineDescription)
    print(majorHeadlineElapsedTime)
    print(majorHeadlineLocation)
    print(majorHeadlineLink)



if __name__ == '__main__':
    main()
