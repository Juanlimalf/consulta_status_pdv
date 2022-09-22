import mysql.connector
from mysql.connector import Error
import sqlalchemy as db

class Conexao:
    try:
        def __init__(self):
            self.con_mysql = mysql.connector.connect(host="nagumo-labs.ccnxv4osz7rv.us-east-1.rds.amazonaws.com",
                                              user="admin",
                                              password="n4gum0L4bs",
                                              database="pdv_carga")
    except Error as E:
        print(E)