from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse
import os
import json


def make_url(url, title):
    base_url = urljoin(url, title)
    return base_url


def download_image(url, img_id, img_directory):
    image_url = urljoin(url, img_id)
    response = requests.get(image_url)
    response.raise_for_status()
    img_name = ''.join(img_id.split('/')[-1:])
    file_path = os.path.join(img_directory, img_name)
    with open(file_path, 'wb') as file:
        file.write(response.content)
    return file_path


def download_txt(book_url, num, book_title, book_directory):
    link = None
    soup = get_soup(book_url)
    links = soup.find('table', class_='d_book').find_all('a')
    for a in links:
        if 'txt' in a['href']:
            link = a['href']
    if link is not None:
        download_url = make_url(book_url, link)
        response = requests.get(download_url, allow_redirects=True)
        response.raise_for_status()
        if response.status_code == 200:
            file_path = os.path.join(book_directory, f'{num}-я, {book_title}.txt')
            with open(file_path, 'w') as file:
                file.write(response.text)
            return file_path
    else:
        return 'No txt file of book'


def get_comments(book_url):
    response = requests.get(book_url)
    response.raise_for_status()


def get_soup(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    return soup


def main():
    img_directory = 'imgs'
    os.makedirs(img_directory, exist_ok=True)
    book_directory = 'books'
    os.makedirs(book_directory, exist_ok=True)
    dir_json = 'json'
    os.makedirs(dir_json, exist_ok=True)
    page_num = 0

    books_catalog = []
    for page in range(1, 5):
        url = f'http://tululu.org/l55/{page}'
        soup = get_soup(url)
        books = soup.find_all('table', class_='d_book')
        for book in books:
            page_num += 1
            book_title = ''.join(book.find('a')['title'].split(' - ')[1:])
            book_author = ''.join(book.find('a')['title'].split(' - ')[:1])
            img_id = book.find('img')['src']
            book_id = book.find('a')['href']
            book_url = make_url(url, book_id)
            book_path = download_txt(book_url, page_num, book_title, book_directory)
            if book_path != 'No txt file of book':
                img_path = download_image(url, img_id, img_directory)
                page_soup = get_soup(book_url)
                comments_tags = page_soup.find_all('div', class_='texts')
                comments = [comment.find('span', class_='black').text.replace('\n', '') for comment in comments_tags]
                genres_tag = page_soup.find('span', class_='d_book').find_all('a')
                genres = [genre.text for genre in genres_tag]
                print(book_path)

            if book_path != 'No txt file of book':
                books_catalog.append({
                    'title': book_title,
                    'author': book_author,
                    'img_src': img_path,
                    'book_path': book_path,
                    'comments': comments,
                    'genres': genres
                }, )

    with open(os.path.join(dir_json, 'books_catalog.json'), 'w', encoding='utf8') as file:
        json.dump(books_catalog, file, ensure_ascii=False, sort_keys=True, indent=4)


if __name__ == '__main__':
    main()
