import json
from os.path import dirname, join, realpath

from os import listdir
from pprint import pprint


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
                statuses += [status]
                schema = generate_schema(status)
    pprint(get_values(statuses, 'status_type'))
    # {'photo', 'link', 'video', 'status'}


if __name__ == '__main__':
    main()
