/*
 * Control bar management.
 */
class ControlBar {

    constructor(config, core) {
        this.config = config;
        this.core = core;

        this.controlbar = document.getElementById("controlbar");

        this.button_open = document.getElementById("cb_open");
        this.button_stop = document.getElementById("cb_stop");
        this.button_play = document.getElementById("cb_play");
        this.button_pause = document.getElementById("cb_pause");

        this.button_open.addEventListener("click", this.button_open_clicked.bind(this));
        this.button_stop.addEventListener("click", this.button_stop_clicked.bind(this));
        this.button_play.addEventListener("click", this.button_play_clicked.bind(this));
        this.button_pause.addEventListener("click", this.button_pause_clicked.bind(this));

        this.core.player.video.addEventListener("play", this.video_play_handler.bind(this));
        this.core.player.video.addEventListener("pause", this.video_pause_handler.bind(this));
    }

    // Handlers //

    video_play_handler() {
        this.button_play.style.display = "none";
        this.button_pause.style.display = "inline-block";
    }

    video_pause_handler() {
        this.button_play.style.display = "inline-block";
        this.button_pause.style.display = "none";
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

    button_play_clicked() {
        this.core.player.play();
    }

    button_pause_clicked() {
        this.core.player.pause();
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