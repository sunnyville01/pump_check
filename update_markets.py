import time
import requests
import json
import urllib.request
from operator import itemgetter


url = 'https://www.coinexchange.io/api/v1/getmarkets'
json_data = requests.get(url).json()['result']

# print(len(json_data)) -- 827

final = []
for item in json_data:
    final.append(item)

with open('markets.json', 'w') as f:
    json_data = json.dump(final, f)
