from scrapt.feeds.__abc import StreamFeed


class TwitterStreamFeed(StreamFeed):
    def __init__(self):
        super(TwitterStreamFeed, self).__init__()

    def stream(self):
        pass
