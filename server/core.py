
from SimpleWebSocketServer import SimpleSSLWebSocketServer
import ssl

from wrapper import WebSocketWrapper
from auth import Auth
from validator import MessageValidator
from media import Media

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
        self.media = Media(self.config, self)
        self.validator = MessageValidator(self.config, self)

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

    def send_system_message_to_all(self, message, allowhtml, duration=-1, authenticated_only=True):
        if authenticated_only:
            for user in self.get_authenticated_users():
                user.send_system_message(message, allowhtml, duration)
        else:
            for user in self.users:
                user.send_system_message(message, allowhtml, duration)

    