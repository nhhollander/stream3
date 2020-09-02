
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
            self.send_system_message("You sent an invalid message (schema validation failure)", False)
            return

        if(message['type'] == "auth"):
            self.auth(message)
            return

        if not self.authenticated:
            print("User not authenticated")
            self.send_system_message("You need to be authenticated to do that", False)
            return

        if not self.has_permission(f"message.{message['type']}"):
            print(f"User [{self.name}] does not have permission to send message of type [{message['type']}]")
            self.send_system_message("You do not have permission to do that", False)
            return

        if message["type"] == "media":
            self.core.media.handle_message(self, message)

        

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
                "message": "Authentication Failure",
                "admin": False
            })
        else:
            self.name = data['name']
            print(f"User [{self.name}] has authenticated!")
            self.authdata = result
            self.authenticated = True
            self.send_object({
                "type": "authresult",
                "success": True,
                "message": "Authentication Successful",
                "admin": result["admin"]
            })
            self.send_system_message(f"Welcome <b>{data['name']}</b>!", True)
            self.core.send_system_message_to_all(f"<b>{data['name']}</b> has connected!", True)
            self.core.media.sync_client(self)

    def send_system_message(self, message, allowhtml, duration=-1):
        if duration < 0:
            duration = self.config["client"]["default_message_duration"]
        self.send_object({
            "type": "message",
            "from": "SYSTEM",
            "class": "system",
            "message": message,
            "allowhtml": allowhtml,
            "duration": duration
        })

    def send_object(self, obj):
        if not self.core.validator.validate(obj):
            print("Sending invalid message, dropping")
            return
        self.socket.sendMessage(json.dumps(obj))

    def has_permission(self, permission):
        permission_parts = permission.split(".")
        for user_permission in self.authdata["permissions"]:
            user_permission_parts = user_permission.split(".")
            success = True
            for i in range(0, min(len(permission_parts),len(user_permission_parts))):
                if user_permission_parts[i] == "*":
                    return True
                if permission_parts[i] == user_permission_parts[i]:
                    continue
                success = False
            if success:
                return True
        return False