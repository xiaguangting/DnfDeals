# 负责对每天数据分析，并将结果以邮件形式发出
import smtplib
from email.header import Header
from email.mime.text import MIMEText

from tqdm import tqdm

from DnfDeals import settings
from DnfDeals.mysqlconn import Bee

bee = Bee(host=settings.HOST, port=settings.PORT, user=settings.USER, password=settings.PASSWORD, db=settings.DB)


def get_content():
    sql = 'SELECT id, name, itemid FROM materials'
    result = bee.read(sql, [])
    email_content = '<table align="center" border="1" cellspacing="0" style="text-align:center;width: 1000px"><tr><th>材料名称</th><th>交易量涨幅</th><th>价格涨幅</th><th>一天内价格涨幅</th></tr>'
    result_set = []
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
            result_set.append([i['name'], itemamt_rate, price_rate, one_day_price_rate])

    for i in sorted(result_set, key=lambda x: x[1], reverse=True):
        line_content = '<tr><td>' + '</td><td>'.join([i[0], str(i[1]) + '%', str(i[2]) + '%',
                                                      str(i[3]) + '%']) + '</td></tr>'
        email_content += line_content
    email_content += '</table>'
    return email_content


def email_send(content=''):
    message = MIMEText(content, 'html', 'utf-8')
    message['From'] = "DnfDeals<%s>" % settings.EMAIL_ADDRESS
    message['To'] = ','.join(settings.ACCEPT_EMAIL_list)
    message['Subject'] = Header('Dnf拍卖行材料价格分析表', 'utf-8')

    smtpObj = smtplib.SMTP()
    smtpObj.connect(settings.EMAIL_SMTP_SERVER)
    smtpObj.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
    smtpObj.sendmail(settings.EMAIL_ADDRESS, settings.ACCEPT_EMAIL_list, message.as_string('utf-8'))


def attack():
    email_content = get_content()
    email_send(email_content)


if __name__ == '__main__':
    attack()
