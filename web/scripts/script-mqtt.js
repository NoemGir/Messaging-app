var clients = {}; // Create an empty array


function client_unsubscribe(clientId, topic) {

    clients[clientId].unsubscribe(topic, () => {
        console.log('Unsubscribed');
    })
}

function client_subscribe(clientId, topic) {

    clients[clientId].subscribe(topic, { qos: 0 }, function (error, granted) {
        if (error) {
            console.log(error)
        } else {
            console.log(`${granted[0].topic} was subscribed`)
        }
    })
}

function client_publish(clientId, topic, message) {
    clients[clientId].publish(topic, message, { qos: 0, retain: true })
}

function connect_client(clientId, clientName, subscriptions) {
    const host = 'ws://localhost:8083/mqtt'
    const options = {
        keepalive: 60,
        clientId: clientId,
        protocolId: 'MQTT',
        protocolVersion: 4,
        clean: true,
        reconnectPeriod: 1000,
        connectTimeout: 30 * 1000,
        will: {
            topic: 'WillMsg',
            payload: 'Connection Closed abnormally..!',
            qos: 0,
            retain: false
        },
    }
    console.log('Connecting mqtt client')
    const client = mqtt.connect(host, options)
    client.on('error', (err) => {
        console.log('Connection error: ', err)
        client.end()
    })
    client.on('reconnect', () => {
        console.log('Reconnecting...')
    })
    client.on('connect', () => {
        console.log(`Client connected: ${clientName}`)
        clients[clientId] = client
        for (let i = 0; i < subscriptions.length; i++){
            client_subscribe(clientId, subscriptions[i])
        }
    })
    client.on('message', function (topic, message) {
        console.log(message.toString())
        let area = document.getElementById('message-area')
        let newMessage = document.createElement('p')
        newMessage.class = "received-message"
        newMessage.innerHTML =  `<b>[${clientName}</b> received on topic <b>${topic}</b>] : <br>${message}`
        area.appendChild(newMessage)
    })

}



