import requests


def is_redirect(response):
    if not response.is_redirect:
        raise requests.exceptions.HTTPError


def main():
    url = 'http://tululu.org/l55'
    response = requests.get(url, allow_redirects=True)
    is_redirect(response)
    print(response.history)
    print(response.url)


if __name__ == '__main__':
    main()
