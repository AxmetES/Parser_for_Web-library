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
    links = page_pars.select('table.d_book a')
    for a in links:
        href = a.get('href')
        if 'txt.php' in href:
            return href


def get_argpars(lust_page):
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_page', type=int, nargs='?', default=1, help='input start page number to pars.')
    parser.add_argument('--end_page', type=int, nargs='?', default=lust_page,
                        help='input end page number to pars.')
    parser.add_argument('--dist_folder', type=str, nargs='?', default='dest_folder')
    parser.add_argument('--skip_imgs', action='store_false', default=True,
                        help='''input '--skip_imgs' if want skip downloading image files.''')
    parser.add_argument('--skip_txt', action='store_false', default=True,
                        help='''input '--skip_txt' if want skip download text files.''')
    parser.add_argument('--json_path', type=str, nargs='?', default=os.path.join('dest_folder', 'json'),
                        help='input path to json file.')
    return parser


def get_end_page(main_page_url):
    soup = get_soup(main_page_url)
    pages = soup.select('.center a')
    page = [page.text for page in pages][-1:]
    lust_page = int(''.join(page)) + 1
    return lust_page


def main():
    page_num = 0
    main_page_url = 'http://tululu.org/l55'
    lust_page = get_end_page(main_page_url)
    parser = get_argpars(lust_page)
    args = parser.parse_args()

    main_distr = args.dist_folder
    os.makedirs(main_distr, exist_ok=True)

    img_directory = os.path.join(main_distr, 'imgs')
    os.makedirs(img_directory, exist_ok=True)

    book_directory = os.path.join(main_distr, 'books')
    os.makedirs(book_directory, exist_ok=True)

    dir_json = args.json_path
    os.makedirs(dir_json, exist_ok=True)

    books_catalog = []
    for page in range(args.start_page, args.end_page):
        url = f'http://tululu.org/l55/{page}'
        soup = get_soup(url)
        books = soup.select("table.d_book")
        for book in books:

            img_id = book.select_one('img')['src']
            book_id = book.select_one('a')['href']
            book_url = make_url(url, book_id)
            page_pars = get_soup(book_url)
            download_link = get_link(page_pars)

            if download_link is not None:
                book_path = img_path = "no text or image, or downloading was skipped"
                page_num += 1
                book_title = ''.join(book.select_one('a')['title'].split(' - ')[1:])
                book_author = ''.join(book.select_one('a')['title'].split(' - ')[:1])
                if args.skip_txt:
                    book_path = download_txt(book_url, page_num, book_title, book_directory, download_link)
                if args.skip_imgs:
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
        json.dump(books_catalog, file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    main()
