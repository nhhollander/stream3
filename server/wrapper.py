##
# This file contains wrapper classes and stuff to connect the helpful
# SimpleWebsocketServer library to the structure of the streaming server

from SimpleWebSocketServer import WebSocket
from user import User

import traceback

class WebSocketWrapper(WebSocket):

    def handleMessage(self):
        try:
            self.cool_user.onmessage(self.data)
        except:
            traceback.print_exc()

    def handleConnected(self):
        try:
            core = self.server.cool_core
            self.cool_user = User(core.config, core, self)
        except:
            traceback.print_exc()

    def handleClose(self):
        try:
            self.cool_user.onclosed()
        except:
            traceback.print_exc()

