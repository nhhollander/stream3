/*
 * Control bar management.
 */
class ControlBar {

    constructor(config, core) {
        this.config = config;
        this.core = core;

        this.controlbar = document.getElementById("controlbar");

        this.button_open = document.getElementById("cb_open");
        this.button_users = document.getElementById("cb_users");
        this.button_stop = document.getElementById("cb_stop");
        this.button_reset = document.getElementById("cb_reset");
        this.button_play = document.getElementById("cb_play");
        this.button_pause = document.getElementById("cb_pause");
        this.button_mute = document.getElementById("cb_mute");
        this.button_unmute = document.getElementById("cb_unmute");

        this.scrub_prog = document.getElementById("cb_prog");
        this.scrub_buff = document.getElementById("cb_buff");

        this.button_open.addEventListener("click", this.button_open_clicked.bind(this));
        this.button_users.addEventListener("click", this.button_users_clicked.bind(this));
        this.button_stop.addEventListener("click", this.button_stop_clicked.bind(this));
        this.button_reset.addEventListener("click", this.button_reset_clicked.bind(this));
        this.button_play.addEventListener("click", this.button_play_clicked.bind(this));
        this.button_pause.addEventListener("click", this.button_pause_clicked.bind(this));
        this.button_mute.addEventListener("click", this.button_mute_clicked.bind(this));
        this.button_unmute.addEventListener("click", this.button_unmute_clicked.bind(this));

        this.core.player.video.addEventListener("play", this.video_play_handler.bind(this));
        this.core.player.video.addEventListener("pause", this.video_pause_handler.bind(this));
        this.core.player.video.addEventListener("volumechange", this.video_volume_handler.bind(this));

        document.body.addEventListener("mousemove", this.mouse_move_handler.bind(this));
        document.body.addEventListener("mousedown", this.mouse_move_handler.bind(this));
        document.body.addEventListener("mouseup", this.mouse_move_handler.bind(this));

        setInterval(this.update_bar.bind(this), this.config["controls"]["update_interval"]);
    }

    update_bar() {
        let video = this.core.player.video;
        let prog = video.currentTime / video.duration;
        if(isNaN(prog)) { prog = 0; }
        this.scrub_prog.style.width = `${prog*100}%`;
        let buffers = video.buffered;
        if(buffers.length > 0) {
            let buffduration = buffers.end(buffers.length-1);
            let bprog = buffduration / video.duration;
            if(isNaN(bprog)) { bprog = 0; }
            this.scrub_buff.style.width = `${bprog*100}%`;
        }
    }

    // Handlers //

    mouse_move_handler() {
        if(!this.core.auth.authenticated) { return; }
        this.controlbar.setAttribute("_hidden", "false");
        document.body.style.cursor = "auto";
        clearTimeout(this.hide_timeout);
        this.hide_timeout = setTimeout(function() {
            this.controlbar.setAttribute("_hidden", "true");
            document.body.style.cursor = "none";
        }.bind(this), this.config["controls"]["timeout"]);
    }

    video_play_handler() {
        this.button_play.style.display = "none";
        this.button_pause.style.display = "inline-block";
    }

    video_pause_handler() {
        this.button_play.style.display = "inline-block";
        this.button_pause.style.display = "none";
    }

    video_volume_handler() {
        let video = this.core.player.video;
        if(video.muted || video.volume == 0) {
            this.button_mute.style.display = "none";
            this.button_unmute.style.display = "inline-block";
        } else {
            this.button_mute.style.display = "inline-block";
            this.button_unmute.style.display = "none";
        }
    }

    button_open_clicked() {
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
        
        this.core.player.setsource(media);
    }

    button_stop_clicked() {
        this.core.player.stop();
    }

    button_users_clicked() {
        this.core.clientstatus.toggle_button_clicked();
    }

    button_reset_clicked() {
        this.core.player.settime(0);
    }

    button_play_clicked() {
        this.core.player.play();
    }

    button_pause_clicked() {
        this.core.player.pause();
    }

    button_mute_clicked() {
        this.core.player.video.muted = true;
    }

    button_unmute_clicked() {
        this.core.player.video.muted = false;
    }
    
    // Other functions //
    setadmin(admin) {
        if(admin) {
            this.controlbar.setAttribute("admin","true");
        } else {
            this.controlbar.setAttribute("admin","false");
        }
    }

}
export { ControlBar }