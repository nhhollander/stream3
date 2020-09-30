/*
 * Player management class.
 * Everything to do with the video player is contained within this class
 */
class VideoPlayer {

    constructor(config, core) {
        this.config = config;
        this.core = core;

        this.frame = document.getElementById("videoplayer");
        this.video = document.getElementById("video");

        this.core.register_handler("message_media", this.handle_message.bind(this));
        this.video.addEventListener("error", this.handle_media_error.bind(this));

        setInterval(this.send_clientstatus.bind(this), this.config["player"]["status_update_interval"]);
    }

    send_clientstatus() {
        if(!this.core.auth.authenticated) { return; }
        if(this.frame.getAttribute("active") == "false") { return; }
        let mediatime = this.video.currentTime;
        let bufferhealth = 0;
        let buffers = this.video.buffered;
        if(buffers.length > 0) {
            for(let i = 0; i < buffers.length; i++) {
                let btime = buffers.end(i);
                let bhealth = btime - mediatime;
                if(bhealth > bufferhealth) {
                    bufferhealth = bhealth;
                }
            }
        }
        this.core.websocket.send_object({
            "type": "clientstatus",
            "mediatime": mediatime,
            "bufferhealth": bufferhealth
        });
    }

    // Handlers //

    handle_media_error(error) {
        this.core.messages.show_message("CLIENT","client","Failed to load media!",false,6000);
        console.log(error);
    }

    handle_message(data) {
        switch(data["command"]) {
            case "setsource":
                if(this.video.src == data["source"]) { return; }
                this.video.src = data["source"];
                this.frame.setAttribute("active","true");
                break;
            case "settime":
                this.video.currentTime = data["seconds"];
                break;
            case "play":
                this.video.play().catch(function() {
                    if(this.video.src != "") {
                        this.core.messages.show_message("CLIENT","client","Media playback failed!  Check your autoplay settings!",false,3000);
                    }
                }.bind(this));
                this.frame.setAttribute("active","true");
                break;
            case "pause":
                this.video.pause();
                break;
            case "stop":
                //this.video.src = "";
                this.frame.setAttribute("active","false");
            default:
                this.core.messages.show_message("CLIENT","client","Server sent bad media command",false,3000);
                console.log(`Bad media command [${data["command"]}]`);
        }
    }

    keydown(data) {
        if(data.key == "F4") {
            if(this.controlbar.getAttribute("admin") == "false") {
                this.controlbar.setAttribute("admin","true");
            } else {
                this.controlbar.setAttribute("admin","false");
            }
        }
    }

    cb_sync_to_me(data) {
        let current_time = this.video.currentTime;
        this.core.websocket.send_object({
            "type": "media",
            "command": "settime",
            "seconds": current_time
        });
    }

    // Media control methods //

    setsource(source) {
        this.core.websocket.send_object({
            "type": "media",
            "command": "setsource",
            "source": source
        });
    }

    settime(time) {
        this.core.websocket.send_object({
            "type": "media",
            "command": "settime",
            "seconds": time
        });
    }

    play() {
        this.core.websocket.send_object({
            "type": "media",
            "command": "play"
        });
    }

    pause() {
        this.core.websocket.send_object({
            "type": "media",
            "command": "pause"
        });
    }

    stop() {
        this.core.websocket.send_object({
            "type": "media",
            "command": "stop"
        });
    }

}
export { VideoPlayer }