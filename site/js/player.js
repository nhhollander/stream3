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
    }

    handle_message(data) {
        switch(data["command"]) {
            case "setsource":
                this.video.src = data["source"];
                this.frame.setAttribute("active","true");
                break;
            case "play":
                this.video.play();
                this.frame.setAttribute("active","true");
                break;
            case "pause":
                this.video.pause();
                break;
            case "stop":
                this.video.src = "";
                this.frame.setAttribute("active","false");
        }
    }

    setsource(source) {
        this.core.websocket.send_object({
            "type": "media",
            "command": "setsource",
            "source": source
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

}
export { VideoPlayer }