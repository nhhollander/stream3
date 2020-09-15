
import json
import time

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
        self.cname = "\033[39m<unauthenticated user>\033[0m"
        print("A new user has connected")
        self.authenticated = False
        self.clientstatus = {
            "mediatime": 0,
            "bufferhealth": 0,
            "timestamp": 0
        }
        self.clientinfo = {
            "browser": "unknown",
            "platform": "unknown"
        }

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

        if(message['type'] == "ping"):
            self.send_object({
                "type": "ping"
            })
            return

        if not self.authenticated:
            print("User not authenticated")
            self.send_system_message("You need to be authenticated to do that", False)
            return

        if not self.has_permission(f"message.{message['type']}"):
            print(f"User [{self.cname}] does not have permission to send message of type [{message['type']}]")
            self.send_system_message("You do not have permission to do that", False)
            return

        if message["type"] == "media":
            self.core.media.handle_message(self, message)

        if message["type"] == "clientstatus":
            self.handle_clientstatus(message)

        if message["type"] == "getallclientstatus":
            self.handle_getallclientstatus()

        

    def onclosed(self):
        print(f"User [{self.cname}] has disconnected")
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
            return
        if data["name"].lower() in [x.name.lower() for x in self.core.users]:
            print(f"Double authentication for user [{data['name']}]!")
            self.send_object({
                "type": "authresult",
                "success": False,
                "message": f"Name \"{data['name']}\" in use",
                "admin": False
            })
            return
        self.name = data['name']
        self.cname = f"\033[{result['logcolor']}{data['name']}\033[0m"
        print(f"User [{self.cname}] has authenticated!")
        self.authdata = result
        self.clientinfo = data['clientinfo']
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

    def handle_clientstatus(self, message):
        self.clientstatus["mediatime"] = message["mediatime"]
        self.clientstatus["bufferhealth"] = message["bufferhealth"]
        self.clientstatus["timestamp"] = time.time()

    ##
    # This method zeroes out the delta on the client media times and buffer
    # health, which is needed when pausing or unpausing the video.
    # If apply is true, times will be updated as if they had been passing
    # noramlly.  If false, the delta will only be zeroed, for when the video
    # was paused.
    def clientstatus_zerodelta(self, apply):
        delta = time.time() - self.clientstatus["timestamp"]
        self.clientstatus["timestamp"] = time.time()
        if apply:
            self.clientstatus["mediatime"] += delta
            self.clientstatus["bufferhealth"] -= delta

    def get_clientstatus(self):
        delta = time.time() - self.clientstatus["timestamp"]
        if self.core.media.mediastate != "play":
            delta = 0
        return {
            "mediatime": self.clientstatus["mediatime"] + delta,
            "bufferhealth": self.clientstatus["bufferhealth"] - delta,
            "browser": self.clientinfo["browser"],
            "platform": self.clientinfo["platform"]
        }

    def handle_getallclientstatus(self):
        status = {}
        for user in self.core.get_authenticated_users():
            status[user.name] = user.get_clientstatus()
        self.send_object({
            "type": "allclientstatus",
            "clients": status
        })