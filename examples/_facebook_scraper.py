import errno
import json
import os

from scrapt.feeds import FacebookArchiveFeed

_path = os.path.dirname(os.path.realpath(__file__))

# Not-Done: 'ගොං-ආතල්-gon-athal' tastelessgentlemen'
# Half: 'punchajoke', dadibidiyasl

app_id = ''
app_secret = ''
page_ids = []
until_date = '2018-03-19'
since_date = '2018-01-01'

if __name__ == '__main__':
    for page_id in page_ids:
        fsf = FacebookArchiveFeed([app_id, app_secret], page_id, since_date, until_date)
        fsf.collect()
        custom_id = 10000
        for data in fsf.collection():
            filename = os.path.join(_path, 'output/facebook/{}/{}.json'.format(page_id, custom_id))
            if not os.path.exists(os.path.dirname(filename)):
                try:
                    os.makedirs(os.path.dirname(filename))
                except OSError as exc:  # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise
            with open(filename, 'w', encoding='utf-8') as outfile:
                json.dump(data, outfile)
            custom_id += 1
