//stock the selected client and subscription
var clicked_client = null
var clicked_sub = null

// show the data of the selected client
function showInformations(data){
    const list = document.getElementById('sub-list')

    const client = data['client'];

    document.getElementById('suppr-client').style.display = 'block'
    document.getElementById('client-informations').style.display = "inline-block";
    document.getElementById('ecrire_message').style.display = "block";
    document.getElementById('info-title').textContent = client['name'];
    document.getElementById('new-sub-name').value = '';
    document.getElementById('message').value = ''
    document.getElementById('indication').textContent = '';

    list.innerHTML = '';


    for (let i = 0; i < client["subscriptions"].length; i++){
        const newSub = document.createElement("li");
        newSub.textContent = client["subscriptions"][i]; 
        newSub.class = "sub-list-element"
        newSub.id= client["subscriptions"][i]; 
        newSub.addEventListener("click", function(e) {
            if(clicked_sub != null){
                clicked_sub.classList.toggle("active");
            } 
            clicked_sub = newSub
            clicked_sub.classList.toggle("active");

            document.getElementById('suppr-sub').style.display = 'block'
            
        }, false);  
        list.appendChild(newSub);
    }
}

// when client is selected - get the data of the selected client
function get_informations(){
    const form = document.getElementById('form')
    form.action="http://localhost:8000/client"
    
    const input = document.getElementById('client_id')
    input.value=clicked_client.id

    let url = 'http://localhost:8000/client/' + clicked_client.id
    $.getJSON(url, showInformations);
}

// creation of list element representing a client
function createListElement(id, name){
    let client = document.createElement("li");
    client.textContent = name
    client.id = id
    client.class = "list-element"
    client.addEventListener("click", function(e) {
            if(clicked_client != null){
                clicked_client.classList.toggle("active");

            } 
            clicked_client = client
            clicked_client.classList.toggle("active");

            if(clicked_sub != null){
                clicked_sub.classList.toggle("active");
            }
            clicked_sub = null
            document.getElementById('suppr-sub').style.display = 'none'
            get_informations();
        }, false);  
    return client
}

// display the list of clients
function addClients(data){
    const clients = data['clients'];
    const list = document.getElementById('client-list')
    list.innerHTML = '';

    for (let i = 0; i < clients.length; i++){
        let client = clients[i]
        console.log(client)
        connect_client(client['id'], client['name'], client['subscriptions'])
        element = createListElement(client['id'], client['name'])
        list.appendChild(element);
    }
}

// when new subscription added to client, verify if the client didn't already have the subscription
function verifyNewSub(){
    const list = document.getElementById('sub-list').children;
    let indication = document.getElementById('indication');
    let sub = $("input[name=sub_name]").val();

    if(list.length > 0){
        let elt = list[0]
        for(let i = 1; i < list.length && elt.textContent != sub; i++){
            elt = list[i]
        }

        if (elt.textContent == sub){
            indication.textContent = "vous êtes déjà abonné à cela !"
            return
        }
    }
    // new subscription for the client : refresh subscriptions list
    client_subscribe(clicked_client.id, sub)
    indication.textContent = ""
    get_informations();
}

//delete a client
function supprClient(){
    fetch('http://localhost:8000/client/' + clicked_client.id, {
        method: 'DELETE',
    }).then(response => response.json())
    .then((data) => {
        clients[clicked_client.id].end();
        location.reload();
    })
    .catch(error => error);
}

//delete a client's subscription
function supprSubscription(){
    fetch('http://localhost:8000/client/' + clicked_client.id + '/subscriptions/' + clicked_sub.id, {
        method: 'DELETE',
    }).then(response => response.json())
    .then((data) => {
        client_unsubscribe(clicked_client.id, clicked_sub.id);
        document.getElementById('suppr-sub').style.display = 'none'
        get_informations();
    })
    .catch(error => error);
}

// send a message with MQTT protocol
function send_Message(event){
    event.preventDefault();
    var message = $('#message').val();
    var topic = $('#topic').val();
    client_publish(clicked_client.id, topic, message)
    
}

//eventListener and recuperation of the list of clients
document.getElementById("form").addEventListener("submit", verifyNewSub, false);
document.getElementById("send-message-form").addEventListener("submit", send_Message, false);
$.getJSON('http://localhost:8000', addClients);
document.getElementById("suppr-client").addEventListener("click", supprClient, false);
document.getElementById("suppr-sub").addEventListener("click", supprSubscription, false);