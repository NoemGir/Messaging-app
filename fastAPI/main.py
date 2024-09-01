from fastapi import FastAPI, HTTPException, Form
from pydantic import BaseModel, Field # pydantic : création et définition d'objets
import logging
from fastapi.middleware.cors import CORSMiddleware
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

# Configurer les logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Client(BaseModel):
    id : int  = Field(description ="Id of the client")
    name : str = Field(description ="Name of the client")
    subscriptions : list[str] = Field(description ="Subscriptions of the client")

def selectInDatabase(sql):
    [conn, cursor] = connect()
    try:
        print("command : {} : ".format(sql), end='')
        cursor.execute(sql)
    except mysql.connector.Error as err:
            conn.close()
            raise HTTPException(status_code=400, detail=err.msg)
    else:
        print("OK")
        data = cursor.fetchall()
        conn.close()
        return  data

def modifyDatabase(sql, val):
    [conn, cursor] = connect()
    try:
        print("command : {} : ".format(sql))
        print("variables : {} : ".format(val))
        cursor.execute(sql, val)
        conn.commit()
    except mysql.connector.Error as err:
            conn.close()
            raise HTTPException(status_code=400, detail=err.msg)
    else:
        conn.close()

# return the list of subscriptions of the gicen client
def getClientSubs(idClient) -> list[str]:
    sql = f"SELECT sub_name FROM subbed WHERE subbed.client_id={idClient};"
    data = selectInDatabase(sql)
    return [sub_name for (sub_name,) in data]
        
#return the list of clients and their informations
def getClientsList() -> list[Client]:
        sql = "SELECT * FROM clients;"
        data = selectInDatabase(sql)
        result = [ Client( id = id, name = name, subscriptions = getClientSubs(id)) for [id, name] in data]
        return  result

#return the informations of a specific client
def getClientInfos(idClient) -> Client :
    sql = f"SELECT * FROM clients WHERE clients.client_id={idClient};"
    data = selectInDatabase(sql)
    if(len(data) != 1):
        raise HTTPException(status_code=400, detail=f"No data for client id {idClient}")
    else:
        client = data[0]
        return  Client(id=client[0], name=client[1], subscriptions=getClientSubs(idClient) )

# add a client in the database
def addClient(client_name) :
    sql = "INSERT INTO clients (client_name) VALUES  (%s)"
    val = [client_name]
    modifyDatabase(sql, val)

# delete a client from the database
def deleteClient(client_id) :
    sql = "DELETE FROM subbed WHERE client_id = %s"
    modifyDatabase(sql, [client_id])
    sql = "DELETE FROM clients WHERE client_id = %s"
    modifyDatabase(sql, [client_id])

# add a subscription to the indicated client
def addSubscription(client_id, sub_name) :
    sql = "INSERT INTO subbed (sub_name, client_id) VALUES  (%s, %s)"
    val = [sub_name, client_id]
    modifyDatabase(sql, val)

def deleteSubscription(client_id, sub_name) :
    sql = "DELETE FROM subbed WHERE client_id = %s AND sub_name = %s"
    modifyDatabase(sql, [client_id, sub_name])

# connection with the database
def connect():
    try:
        conn = mysql.connector.connect(**config)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            raise HTTPException(status_code=400, detail=f"mysql connexion : Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            raise HTTPException(status_code=400, detail=f"Database connexion : Database does not exist")
        else:
            print(err)
    else: 
        cursor = conn.cursor()
        try:
            cursor.execute("USE {}".format(database))
        except mysql.connector.Error as err:
            raise HTTPException(status_code=400, detail=f"Database {database=} does not exists.")
        else:
            return [conn, cursor]
    return None

app = FastAPI()

# to prevent CORS problemes
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def index() -> dict[str, list[Client]]:
    return  {"clients": getClientsList()}

@app.get("/client/{client_id}")
def read_client(client_id:int) -> dict[str, Client]:
    return  {"client" : getClientInfos(client_id)}


@app.post("/")
def add_client(client_name : str = Form(...)) -> dict[str, str]:
    addClient(client_name)
    return {"added": "success"}

@app.post("/client")
def add_subscription(sub_name : str = Form(...), client_id : int = Form(...)) -> dict[str, str]:
    addSubscription(client_id, sub_name)
    return {"added": "success"}

@app.delete("/client/{client_id}")
def delete_client(client_id: int) -> dict[str, str]:
    deleteClient(client_id)
    return {"deleted": "success"}

@app.delete("/client/{client_id}/subscriptions/{sub_name}")
def delete_subscription(client_id: int, sub_name: str) -> dict[str, str]:
    deleteSubscription(client_id, sub_name)
    return {"deleted": "success"}