from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse


def make_url(url, title):
    book_url = urljoin(url, title)
    return book_url


def main():
    url = 'http://tululu.org/l55/'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    books = soup.find_all('table', class_='d_book')
    for book in books:
        book_id = book.find('a')['href']
        book_url = make_url(url, book_id)
        print(book_url)


if __name__ == '__main__':
    main()
