/*
 * Media selector.
 */
class MediaSelector {

    constructor(config, core) {
        this.config = config;
        this.core = core;

        this.openmedia = document.getElementById("openmedia");

        this.core.register_handler("message_medialist", this.handle_message.bind(this));
    }

    handle_message(message) {
        while(this.openmedia.firstChild) {
            this.openmedia.removeChild(this.openmedia.firstChild);
        }
        for(let i = 0; i < message["media"].length; i++) {
            let name = message["media"][i];
            let elem = document.createElement("div");
            elem.className = "media";
            elem.innerText = name;
            elem.setAttribute("mediapath", name);
            elem.addEventListener("click", this.handle_media_click.bind(this));
            this.openmedia.appendChild(elem);
        }
        let close = document.createElement("div");
        close.className = "media";
        close.innerText = "Cancel";
        close.addEventListener("click", this.close.bind(this));
        this.openmedia.appendChild(close);
        this.openmedia.style.display = "inline-block";
    }

    handle_media_click(event) {
        this.openmedia.style.display = "none";
        let target = event.target.getAttribute("mediapath");
        this.core.player.setsource(target);
    }

    close() {
        this.openmedia.style.display = "none";
    }

}
export { MediaSelector }