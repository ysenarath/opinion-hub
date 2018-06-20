import json
from os import listdir
from os.path import dirname, join, realpath

import matplotlib.pyplot as plt
import pandas as pd
from dateutil.parser import parse as date_parse


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


def get_values(values, *attrs):
    if isinstance(values, list):
        temp = values
    else:
        temp = [values]
    for attr in attrs:
        temp = [t[attr] for t in temp]
    return set(temp)


ROOT_PATH = dirname(realpath(__file__))

FACEBOOK_PATH = join(ROOT_PATH, 'output', 'facebook')


def main():
    pages = listdir(FACEBOOK_PATH)
    statuses = []
    for page_fn in pages:
        page_path = join(FACEBOOK_PATH, page_fn)
        status_fns = listdir(page_path)
        for status_fn in status_fns:
            status_path = join(page_path, status_fn)
            with open(status_path, 'r') as f:
                status = json.load(f)
                status['status_published'] = date_parse(status['status_published'])
                status['page'] = page_fn
                for comment in status['comments']:
                    comment['comment_published'] = date_parse(comment['comment_published'])
                statuses += [status]
                # schema = generate_schema(status)

    timeline = []
    for status in statuses:
        page = status['page']
        status_id = status['status_id']
        status_published = status['status_published']
        for comment in status['comments']:
            comment_id = comment['comment_id']
            comment_published = comment['comment_published']
            status_published = status_published.replace(hour=0, minute=0, second=0, microsecond=0)
            comment_published = comment_published.replace(hour=0, minute=0, second=0, microsecond=0)
            timeline += [(page, status_id, comment_id, status_published, comment_published)]
    timeline = pd.DataFrame(timeline,
                            columns=['page', 'status_id', 'comment_id', 'status_published', 'comment_published'])

    # for page in pages:
    #     status_timeline = timeline[timeline.page == page].groupby(['status_published'])['status_id'].count()
    #     x = status_timeline.index.values
    #     y = status_timeline.tolist()
    #     plt.plot(x, y)
    #     plt.show()

    # for page in pages:
    #     comment_timeline = timeline[timeline.page == page].groupby("comment_published")['comment_id'].count()
    #     x = comment_timeline.index.values
    #     y = comment_timeline.tolist()
    #     plt.plot(x, y)
    #     plt.show()

    # comment_timeline = timeline.groupby("comment_published")['comment_id'].count()
    # x = comment_timeline.index.values
    # y = comment_timeline.tolist()
    # plt.plot(x, y)
    # plt.show()

    status_timeline = timeline.groupby("status_published")['comment_id'].count()
    x = status_timeline.index.values
    y = status_timeline.tolist()
    plt.plot(x, y)
    plt.show()


if __name__ == '__main__':
    main()
