from DnfDeals import core, update_materials, sentry, utils

if __name__ == '__main__':
    execute_list = [update_materials.attack, core.attact, sentry.attack]
    for i in execute_list:
        try:
            i()
        except Exception as e:
            import traceback, sys
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error = str(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))
            utils.send_email('程序发生了异常', error)
            continue
