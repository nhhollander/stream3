
import json

##
# User class.
# Separate from the websocket "user" class due to duck type name collision
# issues.
class User:

    def __init__(self, config, core, socket):
        self.config = config
        self.core = core
        self.socket = socket
        self.name = "<unauthenticated user>"

        self.authenticated = False

        core.users.append(self)

    def onmessage(self, data):
        message = json.loads(data)
        # Validate the message
        if not self.core.validator.validate(message):
            print("Received invalid message, dropping")
            return
        print(json.dumps(message, indent=2))

        if(message['type'] == "auth"):
            self.auth(message)

    def onclosed(self):
        print(f"User [{self.name}] has disconnected")
        self.core.users.remove(self)
        if self.authenticated:
            self.core.send_system_message_to_all(f"<b>{self.name}</b> has disconnected", True)

    def auth(self, data):
        result = self.core.auth.authenticate(data["name"], data["key"], self)
        if result == False:
            print(f"User presenting as [{data['name']}] failed authentication")
            self.send_object({
                "type": "authresult",
                "success": False,
                "message": "Authentication Failure"
            })
        else:
            print(f"User [{data['name']}] has authenticated!")
            self.authdata = result
            self.authenticated = True
            self.send_object({
                "type": "authresult",
                "success": True,
                "message": "Authentication Successful"
            })
            self.send_system_message(f"Welcome <b>{data['name']}</b>!", True)
            self.core.send_system_message_to_all(f"<b>{data['name']}</b> has connected!", True)

    def send_system_message(self, message, allowhtml):
        self.send_object({
            "type": "message",
            "from": "SYSTEM",
            "class": "system",
            "message": message,
            "allowhtml": allowhtml
        })

    def send_object(self, obj):
        if not self.core.validator.validate(obj):
            print("Sending invalid message, dropping")
            return
        self.socket.sendMessage(json.dumps(obj))
        