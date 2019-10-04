import pymysql.cursors


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
                                     port=self.port)
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
        finally:
            connection.close()
            return result
