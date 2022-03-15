#Para crear el ambiente virtual
#python3 -m venv .venv
#source .venv/bin/activate

from __future__ import print_function
from geventwebsocket import WebSocketServer, WebSocketApplication, Resource
#python3.7 -m pip install werkzeug
from werkzeug.debug import DebuggedApplication
from flask import Flask, render_template, request
import json

#python3.7 -m pip install gevent
from gevent import monkey

#db and aiml imports
#python3.7 -m pip3.7 install tinydb
from tinydb import TinyDB, Query
import os
#python3.7 -m pip install python-aiml
import aiml

monkey.patch_all()

# Para la interfaz y otras cosas
flask_app = Flask(__name__)
flask_app.debug = True

k = aiml.Kernel()
BRAIN_FILE = "brain.dump"
if os.path.exists(BRAIN_FILE):
    print("Cargando desde archivo cerebral file: " + BRAIN_FILE)
    k.loadBrain(BRAIN_FILE)
else:
    print("Parsing aiml files")
    k.bootstrap(learnFiles="std-startup.aiml", commands="load aiml b")
    print("Cargando Skynet: " + BRAIN_FILE)
    k.saveBrain(BRAIN_FILE)


db = TinyDB('conversations.json')
Usuario = Query()


#INICIO GERSON
#librerías para conexion a facebook
from pymessenger.bot import Bot

#Token para permitir acceso a la pagina
ACCESS_TOKEN = 'EAAFZBSupvax8BAKZCEOyv3sEjOWlkhOC802XZCVRj2SiaezAIzbJHfieA6BecrPVcoaK3UeFgckd6FZCm5856kgbqDRK9BWjEvCGAvKWZAsJx421Qser2HVkrtUTAcHVpvPnjuEeACvDYYTqV2Kx6TOHjiOVc82S4DGOFIQAVgwZDZD'
VERIFY_TOKEN = 'PRUEBATOKEN'
bot = Bot(ACCESS_TOKEN)

#class ChatApplication(WebSocketApplication):



@flask_app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        token_enviado = request.args.get("hub.verify_token")
        return verificar_token(token_enviado)
    else:
        # Obtener el mensaje
       output = request.get_json()
       contador_mensajes = 0
       
       #print (output)
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            if message.get('message'):
                contador_mensajes = contador_mensajes + 1
                #Guarda el ID del usuario para responder
                id_usuario = message['sender']['id']
                #Si es primer mensaje, guarda el id del usuario
                #if contador_mensajes == 0:
                    #send_client_list(id_usuario)
                #Si llega un mensaje lo envía a proceso de respuesta
                if message['message'].get('text'):
                    mensaje_recibido = message['message'].get('text')
                    broadcast(id_usuario, mensaje_recibido)
                    #mensaje_respuesta(id_usuario, mensaje_recibido)
    return "Mensaje Recibido"
#FIN GERSON

def send_client_list(id_usuario):
    #current_client = self.ws.handler.active_client
    #current_client.nickname = message['nickname']
 
    #username = current_client.nickname
    username = id_usuario
    if not len(username)>0:
        username='desconocido'
    user=db.search(Usuario.user == username)
    #print(user)
        
    if len(user) == 0:
        user = db.insert({'user': username, 'conversations': [[]]})
        #user = db.get(eid=user)
    else:
        user=user[0]
        conv=user['conversations']
        if not conv:
            print(conv)
        #conv.append([])
          
        #if not conv:
            
        #db.update({'conversations':conv},doc_ids=[user.doc_id])

    #self.ws.send(json.dumps({
    #    'msg_type': 'update_clients',
    #    'clients': [
    #        getattr(client, 'nickname', 'anonymous')
    #        for client in self.ws.handler.server.clients.values()
    #    ]
    #}))


def broadcast(id_user, message_):
    #nickname = message['nickname']
    #message_ = message['message']
    #print (bot.get_user_info(nickname))
    profile = bot.get_user_info(id_user)
    first_name = profile.get('first_name')
    last_name = profile.get('last_name')
    
    user=db.search(Usuario.id_user == id_user)
    if len(user)==0:
        user=db.insert({'id_user':id_user, 'first_name':first_name, 'last_name':last_name,'conversations':[[]]})
        user=db.get(eid=id_user)
    else:
        user=user[0]
    ans=k.respond(message_)
    
    if message_.upper() == "HOLA":
        ans = ans + " " + first_name
    
    conv=user['conversations']
    
    conv[-1].append({'msg':message_,'ans':ans})
    
    db.update({'conversations':conv},doc_ids=[user.doc_id])
    #emit('response', {'data': ans.lower()})

#INCIO GERSON
    #Llama a metodo para enviar mensaje
    mensaje_respuesta(id_user, ans, message_, first_name)
#FIN GERSON
    
    #for client in self.ws.handler.server.clients.values():
    #    client.ws.send(json.dumps({
    #        'msg_type': 'message',
    #        'nickname': message['nickname'],
    #        'message': message['message']
    #    }))
    #for client in self.ws.handler.server.clients.values():
    #    client.ws.send(json.dumps({
    #        'msg_type': 'botanswer',
    #        'nickname': 'CHATBOT',
    #        'message': ans
    #    }))
    
#INICIO GERSON
def verificar_token(token_enviado):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_enviado == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Token Invalido' 

#Se usa la librería PyMessenger para responder al usuario que envió el mensaje
def mensaje_respuesta(id_usuario, response, message, name):
    #Envia mensaje (id del usuario al que envía, texto a enviar)
    
    bot.send_text_message(id_usuario, response)
    return "enviado"

if __name__ == "__main__":
    flask_app.run()
#FIN GERSON