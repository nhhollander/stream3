import time

##
# Media Management Class.
class Media:

    def __init__(self, config, core):
        self.config = config["media"]
        self.core = core

        self.mediasource = ""
        self.mediatime = (0,0)
        self.mediastate = "stop"

    def handle_message(self, user, message):
        if not user.has_permission(f"media.{message['command']}"):
            print(f"User [{user.cname}] does not have permission to use media command [{message['command']}]")
            user.send_system_message("You do not have permission to do that", False)
            return

        cmd = message['command']
        if cmd == "setsource":
            self.mediasource = message['source']
            self.setsource(message['source'])
            print(f"User [{user.cname}] set the media source to [{message['source']}]")
            self.core.send_system_message_to_all(f"<b>{user.name}</b> has changed the media source",True)
        elif cmd == "settime":
            if self.mediastate == "stop":
                print(f"User [{user.cname}] attempted to change time, but there is no media playing")
                user.send_system_message("Unable to set time: No Media",False)
                return
            seconds = message['seconds']
            ss = int(seconds % 60)
            mm = int(seconds / 60) % 60
            hh = int(seconds / 360)
            self.set_media_time(seconds)
            print(f"User [{user.cname}] set the playback time to [{hh:0>2d}:{mm:0>2d}:{ss:0>2d}]")
            self.core.send_system_message_to_all(f"<b>{user.name}</b> set time to <b>{hh:0>2d}:{mm:0>2d}:{ss:0>2d}</b>",True)
        elif cmd == "play":
            if self.mediastate == "stop":
                print(f"User [{user.cname}] attempted to play playback, but there is no media")
                user.send_system_message("Unable to play: Media is not playing",False)
                return
            if not self.mediastate == "pause":
                print(f"Warning: User [{user.cname}] attempted to start playback, but media was not paused")
            self.play()
            print(f"User [{user.cname}] started playback")
            self.core.send_system_message_to_all(f"<b>{user.name}</b> started playback",True)
        elif cmd == "pause":
            if self.mediastate == "stop":
                print(f"User [{user.cname}] attempted to pause playback, but there is no media")
                user.send_system_message("Unable to pause: Media is not playing",False)
                return
            if not self.mediastate == "play":
                print(f"Warning: User [{user.cname}] attempted to pause playback, but media was not playing")
            self.pause()
            print(f"User [{user.cname}] paused playback")
            self.core.send_system_message_to_all(f"<b>{user.name}</b> paused playback",True)
        elif cmd == "stop":
            if self.mediastate == "stop":
                print(f"Warning: User [{user.cname}] attempted to stop playback, but media was not playing")
                user.send_system_message("Unable to stop: Media is not playing",False)
                return
            self.stop()
            print(f"User [{user.cname}] stopped playback")
            self.core.send_system_message_to_all(f"<b>{user.name}</b> stopped playback",True)
        
    def sync_client(self, user):
        if self.mediastate == "stop": return
        user.send_object({
            "type": "media",
            "command": "setsource",
            "source": self.mediasource
        })
        user.send_object({
            "type": "media",
            "command": "settime",
            "seconds": self.get_media_time()
        })
        user.send_object({
            "type": "media",
            "command": self.mediastate
        })

    def get_media_time(self):
        if self.mediastate == "pause":
            return self.mediatime[1]
        elif self.mediastate == "play":
            timedelta = time.time() - self.mediatime[0]
            return self.mediatime[1] + timedelta
        elif self.mediastate == "stop":
            return -1

    def set_media_time(self, t):
        self.mediatime = (time.time(), t)
        self.core.send_object_to_all({
            "type": "media",
            "command": "settime",
            "seconds": t
        })

    def update_media_time(self):
        self.set_media_time(self.get_media_time())

    def setsource(self, uri):
        self.mediasource = uri
        self.mediastate = "pause"
        self.set_media_time(0)
        self.core.send_object_to_all({
            "type": "media",
            "command": "setsource",
            "source": uri
        })

    def settime(self, time):
        self.pause()
        self.set_media_time(time)
        self.core.send_object_to_all({
            "type": "media",
            "command": "settime",
            "seconds": time
        })

    def play(self):
        self.update_media_time()
        self.mediastate = "play"
        self.core.send_object_to_all({
            "type": "media",
            "command": "play"
        })
        for user in self.core.get_authenticated_users():
            user.clientstatus_zerodelta(False)

    def pause(self):
        self.update_media_time()
        self.mediastate = "pause"
        self.core.send_object_to_all({
            "type": "media",
            "command": "pause"
        })
        for user in self.core.get_authenticated_users():
            user.clientstatus_zerodelta(True)

    def stop(self):
        self.mediastate = "stop"
        self.core.send_object_to_all({
            "type": "media",
            "command": "stop"
        })