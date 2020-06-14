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


def get_base_url(download_url, payload_id):
    url = urlparse(download_url)
    base_url = url._replace(path=str(payload_id)).geturl()
    return base_url


def get_image(book_img_url, download_url):
    image_url = urlparse(download_url)._replace(path=book_img_url).geturl()
    return image_url


def get_title(download_url, payload_id):
    base_url = get_base_url(download_url, payload_id)
    response = requests.get(base_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    book_title = soup.find('h1').text.split('::').pop(0).strip()
    if soup.find('div', class_='bookimage'):
        book_img_url = soup.find('div', class_='bookimage').find('img')['src']
        img_url = get_image(book_img_url, download_url)

    else:
        book_img_url = soup.find('img', class_='imtexts')['src']
        img_url = get_image(book_img_url, download_url)
    return book_title, img_url


def main():
    download_url = 'http://tululu.org/txt.php'

    directory = 'books'
    os.makedirs(directory, exist_ok=True)
    for i in range(10):
        _id = i + 1
        payload = {'id': _id}
        title, img_src = get_title(download_url, payload_id=f'b{_id}')
        filename = f'{_id}. {title}'
        # filepath = download_txt(download_url, payload, filename, directory)
        print(title)
        print(img_src)


if __name__ == '__main__':
    main()
