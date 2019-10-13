# 负责对每天数据分析，并将结果以邮件形式发出
import datetime

from tqdm import tqdm

from DnfDeals import settings, utils


bee = utils.Bee(host=settings.HOST, port=settings.PORT, user=settings.USER, password=settings.PASSWORD, db=settings.DB)


def price_show(price):  # 将价格数字按照三位一逗号显示
    price_str = str(price)
    price_len = len(price_str)
    if price_len > 3:
        price_len_cm = price_len % 3
        price_show_list = []
        if price_len_cm > 0:
            price_show_list.append(price_str[:price_len_cm])
        for j in range((price_len - price_len_cm) // 3):
            head_index = price_len_cm + j * 3
            price_show_list.append(price_str[head_index: head_index + 3])
        price2 = ','.join(price_show_list)
    else:
        price2 = str(price)
    return price2


def get_content():
    # 获取昨天的时间
    yesterday = str(datetime.date.today() - datetime.timedelta(days=1)).replace('-', '')
    sql = 'SELECT m.id, m.name, m.itemid FROM materials m JOIN statistics s on m.id = s.materials_id WHERE ' \
          's.itemamt > 10000 AND s.local_time = %s' % yesterday
    result = bee.read(sql, [])
    email_content = '<table align="center" border="1" cellspacing="0" style="text-align:center;width: 1000px" ' \
                    'summary="交易量大于1w的材料"><caption>{0}分析表</caption><tr><th>序号</th><th>材料名称</th>' \
                    '<th>价格</th><th>交易量涨幅</th><th>价格涨幅</th><th>一天内价格涨幅</th></tr>'.format(yesterday)
    result_set = []
    print('Run analyze')
    for i in tqdm(result):
        sql2 = 'SELECT itemamt, price, maxprice, minprice, local_time FROM statistics WHERE materials_id = %s ' \
               'ORDER BY local_time DESC LIMIT 2'
        result2 = bee.read(sql2, [i['id']])
        if len(result2) == 2:
            yesterday, before_yesterday = result2[0], result2[1]
            # 昨天的交易量相比前天的涨幅
            if before_yesterday['itemamt'] != 0:
                itemamt_rate = round((yesterday['itemamt'] - before_yesterday['itemamt']) / before_yesterday['itemamt'] * 100, 2)
            else:
                itemamt_rate = 0
            # 昨天的价格相比前天的涨幅
            if before_yesterday['price'] != 0:
                price_rate = round((yesterday['price'] - before_yesterday['price']) / before_yesterday['price'] * 100, 2)
            else:
                price_rate = 0
            # 昨天一天最低价到最高价的涨幅
            if yesterday['minprice'] != 0:
                one_day_price_rate = round((yesterday['maxprice'] - yesterday['minprice']) / yesterday['minprice'] * 100, 2)
            else:
                one_day_price_rate = 0
            result_set.append([i['name'], yesterday['price'], itemamt_rate, price_rate, one_day_price_rate])

    index = 0
    for i in sorted(result_set, key=lambda x: x[2], reverse=True):
        index += 1
        # print(price_show(i[1]), i[1])
        line_content = '<tr><td>' + '</td><td>'.join([str(index), i[0], price_show(i[1]), str(i[2]) + '%', str(i[3]) + '%',
                                                      str(i[4]) + '%']) + '</td></tr>'
        email_content += line_content
    email_content += '</table>'
    return email_content


def attack():
    email_content = get_content()
    utils.send_email('Dnf拍卖行材料价格分析', email_content)


if __name__ == '__main__':
    attack()
