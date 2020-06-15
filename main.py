import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import argparse


def get_args():
    parser = argparse.ArgumentParser(description='path url, filename, dir')
    parser.add_argument('foldername', nargs='?', type=str, default='books', help='input directory path')
    args = parser.parse_args()
    return args


def download_txt(url, payload, filename, folder):
    response = get_request_txt(url, payload)
    if response.status_code == 200:
        save_file(response, filename, folder)
        return f'{folder}/{filename}.txt'


def get_request_txt(url, payload):
    response = requests.get(url, params=payload, allow_redirects=False)
    response.raise_for_status()
    return response


def save_file(response, filename, folder):
    with open(os.path.join(folder, filename + '.txt'), 'w') as file:
        file.write(response.text)


def make_url(base_url, payload):
    base_url = urljoin(base_url, payload)
    return base_url


def download_image(img_src, img_directory):
    img_name = img_src.split('/')[-1]
    response = requests.get(img_src, allow_redirects=False)
    response.raise_for_status()
    file_path = os.path.join(img_directory, img_name)
    with open(file_path, 'wb') as file:
        file.write(response.content)
    return file_path


def get_title(download_url, payload_id):
    base_url = make_url(download_url, payload_id)
    response = requests.get(base_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    book_title = soup.find('h1').text.split('::').pop(0).strip()
    book_comments = soup.find_all('div', class_='texts')
    book_genres = soup.find_all('span', class_='d_book')

    if soup.find('div', class_='bookimage'):
        book_img_url = soup.find('div', class_='bookimage').find('img')['src']

    else:
        book_img_url = soup.find('img', class_='imtexts')['src']

    img_url = make_url(download_url, book_img_url)
    return book_title, img_url, book_comments, book_genres


def main():
    download_url = 'http://tululu.org/txt.php'

    book_directory = 'books'
    os.makedirs(book_directory, exist_ok=True)
    img_directory = 'img'
    os.makedirs(img_directory, exist_ok=True)
    for i in range(10):
        _id = i + 1
        payload = {'id': _id}
        title, img_src, book_comments, book_genres = get_title(download_url, payload_id=f'b{_id}')
        filename = f'{_id}. {title}'
        # filepath = download_txt(download_url, payload, filename, directory)
        img_filepath = download_image(img_src, img_directory)
        print(title)
        # print(img_src)
        print(img_filepath)
        for comment in book_genres:
            print(comment.text)


if __name__ == '__main__':
    main()
