from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import os
import json
import argparse


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


def download_txt(book_url, num, book_title, book_directory, link):
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


def get_link(page_pars):
    link = None
    links = page_pars.select('table.d_book a')
    for a in links:
        if 'txt' in a['href']:
            link = a['href']
    return link


def get_argpars(lust_page):
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_page', type=int, help='input start page number to pars.')
    parser.add_argument('--end_page', type=int, nargs='?', default=lust_page,
                        help='input end page number to pars.')
    return parser


def get_end_page(main_page_url):
    soup = get_soup(main_page_url)
    pages = soup.select('.center a')
    page = [page.text for page in pages][-1:]
    lust_page = int(''.join(page))+1
    return lust_page


def main():
    img_directory = 'imgs'
    os.makedirs(img_directory, exist_ok=True)
    book_directory = 'books'
    os.makedirs(book_directory, exist_ok=True)
    dir_json = 'json'
    os.makedirs(dir_json, exist_ok=True)
    page_num = 0
    main_page_url = 'http://tululu.org/l55'
    lust_page = get_end_page(main_page_url)
    parser = get_argpars(lust_page)
    args = parser.parse_args()

    books_catalog = []
    for page in range(args.start_page, args.end_page):
        url = f'http://tululu.org/l55/{page}'
        soup = get_soup(url)
        books = soup.select("table.d_book")
        for book in books:
            page_num += 1
            book_author = ''.join(book.select_one('a')['title'].split(' - ')[:1])
            book_title = ''.join(book.select_one('a')['title'].split(' - ')[1:])
            img_id = book.select_one('img')['src']
            book_id = book.select_one('a')['href']
            book_url = make_url(url, book_id)
            page_pars = get_soup(book_url)
            link_txt = get_link(page_pars)

            if link_txt is not None:
                book_path = download_txt(book_url, page_num, book_title, book_directory, link_txt)
                img_path = download_image(url, img_id, img_directory)

                comments_pars = page_pars.select(".black")
                comments = [comment.text.replace('\n', '') for comment in comments_pars][10:]

                genres_pars = page_pars.select("span.d_book a[href]")
                genres = [genre.text for genre in genres_pars]

                print(book_url)

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
