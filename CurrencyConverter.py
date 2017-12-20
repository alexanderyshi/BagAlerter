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
        return cache[currency].response['rates']
    return None


def _get_rates(currency_base):
    url = url_base + 'latest?base=' + currency_base
    r = requests.get(url, headers=headers)
    response = r.json()
    _cache(currency_base, response)
    return response['rates']


def convert(value, currency, target):
    if target == currency:
        return value

    currency_cached = _get_cached(currency)
    target_cached = _get_cached(target)

    if currency_cached is not None:
        if target in currency_cached:
            return value * currency_cached[target]
        else:
            raise Exception("Currency not found")
    elif target_cached is not None:
        if currency in target_cached:
            return value / target_cached[currency]
        else:
            raise Exception("Currency not found")
    else:
        rates = _get_rates(currency)
        if target in rates:
            return value * rates[target]
        else:
            raise Exception("Currency not found")


def _main():
    # caching test
    convert(3599, "USD", "CAD")
    convert(3599, "USD", "CAD")
    convert(3599, "USD", "CAD")
    convert(3599, "USD", "CAD")
    convert(3599, "USD", "CAD")
    convert(3599, "USD", "CAD")
    convert(3599, "USD", "CAD")
    convert(3599, "USD", "CAD")
    print convert(3599, "USD", "CAD")

    convert(4624.715, "CAD", "USD")
    convert(4624.715, "CAD", "USD")
    convert(4624.715, "CAD", "USD")
    convert(4624.715, "CAD", "USD")
    convert(4624.715, "CAD", "USD")
    print convert(4624.715, "CAD", "USD")


if __name__ == "__main__":
    _main()
