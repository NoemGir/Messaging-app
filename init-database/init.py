# if the database isn't initialized with the correct table and data, create the missing tables

import mysql.connector
from mysql.connector import errorcode
import os

user = os.environ['MYSQL_USER']
password = os.environ['MYSQL_PASSWORD']
host = os.environ['MYSQL_SERVER_NAME']
database = os.environ['MYSQL_DATABASE']
port = os.environ['MYSQL_PORT']


config = {
  'user':user,
  'password': password,
  'host': host,
  'port': port,
  'database':database,
  'raise_on_warnings': True,
  "connect_timeout": 180,
}


TABLES = {}

TABLES['clients'] = (
    "CREATE TABLE IF NOT EXISTS clients ("
    "client_id INT auto_increment,"
    "client_name VARCHAR(10),"
    "PRIMARY KEY(`client_id`));")

TABLES['subbed'] = (
    "CREATE TABLE IF NOT EXISTS subbed ("
    "sub_name VARCHAR(10) NOT NULL,"
    "client_id INT NOT NULL,"
    "PRIMARY KEY(`sub_name`, `client_id`));")

# Add the tables to the database
def add_tables(cursor, TABLES):
    for table_name in TABLES:
        table_description = TABLES[table_name]
        try:
            print("Creating table {}: ".format(table_name), end='')
            cursor.execute(table_description)
            if(table_name != "subbed"):
                alter_table(cursor, table_name)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print(err.msg)
        else:
            print("OK")

# alter the table to get the autoincrement ( only if the tables don't already exists)
def alter_table(cursor, tableName):
    if tableName in TABLES:
        sql = "ALTER TABLE " + tableName + " AUTO_INCREMENT=0;"
        try:
            print("ALter table {}: ".format(tableName), end='')
            cursor.execute(sql)
        except mysql.connector.Error as err:
                print(err.msg)
        else:
            print("OK")
    else:
        print("table does not exists")

# when connected, go to the right database and run the creation of the tables
def modify_tables():
    cursor = conn.cursor()
    try:
        cursor.execute("USE {}".format(database))
    except mysql.connector.Error as err:
        print("Database {} does not exists.".format(database))
    else:
        add_tables(cursor, TABLES)

#connection
try:
  conn = mysql.connector.connect(**config)
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with your user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err)
else: 
    modify_tables()
    conn.close()

