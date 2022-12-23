import mysql.connector
from mysql.connector import Error
from decouple import config


user = config("user")
password = config("password")
host = config("host")
database = config("database")


class Conexao:
    try:
        def __init__(self):
            self.con_mysql = mysql.connector.connect(host=host,
                                              user=user,
                                              password=password,
                                              database=database)
    except Error as E:
        print(E)