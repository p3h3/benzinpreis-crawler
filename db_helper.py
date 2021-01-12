import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool

def init_db(mysql_user, mysql_password, mysql_host, mysql_database):
    print("INFO: Opening database..")
    try:
        db_pool = MySQLConnectionPool(user=mysql_user, password=mysql_password,
                                      host=mysql_host,
                                      database=mysql_database,
                                      pool_size=32)

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

    def insert_datapoint(self, dataframe, trade_pair):
        # getting db connector and cursor from connection pool
        try:
            db_connector = self.db_pool.get_connection()
            db_cursor = db_connector.cursor()
            # obviously the sql query to insert new dataframe into db
            query = "INSERT INTO `astrotrader`.`" \
                    + trade_pair \
                    + "` (`epochtime`, `timeinterval`, `open`, `close`, `high`, `low`, `change`, `volume`) " \
                      "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) on duplicate key update `epochtime`=(%s)"
            values = (dataframe["time"], dataframe["t"], dataframe["o"], dataframe["c"], dataframe["h"], dataframe["l"],
                      (float(dataframe["c"]) / float(dataframe["o"])) - 1, dataframe["v"], dataframe["time"])

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
            #sleep(.2)
            self.insert_datapoint(dataframe, trade_pair)  # trying again recursively

    # closing all connections
    def close_connection(self):
        print("Closing connection")