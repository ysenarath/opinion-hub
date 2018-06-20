import time

import tweepy


def get_location(country):
    try:
        from geopy.geocoders import Yandex
        geo_locator = Yandex(lang='en_US')
        location = geo_locator.geocode(country, timeout=10)
        return location
    except ImportError:
        raise ImportError('Cannot import geocoder.')


def get_bounds(country):
    location = get_location(country).raw
    bounds_raw = location['boundedBy']['Envelope']
    upper = list(map(eval, bounds_raw['upperCorner'].split()))
    lower = list(map(eval, bounds_raw['lowerCorner'].split()))
    return lower + upper


def unicode_decode(text):
    try:
        return text.encode('utf-8').decode()
    except UnicodeDecodeError:
        return text.encode('utf-8')


class WaitUntil:
    def __init__(self, predicate, timeout=None, period=1):
        self._predicate = predicate
        self._timeout = timeout
        self._period = period

    # based on https://stackoverflow.com/a/2785908/1056345
    def __call__(self, *args, **kwargs):
        if self._timeout is None:
            while True:
                if self._predicate(*args, **kwargs):
                    return True
                time.sleep(self._period)
        else:
            must_end = time.time() + self._timeout
            while time.time() < must_end:
                if self._predicate(*args, **kwargs):
                    return True
                time.sleep(self._period)
        return False


def get_api(consumer_key, consumer_secret, access_token, access_token_secret):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)
    return api, auth


def generate_schema(value, schema=None):
    if isinstance(value, dict):
        if schema is None:
            schema = dict()
        for k in value.keys():
            v = value[k]
            if isinstance(v, list):
                schema[k] = {'list': generate_schema(v[0]) if len(v) > 0 else 'NoneType'}
            else:
                schema[k] = generate_schema(v)
    else:
        return type(value).__name__
    return schema
