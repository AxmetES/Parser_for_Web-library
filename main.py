import requests
import os


def get_request_txt(url, payload):
    response = requests.get(url, params=payload, allow_redirects=False)
    response.raise_for_status()
    return response


def save_to_file(_id, response, directory):
    os.makedirs(directory, exist_ok=True)
    with open(os.path.join(directory, f'id{_id}.txt'), 'w') as file:
        file.write(response.text)


def get_txt_by_id(url, directory, range_num):
    for i in range(range_num):
        _id = 1 + i
        payload = {'id': _id}
        response = get_request_txt(url, payload)
        if response.status_code == 200:
            save_to_file(_id, response, directory)


def main():
    url = 'http://tululu.org/txt.php'
    directory = 'books'
    range_num = 10
    get_txt_by_id(url, directory, range_num)


if __name__ == '__main__':
    main()
