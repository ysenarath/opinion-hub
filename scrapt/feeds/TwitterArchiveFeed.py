import time

import tweepy

from scrapt.feeds.__abc import ArchiveFeed


class TwitterArchiveFeed(ArchiveFeed):
    def __init__(self, auth, access_token, query, since_id=False, until_id=-1, max_tweets=100000, limit=100):
        super(TwitterArchiveFeed, self).__init__()
        # Authentication & Authorization
        self._auth = auth
        self._access_token = access_token
        # Query parameters
        self._query = query
        self._since_id = since_id
        self._until_id = until_id
        self._max_tweets = max_tweets
        self._limit = limit

    def collect(self):
        auth = tweepy.OAuthHandler(*self._auth)
        auth.set_access_token(*self._access_token)
        api = tweepy.API(auth, wait_on_rate_limit=True)
        max_id = self._until_id
        tweet_count = 0
        while tweet_count < self._max_tweets:
            try:
                if max_id <= 0:
                    if not self._since_id:
                        new_tweets = api.search(q=self._query, count=self._limit)
                    else:
                        new_tweets = api.search(q=self._query, count=self._limit, since_id=self._since_id)
                else:
                    if not self._since_id:
                        new_tweets = api.search(q=self._query, count=self._limit, max_id=str(max_id - 1))
                    else:
                        new_tweets = api.search(q=self._query, count=self._limit, max_id=str(max_id - 1),
                                                since_id=self._since_id)
                if not new_tweets:
                    break
                for tweet in new_tweets:
                    tweet_id = tweet._json['id']
                    tweet_status = api.get_status(tweet_id, tweet_mode='extended')
                    self._collection += [self._process_tweet(tweet_status._json)]
                    tweet_count += len(new_tweets)
                # TODO: print update status
                max_id = new_tweets[-1].id
            except tweepy.TweepError as e:
                time.sleep(5)
                # TODO: print error status
                print("Twitter Error: {}. Retrying...".format(e))  # TODO: Remove

    @staticmethod
    def _process_tweet(json):
        return json
