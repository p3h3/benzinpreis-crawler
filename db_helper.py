import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool


def init_db(mysql_user, mysql_password, mysql_host, mysql_database):
    print("INFO: Opening database..")
    try:
        db_pool = MySQLConnectionPool(user=mysql_user, password=mysql_password,
                                      host=mysql_host,
                                      database=mysql_database,
                                      pool_size=10)

        if db_pool.get_connection().is_connected():
            print("INFO: Opened database!")
            return db_pool
        else:
            print("ERROR: Connection opened, but closed immediately!")

    except KeyboardInterrupt:
        print("ERROR: Can't open database!")
        exit()

    return


class DbHelper:
    def __init__(self, mysql_user, mysql_password, mysql_host, mysql_database):

        db_pool = init_db(mysql_user, mysql_password, mysql_host, mysql_database)

        self.db_pool = db_pool

    # getting latest historic data
    def get_latest_historic_data(self, number):
        # getting db connector and cursor from connection pool
        db_connector = self.db_pool.get_connection()
        db_cursor = db_connector.cursor()
        # check for valid db connection
        if not db_connector.is_connected():
            return

        try:
            # Collect some data
            db_cursor.execute("select `time`, `price` from " +
                              "kraftstoffpreise.diesel " +
                              "where address='Leipziger Str. 327' " +
                              "order by id desc limit " + str(number) + ";")
            # get data from db_connector
            data = db_cursor.fetchall()
            db_connector.commit()

            # closing opened pool connection
            db_connector.close()

            return data
        except mysql.connector.Error:
            return

    # getting latest historic data
    def get_offset_historic_data(self, number, offset):
        # getting db connector and cursor from connection pool
        db_connector = self.db_pool.get_connection()
        db_cursor = db_connector.cursor()
        # check for valid db connection
        if not db_connector.is_connected():
            return

        try:
            # Collect some data
            db_cursor.execute("select `time`, `price` from " +
                              "kraftstoffpreise.supere10 " +
                              "where address='Leipziger Str. 327' " +
                              "order by id desc limit " + str(number) +
                              " offset " + str(offset) + ";")
            # get data from db_connector
            data = db_cursor.fetchall()
            db_connector.commit()

            # closing opened pool connection
            db_connector.close()

            return data

        except mysql.connector.Error:
            return

    def insert_datapoint(self, dataframe, type, db_name):
        # getting db connector and cursor from connection pool
        try:
            db_connector = self.db_pool.get_connection()
            db_cursor = db_connector.cursor()
            # obviously the sql query to insert new dataframe into db
            query = "INSERT INTO `" + db_name + "`.`" \
                    + type \
                    + "` (`name`, `address`, `time`, `price`) " \
                      "VALUES (%s, %s, %s, %s) on duplicate key update `name`=(%s)"
            values = (dataframe["name"], dataframe["address"], dataframe["time"], dataframe["price"], dataframe["time"])

            try:
                # trying to execute query
                db_cursor.execute(query, values)
                db_connector.commit()

                # closing opened pool connection
                db_connector.close()

            except KeyboardInterrupt:
                print("ERROR: while executing database insert query")

            except mysql.connector.errors.IntegrityError as e:
                print("ERROR: " + str(e))

        except mysql.connector.errors.PoolError:
            print("ERROR: Pool exhausted.. trying again in 000ms")
            # sleep(.2)
            self.insert_datapoint(dataframe, type, db_name)  # trying again recursively

    # closing all connections
    def close_connection(self):
        print("Closing connection")
