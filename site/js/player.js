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
        this.controlnub.addEventListener("mouseenter", this.control_nub_hover.bind(this));
        this.controlbar.addEventListener("mouseleave", this.control_bar_leave.bind(this));

        // Admin panel
        document.getElementById("cb_admin_setmedia").addEventListener("click", this.cb_select_media.bind(this));
        document.getElementById("cb_admin_play").addEventListener("click", this.play.bind(this));
        document.getElementById("cb_admin_pause").addEventListener("click", this.pause.bind(this));
        document.getElementById("cb_admin_sync").addEventListener("click", this.cb_sync_to_me.bind(this));
        // User panel

        document.body.addEventListener("keydown", this.keydown.bind(this))

        this.core.register_handler("message_media", this.handle_message.bind(this));
    }

    // Handlers //

    handle_message(data) {
        switch(data["command"]) {
            case "setsource":
                this.video.src = data["source"];
                this.frame.setAttribute("active","true");
                break;
            case "settime":
                console.log("Fun time!");
                this.video.currentTime = data["seconds"];
                break;
            case "play":
                this.video.play().catch(function() {
                    this.core.messages.show_message("CLIENT","client","Media playback failed!  Check your autoplay settings!",false,3000);
                }.bind(this));
                this.frame.setAttribute("active","true");
                break;
            case "pause":
                this.video.pause();
                break;
            case "stop":
                this.video.src = "";
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
        // I stole this regular expression from some website lol
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