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

        this.controlbar = document.getElementById("controlbar");
        this.controlnub = document.getElementById("controlnub");
        this.button_selectmedia = document.getElementById("cb_setmedia");
        this.button_play = document.getElementById("cb_play");
        this.button_pause = document.getElementById("cb_pause");

        this.controlnub.addEventListener("mouseenter", this.control_nub_hover.bind(this));
        this.controlbar.addEventListener("mouseleave", this.control_bar_leave.bind(this));
        this.button_selectmedia.addEventListener("click", this.cb_select_media.bind(this));
        this.button_play.addEventListener("click", this.play.bind(this));
        this.button_pause.addEventListener("click", this.pause.bind(this));

        this.core.register_handler("message_media", this.handle_message.bind(this));
    }

    handle_message(data) {
        switch(data["command"]) {
            case "setsource":
                this.video.src = data["source"];
                this.frame.setAttribute("active","true");
                break;
            case "settime":
                this.video.currentTime = data["seconds"];
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

    // Control bar methods //

    control_nub_hover(e) {
        if(this.core.auth.authenticated) {
            this.controlbar.setAttribute("visible","true");
        }
    }

    control_bar_leave(e) {
        this.controlbar.setAttribute("visible","false");
    }

    cb_select_media() {
        let media = prompt("Enter URI:");
        var pattern = new RegExp('^(https?:\\/\\/)?'+ // protocol
            '((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|'+ // domain name
            '((\\d{1,3}\\.){3}\\d{1,3}))'+ // OR ip (v4) address
            '(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*'+ // port and path
            '(\\?[;&a-z\\d%_.~+=-]*)?'+ // query string
            '(\\#[-a-z\\d_]*)?$','i'); // fragment locator
        if(!pattern.test(media)) {
            this.core.messages.show_message("CLIENT","client","Invalid URI",false,3000);
            return;
        }
        
        this.setsource(media);
    }

}
export { VideoPlayer }