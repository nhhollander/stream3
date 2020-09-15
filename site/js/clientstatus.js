/*
 * Client status for admin.
 */
class ClientStatus {

    constructor(config, core) {
        this.config = config;
        this.core = core;

        this.infobox = document.getElementById("userinfo");
        this.table = document.getElementById("userinfotable");

        this.core.register_handler("message_allclientstatus", this.handle_message.bind(this));

        this.running = false;
        this.updateinterval = undefined;
    }

    /*!
     *  Convert seconds into hh:mm:ss.ms
     */
    convert_time(time) {
        time = Math.max(time, 0);
        let hh = Math.floor(time / 360);
        let mm = Math.floor(time / 60) % 60;
        let ss = Math.floor(time % 60);
        let ms = Math.floor((time % 1) * 100);
        hh = ('' + hh).padStart(2,'0');
        mm = ('' + mm).padStart(2,'0');
        ss = ('' + ss).padStart(2,'0');
        ms = ('' + ms).padStart(2,'0');
        return `${hh}:${mm}:${ss}.${ms}`;
    }

    get_platform_string(platform) {
        let res = "";
        switch(platform["browser"]) {
            case "opera": res += "&#xe011;"; break;
            case "chrome": res += "&#xe012;"; break;
            case "safari": res += "&#xe013;"; break;
            case "firefox": res += "&#xe010;"; break;
            case "ie": res += "&#xe014;"; break;
            default: res += "&#xe015;"; break;
        }
        switch(platform["platform"]) {
            case "linux": res += "&#xe00c;"; break;
            case "windows": res += "&#xe00d;"; break;
            case "apple": res += "&#xe00e;"; break;
            case "android": res += "&#xe00f;"; break;
            default: res += "&#xe015;"; break;
        }
        return res;
    }

    handle_message(message) {
        let oldrows = this.table.querySelectorAll("tr:not([isheader])");
        for(let i = 0; i < oldrows.length; i++) {
            let row = oldrows[i];
            row.parentElement.removeChild(row);
        }
        for(const username in message["clients"]) {
            let user = message["clients"][username];
            let row = document.createElement("tr");
            let usercell = document.createElement("td");
            usercell.innerText = username;
            let platform = document.createElement("td");
            platform.innerHTML = this.get_platform_string(user);
            let currenttime = document.createElement("td");
            currenttime.innerText = this.convert_time(user["mediatime"]);
            let bufferhealth = document.createElement("td");
            bufferhealth.innerText = this.convert_time(user["bufferhealth"]);
            row.appendChild(usercell);
            row.appendChild(platform);
            row.appendChild(currenttime);
            row.appendChild(bufferhealth);
            this.table.appendChild(row);
        }
    }

    toggle_button_clicked() {
        if(this.running) {
            this.running = false;
            clearInterval(this.updateinterval);
            this.infobox.style.display = "none";
        } else {
            this.running = true;
            this.updateinterval = setInterval(this.requestupdate.bind(this), this.config["clientstatus"]["interval"]);
            this.infobox.style.display = "inline-block";
        }
    }

    requestupdate() {
        this.core.websocket.send_object({
            "type": "getallclientstatus"
        });
    }
}
export { ClientStatus }