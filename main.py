import httpx
from bs4 import BeautifulSoup

url = 'https://www.cnn.com/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
}

def main():
    response = httpx.get(url, headers=headers, follow_redirects=True)
    response.html = response.text

    soup = BeautifulSoup(response.html, 'html.parser')
    print(soup.find_all('a'))


if __name__ == '__main__':
    main()
