
from SimpleWebSocketServer import SimpleSSLWebSocketServer
import ssl
from wrapper import WebSocketWrapper
from auth import Auth

##
# Core of the server.
# This is where the magic comes together.
# This is a helpful comment.
class Core:

    def __init__(self, config):
        self.config = config

        self.users = []

        wshost = self.config['wsserver']['host']
        wsport = self.config['wsserver']['port']
        wscert = self.config['wsserver']['certfile']
        wskey  = self.config['wsserver']['keyfile']
        self.server = SimpleSSLWebSocketServer(wshost,wsport,WebSocketWrapper,wscert,wskey,ssl.PROTOCOL_TLS)
        self.server.cool_core = self

        self.auth = Auth(self.config, self)

    def run(self):
        print("Server is now running forever!")
        self.server.serveforever()

    def get_authenticated_users(self):
        return [x for x in self.users if x.authenticated]

    def send_object_to_all(self, obj, authenticated_only=True):
        if authenticated_only:
            for user in self.get_authenticated_users():
                user.send_object(obj)
        else:
            for user in self.users:
                user.send_object(obj)

    def send_system_message_to_all(self, message, allowhtml, authenticated_only=True):
        if authenticated_only:
            for user in self.get_authenticated_users():
                user.send_system_message(message, allowhtml)
        else:
            for user in self.users:
                user.send_system_message(message, allowhtml)

    