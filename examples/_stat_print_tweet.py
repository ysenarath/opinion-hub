import json
import re
from os import listdir
from os.path import dirname, realpath, join

import pandas as pd

ROOT_PATH = dirname(realpath(__file__))

TWITTER_PATH = join(ROOT_PATH, 'output', 'twitter')

URI_RE = r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))'
MENTIONS_RE = r'@\w+'
NUMBER_RE = r'([0-9]+(\.[0-9]+)?)|(\.[0-9]+)'


def get_values(values, *attrs):
    if isinstance(values, list):
        temp = values
    else:
        temp = [values]
    for attr in attrs:
        temp = [t[attr] for t in temp]
    return set(temp)


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


def preprocess(text):
    text = re.sub(URI_RE, '[LINK]', text)
    text = re.sub(MENTIONS_RE, '[MENTION]', text)
    text = re.sub(NUMBER_RE, '[NUMBER]', text)
    return text


def main():
    schema = dict()
    results_all = []
    queries_fns = listdir(TWITTER_PATH)
    data = []
    for query in queries_fns:
        results_fn = join(TWITTER_PATH, query)
        with open(results_fn, 'r') as f:
            results = json.load(f)
            results_all += results
            for result in results:
                rschema = generate_schema(result)
                schema.update(rschema)
                id = result['id']
                created_at = result['created_at']
                text = result['full_text']
                retweeted = text.startswith('RT')
                clean_text = preprocess(text)
                lang = result['lang']
                data += [(id, text, clean_text, retweeted, created_at, query, lang)]
    df = pd.DataFrame(data, columns=['id', 'text', 'clean_text', 'retweet', 'created_at', 'query', 'lang'])
    for q in df['query'].unique():
        dfq = df[df['query'] == q]
        dfq = dfq[dfq.retweet == False]
        unique_text = dfq.clean_text.unique()
        text = dfq.text.unique()
        si_tw = dfq[dfq.lang == 'si']
        si_tw_unique_text = si_tw.clean_text.unique()
        si_tw_text = si_tw.text.unique()
        en_tw = dfq[dfq.lang == 'en']
        en_tw_unique_text = en_tw.clean_text.unique()
        en_tw_text = en_tw.text.unique()
        # print(en_tw_text, flush=True)
        # print('SI_{}\t\t{}\t{}\t{}\t{}\t{}\t{}'.format(q, len(text), len(unique_text), len(si_tw_text), len(si_tw_unique_text), len(en_tw_text), len(en_tw_unique_text)))
    unique_text = df.clean_text.unique()
    text = df.text.unique()
    print(text[1058])
    print('{}\t{}\t{}'.format('all', len(text), len(unique_text)))


if __name__ == '__main__':
    main()
