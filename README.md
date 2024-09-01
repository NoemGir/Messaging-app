# Messaging-app
Messaging app where clients can communicates between each others.  
A client can send messages and subscribe to different topics.  
We have the possibility to see all the messages received by the clients.  

This project is designed primarily for training in Docker utilization. 
  
/!\ BEWARE /!\  starting the containers can take a little bit of time due to waiting for the mysql database to be healthy

### Specifications 

The web app will be accessible on *localhost* port *8080*.  
  
It is possible to click on listed client and listed subscription.    
  
- Use of database **mysql** : To store the informations of the clients and their subscriptions.
- Use of **FastAPI** : To access the database information from the website.
- Use of Broker **MQTT** ( mosquitto) : To send the messages between the clients and manage the subscriptions.
