import json
import re

import requests

import settings
from mysqlconn import Bee

bee = Bee(host=settings.HOST, port=settings.PORT, user=settings.USER, password=settings.PASSWORD, db=settings.DB)


def is_exist(materials_id, local_time):
    sql = "SELECT id FROM statistics WHERE materials_id = %s AND local_time = %s"
    return bee.read(sql, (materials_id, local_time))


def attact(is_yesterday=True):
    sql = 'SELECT id, name, itemid FROM materials'
    result = bee.read(sql, [])
    for i in result:
        url = 'https://bang.qq.com/app/dnf/acution/actiondetail?itemid=%s&serverId=%s' % (i.get('itemid'), 24)
        resp = requests.get(url)
        pattern = 'var pricelist = (\[.*\]);'
        result = re.findall(pattern, resp.text)
        data = json.loads(result[0])
        if is_yesterday:
            data = data[-1:]
        for j in data:
            materials_id = i.get('id')
            local_time = j.get('time')
            if not is_exist(materials_id, local_time):
                insert_data = {
                    'materials_id': materials_id,
                    'itemamt': j.get('itemamt'),
                    'price': str(j.get('price')).split('.')[0],
                    'maxprice': str(j.get('maxprice')).split('.')[0],
                    'minprice': str(j.get('minprice')).split('.')[0],
                    'local_time': local_time
                }
                bee.insert_smart('statistics', insert_data)


if __name__ == '__main__':
    attact()
