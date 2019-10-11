import logging
import smtplib
from email.mime.text import MIMEText
from logging.handlers import TimedRotatingFileHandler

import pymysql

from DnfDeals import settings


def send_email(subject, content):
    message = MIMEText(content, 'html', 'utf-8')
    message['From'] = "DnfDeals<%s>" % settings.EMAIL_ADDRESS
    message['To'] = ','.join(settings.ACCEPT_EMAIL_list)
    message['Subject'] = subject

    smtpObj = smtplib.SMTP_SSL(settings.EMAIL_SMTP_SERVER, 465)
    smtpObj.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
    smtpObj.sendmail(settings.EMAIL_ADDRESS, settings.ACCEPT_EMAIL_list, message.as_string('utf-8'))
    smtpObj.quit()


hunter = logging.Logger(name='hunter')

handler = TimedRotatingFileHandler(filename=settings.LOG_ADDRESS, when='D', backupCount=30)
hunter.addHandler(handler)


class Bee(object):
    def __init__(self, host, port, user, password, db, charset='utf8mb4'):
        self.host = host
        self.user = user
        self.password = password
        self.db = db
        self.charset = charset
        self.port = port

    def start_conn(self):
        # Connect to the database
        connection = pymysql.connect(host=self.host,
                                     user=self.user,
                                     password=self.password,
                                     db=self.db,
                                     charset=self.charset,
                                     cursorclass=pymysql.cursors.DictCursor,
                                     port=int(self.port))
        return connection

    def insert(self, sql, paras):
        connection = self.start_conn()
        try:
            with connection.cursor() as cursor:
                # Create a new record
                cursor.execute(sql, paras)
            connection.commit()
        finally:
            connection.close()

    def insert_smart(self, tablename, data):
        field_name_list = []
        field_value_list = []
        for i, j in data.items():
            field_name_list.append(i)
            field_value_list.append(j)
        sql = "INSERT INTO %s (id, %s) VALUES (0, %s)" % (
            tablename, ','.join(field_name_list), ','.join(['%s' for i in range(len(field_name_list))]))
        self.insert(sql, field_value_list)

    def read(self, sql, paras):
        # Read a single record
        connection = self.start_conn()
        try:
            result = None
            with connection.cursor() as cursor:
                cursor.execute(sql, paras)
                result = cursor.fetchall()
            connection.commit()
        finally:
            connection.close()
            return result
