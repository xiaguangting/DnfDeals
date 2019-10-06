import json
import re

import requests
from tqdm import tqdm

from DnfDeals import settings
from DnfDeals.mysqlconn import Bee

bee = Bee(host=settings.HOST, port=settings.PORT, user=settings.USER, password=settings.PASSWORD, db=settings.DB)


def is_exist(materials_id, local_time):
    sql = "SELECT id FROM statistics WHERE materials_id = %s AND local_time = %s"
    return bee.read(sql, (materials_id, local_time))


def attact(is_yesterday=True):
    sql = 'SELECT id, name, itemid FROM materials'
    result = bee.read(sql, [])
    is_finish = False
    for i in tqdm(result):
        materials_id = i.get('id')
        itemamt, price, maxprice, minprice, local_time = 0, 0, 0, 0, None
        area_list = settings.HUBEI + settings.HUNAN
        for j in area_list:
            url = settings.MATERIALS_URL.format(i.get('itemid'), j)
            resp = requests.get(url)
            pattern = 'var pricelist = (\[.*\]);'
            result = re.findall(pattern, resp.text)
            data = json.loads(result[0])

            yesterday_data = data[-1]
            local_time = yesterday_data.get('time')
            if is_exist(materials_id, local_time):
                is_finish = True
                break

            itemamt += int(yesterday_data['itemamt'])
            price += int(str(yesterday_data['price']).split('.')[0])
            maxprice_tmp = int(str(yesterday_data['maxprice']).split('.')[0])
            if maxprice < maxprice_tmp:
                maxprice = maxprice_tmp
            minprice_tmp = int(str(yesterday_data['minprice']).split('.')[0])
            if minprice > minprice_tmp or minprice == 0:
                minprice = minprice_tmp

        if is_finish:
            is_finish = False
            continue

        price = price // len(area_list)
        # print(i['name'], itemamt, price, maxprice, minprice, local_time)
        insert_data = {
            'materials_id': materials_id,
            'itemamt': itemamt,
            'price': price,
            'maxprice': maxprice,
            'minprice': minprice,
            'local_time': local_time
        }
        bee.insert_smart('statistics', insert_data)


if __name__ == '__main__':
    attact()
