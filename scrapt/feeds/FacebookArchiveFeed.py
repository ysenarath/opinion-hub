import datetime
import json
import time

from scrapt.feeds.__abc import ArchiveFeed
from scrapt.utils import unicode_decode

try:
    from urllib2 import urlopen, Request
except ImportError:
    from urllib.request import urlopen, Request


class FacebookArchiveFeed(ArchiveFeed):
    STATUS_HEADER = ["status_id", "status_message", "link_name", "status_type", "status_link", "status_published",
                     "num_reactions", "num_comments", "num_shares", "num_likes", "num_loves", "num_wows", "num_hahas",
                     "num_sads", "num_angrys", "num_special"]

    COMMENT_HEADER = ["comment_id", "status_id", "parent_id", "comment_message", "comment_author",
                      "comment_published", "num_reactions", "num_likes", "num_loves", "num_wows",
                      "num_hahas", "num_sads", "num_angrys", "num_special"]

    STATUS_FIELDS = "&fields=message,link,created_time,type,name,id,comments.limit(0).summary(true),shares," \
                    "reactions.limit(0).summary(true)"

    COMMENT_FIELDS = "&fields=id,message,reactions.limit(0).summary(true)" + \
                     ",created_time,comments,from,attachment"

    def __init__(self, access_token, page_id, since_date, until_date, limit=100):
        """
        Cstr
        :param access_token: Facebook access token format tuple(app_id, app_secret)
        :param page_id:
        :param since_date:
        :param until_date:
        :type limit:
        """
        super(FacebookArchiveFeed, self).__init__()
        # Authentication & Authorization
        self._access_token = '{}|{}'.format(*access_token)
        # Query parameters
        self._page_id = page_id
        self._since_date = since_date
        self._until_date = until_date
        self._limit = limit
        # Link properties based on limit and access token parameters
        self._base = "https://graph.facebook.com/v2.9"  # URL base
        self._parameters = "/?limit={}&access_token={}".format(self._limit, self._access_token)

    def collect(self):
        has_next_page = True
        num_processed = 0
        scrape_start_time = datetime.datetime.now()
        after = ''
        node = "/{}/posts".format(self._page_id)
        since = "&since={}".format(self._since_date) if self._since_date is not '' else ''
        until = "&until={}".format(self._until_date) if self._until_date is not '' else ''
        # TODO: print update status
        while has_next_page:
            after = '' if after is '' else "&after={}".format(after)
            base_url = self._base + node + self._parameters + after + since + until
            # Create url and request information see http://stackoverflow.com/a/37239851 for Reactions parameters
            url = base_url + FacebookArchiveFeed.STATUS_FIELDS
            statuses = json.loads(self.request_until_succeed(url))
            reactions = self.get_reactions(base_url)
            # Process and format data
            for status in statuses['data']:
                # Ensure it is a status with the expected metadata
                if 'reactions' in status:
                    status_data = self.process_status(status)
                    reactions_data = reactions[status_data[0]]
                    # calculate thankful/pride through algebra
                    num_special = status_data[6] - sum(reactions_data)
                    status = {t: v for t, v in
                              zip(FacebookArchiveFeed.STATUS_HEADER, status_data + reactions_data + (num_special,))}
                    status['comments'] = self._collect_comments(status)
                    self._collection += [status]
                num_processed += 1
                # TODO: print update status
            # if there is no next page, we're done.
            if 'paging' in statuses:
                after = statuses['paging']['cursors']['after']
            else:
                has_next_page = False
        # TODO: print update status

    def _collect_comments(self, status):
        num_processed = 0
        after = ''
        has_next_page = True
        comment_lst = []
        while has_next_page:
            node = "/{}/comments".format(status['status_id'])
            after = '' if after is '' else "&after={}".format(after)
            base_url = self._base + node + self._parameters + after
            url = base_url + self.COMMENT_FIELDS
            comments = json.loads(self.request_until_succeed(url))
            reactions = self.get_reactions(base_url)
            for comment in comments['data']:
                comment_data = self.process_comments(comment, status['status_id'])
                reactions_data = reactions[comment_data[0]]
                # calculate thankful/pride through algebra
                num_special = comment_data[6] - sum(reactions_data)
                comment_lst += [
                    {t: v for t, v in zip(self.COMMENT_HEADER, (comment_data + reactions_data + (num_special,)))}]

                if 'comments' in comment:
                    has_next_subpage = True
                    sub_after = ''

                    while has_next_subpage:
                        sub_node = "/{}/comments".format(comment['id'])
                        sub_after = '' if sub_after is '' else "&after={}".format(
                            sub_after)
                        sub_base_url = self._base + sub_node + self._parameters + sub_after

                        sub_url = sub_base_url + self.COMMENT_FIELDS
                        sub_comments = json.loads(self.request_until_succeed(sub_url))
                        sub_reactions = self.get_reactions(sub_base_url)

                        for sub_comment in sub_comments['data']:
                            sub_comment_data = self.process_comments(sub_comment, status['status_id'],
                                                                     comment['id'])
                            sub_reactions_data = sub_reactions[sub_comment_data[0]]
                            num_sub_special = sub_comment_data[6] - sum(sub_reactions_data)
                            comment_lst += [
                                {t: v for t, v in
                                 zip(self.COMMENT_HEADER,
                                     (sub_comment_data + sub_reactions_data + (num_sub_special,)))}]

                            num_processed += 1
                        if 'paging' in sub_comments:
                            if 'next' in sub_comments['paging']:
                                sub_after = sub_comments[
                                    'paging']['cursors']['after']
                            else:
                                has_next_subpage = False
                        else:
                            has_next_subpage = False
                # TODO: print update status
                num_processed += 1
            if 'paging' in comments:
                if 'next' in comments['paging']:
                    after = comments['paging']['cursors']['after']
                else:
                    has_next_page = False
            else:
                has_next_page = False
        return comment_lst

    @staticmethod
    def get_reactions(base_url):
        """
        Collects reactions for the given base url
        :param base_url: base url to collect reactions
        :return: a dict of reaction status
        """
        reaction_types = ['like', 'love', 'wow', 'haha', 'sad', 'angry']
        reactions_dict = {}  # dict of {status_id: tuple<6>}
        for reaction_type in reaction_types:
            fields = "&fields=reactions.type({}).limit(0).summary(total_count)".format(reaction_type.upper())
            url = base_url + fields
            data = json.loads(FacebookArchiveFeed.request_until_succeed(url))['data']  # definded function
            data_processed = set()  # set() removes rare duplicates in statuses
            for status in data:
                id = status['id']
                count = status['reactions']['summary']['total_count']
                data_processed.add((id, count))
            for id, count in data_processed:
                if id in reactions_dict:
                    reactions_dict[id] = reactions_dict[id] + (count,)
                else:
                    reactions_dict[id] = (count,)
        return reactions_dict

    @staticmethod
    def process_comments(comment, status_id, parent_id=''):
        comment_id = comment['id']
        comment_message = '' if 'message' not in comment or comment['message'] is '' else unicode_decode(
            comment['message'])
        comment_author = '' if 'from' not in comment else unicode_decode(comment['from']['name'])
        num_reactions = 0 if 'reactions' not in comment else comment['reactions']['summary']['total_count']
        if 'attachment' in comment:
            attachment_type = comment['attachment']['type']
            attachment_type = 'gif' if attachment_type == 'animated_image_share' else attachment_type
            attach_tag = "[[{}]]".format(attachment_type.upper())
            comment_message = attach_tag if comment_message is '' else comment_message + " " + attach_tag
        # Time needs special care since a) it's in UTC and b) it's not easy to use in statistical programs.
        comment_published = datetime.datetime.strptime(comment['created_time'], '%Y-%m-%dT%H:%M:%S+0000')
        comment_published = comment_published + datetime.timedelta(hours=-5)  # EST
        comment_published = comment_published.strftime('%Y-%m-%d %H:%M:%S')  # best time format for spreadsheet programs
        # Return a tuple of all processed data
        return (comment_id, status_id, parent_id, comment_message,
                comment_author, comment_published, num_reactions)

    @staticmethod
    def process_status(status):
        status_id = status['id']
        status_type = status['type']
        status_message = '' if 'message' not in status else unicode_decode(status['message'])
        link_name = '' if 'name' not in status else unicode_decode(status['name'])
        status_link = '' if 'link' not in status else unicode_decode(status['link'])
        # Time needs special care since a) it's in UTC and b) it's not easy to use in statistical programs.
        status_published = datetime.datetime.strptime(status['created_time'], '%Y-%m-%dT%H:%M:%S+0000')
        status_published = status_published + datetime.timedelta(hours=-5)  # EST
        status_published = status_published.strftime('%Y-%m-%d %H:%M:%S')  # best time format for spreadsheet programs
        # Nested items require chaining dictionary keys.
        num_reactions = 0 if 'reactions' not in status else status['reactions']['summary']['total_count']
        num_comments = 0 if 'comments' not in status else status['comments']['summary']['total_count']
        num_shares = 0 if 'shares' not in status else status['shares']['count']
        return (status_id, status_message, link_name, status_type, status_link,
                status_published, num_reactions, num_comments, num_shares)

    @staticmethod
    def request_until_succeed(url):
        """
        Request until success
        :param url:
        :return:
        """
        req = Request(url)
        while True:
            try:
                response = urlopen(req)
                if response.getcode() == 200:
                    break
            except Exception as e:
                time.sleep(5)
                # TODO: print update status
                print("Service Error: {}. Retrying...".format(e))  # TODO: Remove
        return response.read()
