import requests
from lxml import etree
from tqdm import tqdm

from DnfDeals import settings
from DnfDeals.mysqlconn import Bee

bee = Bee(host=settings.HOST, port=settings.PORT, user=settings.USER, password=settings.PASSWORD, db=settings.DB)


def is_exist(itemnmae):
    sql = "SELECT id from materials where name = %s"
    return bee.read(sql, (itemnmae,))


def attack():
    resp = requests.get(settings.DEALS_URL)
    tree = etree.HTML(resp.content)
    uls = tree.xpath('//div[@id="hotlist"]/div/ul')[1:]
    for i in tqdm(uls):
        itemname = i.xpath('./li[3]/text()')[0]
        if not is_exist(itemname):
            picture = i.xpath('./li[2]/img/@data-lazysrc')[0]
            picture = picture if picture.startswith('http:') else 'http:' + picture
            data = {
                'name': itemname,
                'picture': picture,
                'itemid': i.xpath('./@itemid')[0]
            }
            bee.insert_smart('materials', data)


if __name__ == '__main__':
    attack()
