from __future__ import print_function

from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import os
import json
import argparse
from pathvalidate.argparse import sanitize_filename, validate_filename_arg
from unique_id import get_unique_id
import sys
import time


def std_print(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def is_redirect(response):
    if response.status_code == 301:
        raise requests.HTTPError('Request redirected 301.')


def download_image(image_url, img_id, img_directory):
    response = requests.get(image_url, allow_redirects=False, timeout=5)
    response.raise_for_status()
    is_redirect(response)
    extension = img_id[-4:]
    img_name = sanitize_filename(os.path.join(get_unique_id(6), extension))
    file_path = os.path.join(img_directory, img_name)
    with open(file_path, 'wb') as file:
        file.write(response.content)
    return file_path


def download_txt(download_url, book_title, book_directory):
    response = requests.get(download_url, allow_redirects=True, timeout=5)
    response.raise_for_status()
    is_redirect(response)
    my_id = get_unique_id(6)
    book_name = sanitize_filename(f'{my_id} - {book_title}.txt')
    file_path = os.path.join(book_directory, book_name)
    with open(file_path, 'w') as file:
        file.write(response.text)
    return file_path


def get_soup(url):
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    is_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    return soup


def get_link(page_pars):
    links = page_pars.select('table.d_book a')
    url = [link.get('href') for link in links].pop(8)
    return url


def get_argpars(last_page):
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_page', type=int, nargs='?', default=1, help='input start page number to pars.')
    parser.add_argument('--end_page', type=int, nargs='?', default=last_page,
                        help='input end page number to pars.')
    parser.add_argument('--dist_folder', type=validate_filename_arg, nargs='?', default='dest_folder')
    parser.add_argument('--skip_imgs', action='store_false', default=False,
                        help='''input '--skip_imgs' if want skip downloading image files.''')
    parser.add_argument('--skip_txt', action='store_false', default=False,
                        help='''input '--skip_txt' if want skip download text files.''')
    parser.add_argument('--json_path', type=str, nargs='?', default=os.path.join('dest_folder', 'json'),
                        help='input path to json file.')
    return parser


def get_end_page(main_page_url):
    soup = get_soup(main_page_url).select('.center a')
    pages = [page.text for page in soup][-1:]
    last_page = int(''.join(pages)) + 1
    return last_page


def serialize_book(book):
    img_id = book.select_one('img')['src']
    book_id = book.select_one('a')['href']
    book_title = ''.join(book.select_one('a')['title'].split(' - ')[1:])
    book_author = ''.join(book.select_one('a')['title'].split(' - ')[:1])
    return img_id, book_id, book_title, book_author


def make_directories(args):
    main_directory = args.dist_folder
    os.makedirs(main_directory, exist_ok=True)
    img_directory = os.path.join(main_directory, 'imgs')
    os.makedirs(img_directory, exist_ok=True)
    book_directory = os.path.join(main_directory, 'books')
    os.makedirs(book_directory, exist_ok=True)
    dir_json = args.json_path
    os.makedirs(dir_json, exist_ok=True)
    return main_directory, img_directory, book_directory, dir_json


def serialize_page(page_pars):
    comments_pars = page_pars.select(".black")
    comments = [comment.text.replace('\n', '') for comment in comments_pars][10:]
    genres_pars = page_pars.select("span.d_book a[href]")
    genres = [genre.text for genre in genres_pars]
    return comments, genres


def get_catalog_serialize(book_title, book_author, img_path, book_path, comments, genres):
    return {
        'title': book_title,
        'author': book_author,
        'img_src': img_path,
        'book_path': book_path,
        'comments': comments,
        'genres': genres
    }


def main():
    main_page_url = 'http://tululu.org/l55'
    books_catalog = []
    book_path = img_path = None

    try:
        last_page = get_end_page(main_page_url)
        parser = get_argpars(last_page)
        args = parser.parse_args()

        main_directory, img_directory, book_directory, dir_json = make_directories(args)

        for page in range(args.start_page, args.end_page):
            url = f'http://tululu.org/l55/{page}'
            books = get_soup(url).select("table.d_book")
            for book in books:
                try:
                    img_id, book_id, book_title, book_author = serialize_book(book)
                    book_url = urljoin(url, book_id)
                    page_pars = get_soup(book_url)
                    download_link = get_link(page_pars)
                    print(download_link)
                except IndexError:
                    print(f'Download link is broken or is absent - {book_title}.')
                    download_link = None

                download_url = urljoin(book_url, download_link)
                image_url = urljoin(url, img_id)
                comments, genres = serialize_page(page_pars)

                if not args.skip_txt:
                    if download_link:
                        book_path = download_txt(download_url, book_title, book_directory)
                if not args.skip_imgs:
                    if not 'nopic' in img_id:
                        img_path = download_image(image_url, img_id, img_directory)

                books_catalog.append(
                    get_catalog_serialize(book_title, book_author, img_path, book_path, comments, genres))

        with open(os.path.join(dir_json, 'books_catalog.json'), 'w', encoding='utf8') as file:
            json.dump(books_catalog, file, ensure_ascii=False, indent=4)

    except requests.exceptions.ConnectionError:
        std_print('Connection error')
        time.sleep(3)


if __name__ == '__main__':
    main()
