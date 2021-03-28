import requests
import json
import csv
import os
import time
import logging
import sys
from datetime import datetime

time_delay = 2
data_file = 'data.csv'
url = 'https://front.wegobuy.com/shoppingguide/sale-daily-new?count='
num_items = 15
row_names = ['id', 'goodsId', 'goodsPicUrl', 'goodsTitle', 'goodsLink', 'goodsPrice', 'buyerId', 'buyerName', 'orderState', 'goodsOrderTime', 'status', 'createTime', 'updateTime', 'buyerAvatar', 'userLevel', 'userLevelType', 'currencySymbol', 'userName', 'timeName', 'countryCode', 'statePicUrl']

if not os.path.isdir('logs'):
    os.mkdir('logs')

log_file = 'logs\{:%Y_%m_%d_%H}.log'.format(datetime.now())
log_format = u'%(asctime)s | %(levelname)-8s | %(message)s'
logger = logging.getLogger('WegobuyWatcher')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(log_file, encoding='utf-8')
formatter = logging.Formatter(log_format)
handler.setFormatter(formatter)
logger.addHandler(handler)
printer = logging.StreamHandler(sys.stdout)
printer.setLevel(logging.DEBUG)
printer.setFormatter(formatter)
logger.addHandler(printer)

def watch():
    logger.info('**** STARTING WATCHER ****')
    logger.info(
        f'Program settings: time_delay: {time_delay}, data_file: {data_file}, num_items: {num_items}, log_file: {log_file}')
    if not os.path.isfile(data_file):
        with open(data_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(row_names)
            logger.info(f'Data file {data_file} not found, created it with row names {row_names}')
    old_ids = []
    with open(data_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            old_ids.append(row['id'])
        logger.info(f'Read {len(old_ids)} ids from {data_file}')
    logger.info('Starting main loop...')
    while True:
        response = requests.get(url + str(num_items))
        response = json.loads(response.text.encode('utf-8'))
        curr_data = response['data']
        curr_data = [{k: str(v) for k, v in c.items()} for c in curr_data]
        for c in list(curr_data):
            if c['id'] in old_ids:
                curr_data.remove(c)
            else:
                old_ids.append(c['id'])
        if len(curr_data) > 0:
            with open(data_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, row_names)
                writer.writerows(curr_data)
                logger.info(f'Wrote the following to {data_file}: {curr_data}')
        else:
            logger.info('No new items found')
        time.sleep(time_delay)

if __name__ == '__main__':
    try:
        watch()
    except:
        logger.exception('ERROR')
