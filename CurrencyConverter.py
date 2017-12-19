import requests
from datetime import datetime, timedelta

url_base = 'https://api.fixer.io/'
headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
cache = {}
cache_timeout = timedelta(hours=1)


class CachedResponse:

    def __init__(self, response):
        self.response = response
        self.retrieved = datetime.today()


def _cache(currency, response):
    cache[currency] = CachedResponse(response)


def _get_cached(currency):
    if currency in cache and datetime.today() - cache[currency].retrieved < cache_timeout:
        return cache[currency].response
    return None


def _get_rates(currency_base):
    cached_response = _get_cached(currency_base)
    if cached_response is not None:
        response = cached_response
    else:
        url = url_base + 'latest?base=' + currency_base
        r = requests.get(url, headers=headers)
        response = r.json()
        _cache(currency_base, response)
    return response['rates']


def convert(value, currency, target):
    rates = _get_rates(currency)
    if target in rates:
        return value * rates[target]
    elif target == currency:
        return value
    else:
        raise Exception("Currency not found")


def _main():
    print convert(3599, "USD", "CAD")


if __name__ == "__main__":
    _main()
