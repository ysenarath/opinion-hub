import json
import os
from collections import Counter

page_id = '#AntiRacismSL'

_path = os.path.dirname(os.path.realpath(__file__))

filename = os.path.join(_path, 'output/twitter/{}.json'.format(page_id))

hs_counter = Counter()
mention_counter = Counter()
if __name__ == '__main__':
    with open(filename, 'r') as f:
        content = json.loads(f.read())
        for item in content:
            hs = item['entities']['hashtags']
            for h in hs:
                hs_counter[h['text']] += 1
            ums = item['entities']['user_mentions']
            for um in ums:
                mention_counter[um['screen_name']] += 1
print('Found {} of unique hashtags.'.format(len(hs_counter)))
print('Found {} of unique user mentions.'.format(len(mention_counter)))
# filename = os.path.join(_path, 'output/twitter/fb_{}_hashtags1.txt'.format(page_id))
# with open(filename, 'a', encoding='utf-8') as out:
#     for h, c in hs_counter.most_common():
#         out.write('{}\t{}\n'.format(h, c))
most_common = mention_counter.most_common()
print(most_common)
most_common = hs_counter.most_common()
print(most_common)
