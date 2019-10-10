from DnfDeals import settings
from DnfDeals.mysqlconn import Bee

from matplotlib import pyplot as plt

bee = Bee(host=settings.HOST, port=settings.PORT, user=settings.USER, password=settings.PASSWORD, db=settings.DB)


def action(name):
    sql = 'SELECT price, itemamt, local_time FROM statistics WHERE materials_id in (SELECT id FROM materials WHERE ' \
          'name = %s) ORDER BY local_time'
    result = bee.read(sql, [name])
    x, y1, y2 = [], [], []
    for i in result:
        x.append(i['local_time'])
        if i['price'] == 0:
            if len(y1) > 0:
                y1.append(y1[-1])
            else:
                y1.append(0)
        else:
            y1.append(i['price'])
        if i['itemamt'] == 0:
            if len(y2) > 0:
                y2.append(y2[-1])
            else:
                y2.append(0)
        else:
            y2.append(i['itemamt'])

    # plt.figure(figsize=(16, 9))
    ax1 = plt.subplot(2, 1, 1)
    ax2 = plt.subplot(2, 1, 2)

    plt.sca(ax1)
    plt.title('Price Chart')
    plt.plot(x, y1, color='red')
    plt.xticks(rotation=45)

    plt.sca(ax2)
    plt.title('Amount Chart')
    plt.plot(x, y2, color='green')
    plt.xticks(rotation=45)

    plt.show()


if __name__ == '__main__':
    name = '深渊派对挑战书'
    action(name)
