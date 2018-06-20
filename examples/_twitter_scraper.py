import errno
import json
import os

from scrapt.feeds import TwitterArchiveFeed

_path = os.path.dirname(os.path.realpath(__file__))

consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''
hashtags = [
]

if __name__ == '__main__':
    for query in ['#{}'.format(x) for x in hashtags]:
        version = 0
        while True:
            filename = os.path.join(_path, 'output/twitter/{}_{}.json'.format(query, 'v_{}'.format(
                version) if version != 0 else ''))
            if os.path.exists(filename):
                version += 1
            else:
                break
        kwargs = {
            'auth': (consumer_key, consumer_secret),
            'access_token': (access_token, access_token_secret),
            'query': query,
            'max_tweets': 10000000
        }
        taf = TwitterArchiveFeed(**kwargs)
        taf.start()  # Starts new thread
        idx = 0
        for data in taf.collection():
            print(data)
            if idx % 100 == 0:
                if not os.path.exists(os.path.dirname(filename)):
                    try:
                        os.makedirs(os.path.dirname(filename))
                    except OSError as exc:  # Guard against race condition
                        if exc.errno != errno.EEXIST:
                            raise
                if os.path.exists(filename):
                    os.remove(filename)
                with open(filename, 'w', encoding='utf-8') as outfile:
                    json.dump(taf.get_all(), outfile)
            idx += 1
