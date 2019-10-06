from DnfDeals import core, update_materials, sentry

if __name__ == '__main__':
    print('开始更新材料数据')
    update_materials.attack()
    print('\n开始更新昨天价格数据')
    core.attact()
    print('\n开始分析数据并发送邮件')
    sentry.attack()
