"""
https://www.youtube.com/watch?v=SORiTsvnU28&t=760s
"""
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

class SimpleClient(BaseModel):
    id : int  = Field(description ="Id of the client")
    name : str = Field(description ="Name of the client")

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


def getClientSubs(idClient) -> list[str]:
    sql = f"SELECT sub_name FROM subbed WHERE subbed.client_id={idClient};"
    data = selectInDatabase(sql)
    return [sub_name for (sub_name,) in data]
        
        
def getClientsList() -> list[Client]:
        sql = "SELECT * FROM clients;"
        data = selectInDatabase(sql)
        result = [ Client( id = id, name = name, subscriptions = getClientSubs(id)) for [id, name] in data]
        return  result

def getClientInfos(idClient) -> Client :
    sql = f"SELECT * FROM clients WHERE clients.client_id={idClient};"
    data = selectInDatabase(sql)
    if(len(data) != 1):
        raise HTTPException(status_code=400, detail=f"No data for client id {idClient}")
    else:
        client = data[0]
        return  Client(id=client[0], name=client[1], subscriptions=getClientSubs(idClient) )

def addClient(client_name) :
    sql = "INSERT INTO clients (client_name) VALUES  (%s)"
    val = [client_name]
    modifyDatabase(sql, val)

def deleteClient(client_id) :
    sql = "DELETE FROM subbed WHERE client_id = %s"
    modifyDatabase(sql, [client_id])
    sql = "DELETE FROM clients WHERE client_id = %s"
    modifyDatabase(sql, [client_id])


def addSubscription(client_id, sub_name) :
    sql = "INSERT INTO subbed (sub_name, client_id) VALUES  (%s, %s)"
    val = [sub_name, client_id]
    modifyDatabase(sql, val)

def deleteSubscription(client_id, sub_name) :
    sql = "DELETE FROM subbed WHERE client_id = %s AND sub_name = %s"
    modifyDatabase(sql, [client_id, sub_name])

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


"""
#on defini une variable item_id qui va être la suite de items



# AVoir une fonction dans une fonction permet a la fonction imbriquée 
# d'avoir accès aux variables locales de la premère fonction 
# -> évite d'utiliser des variables globales
# = None dans le paramettre indique que le parametre est obtionnel
@app.get("/clients/")
def query_items_by_parameters(
    name : str | None = None,
    price : float | None = None,
    count : int | None = None,
) :
    # fonction qui vérifie si l'item donné a bien les mêmes éléments qu'un item existant
    # all : signifie que toutes les conditions doivent être respectées
    def check_item(item: Item) -> bool:
        return all(
            (
                name is None or item.name == name,
                price is None or item.price == price,
                count is None or item.count != count,
=            )
        )
    selection = [item for item in items.values() if check_item(item)]
    return {
        "query" : {"name" : name, "price" : price, "count" : count},
        "selection" : selection,
    }

#prend directement un objet de type Item
# prend un json -> fastAPI transforme direct JSON data en objet BaseModel

#exemple de request (POST) :
# https://localhost:8080/{**contenue du JSON**}


#exemple de request : (PUT)
# https://localhost:8080/items/0?count=9001
@app.put("/update/{item_id}", 
    responses={
        404: {"description": "Item not found"},
        400: {"description": "no arguments specified"}
    }
)
def update(
    item_id: int = Path(
        title="item ID", description="Unique integer that specifies an item", ge=0
    ),
    name : str | None = Query(default=None, min_length=1, max_length=8),
    price : float | None = Query(default=None, gt=0),
    count : int | None = Query(default=None, ge=0),
) -> dict[str, Item]:
    
    if item_id not in items:
        raise HTTPException(status_code=404)
    if all(info is None for info in (name, price, count)):
        raise HTTPException(status_code=400)

    item = items[item_id]
    if name is not None:
        item.name = name
    if price is not None:
        item.price = price
    if count is not None:
        item.count = count

    return {"udated": item}


#exemple de request (DELETE):
# https://localhost:8080/items/0


#  @app.options()
#  @app.head()
#  @app.patch()
#  @app.trace()
"""