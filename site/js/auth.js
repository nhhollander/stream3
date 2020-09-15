/*
 * Client authentication management class.
 * This class is responsible for authenticating the user with the server.
 */
class Auth {

    constructor(config, core) {
        this.config = config['auth'];
        this.core = core;

        this.authenticated = false;
        this.autosubmit = false;

        this.authwindow = document.getElementById("auth");
        this.elem_nickname = document.getElementById("auth_nickname");
        this.elem_key = document.getElementById("auth_key");
        this.elem_submit = document.getElementById("auth_submit");
        this.elem_error = document.getElementById("auth_error");
        this.elem_hello = document.getElementById("hello");
        this.elem_hellonick = document.getElementById("nickname");

        this.core.register_handler("message_authresult", this.callback.bind(this));
        this.core.register_handler("ws_open", this.ws_open.bind(this));
        this.core.register_handler("ws_close", this.ws_close.bind(this));

        this.elem_submit.addEventListener("click", this.submit.bind(this));

        this.parse_hash();
    }

    parse_hash() {
        if(!window.location.hash) { return; }
        if(window.location.hash == "") { return; }
        let decoded = JSON.parse(atob(window.location.hash.substring(1)));
        if("name" in decoded) {
            this.elem_nickname.value = decoded['name'];
            this.elem_nickname.disabled = true;
        }
        if("key" in decoded) {
            this.elem_key.value = decoded['key'];
            this.elem_key.disabled = true;
        }
        if("autosubmit" in decoded) {
            this.autosubmit = decoded['autosubmit'];
        }
    }

    get_browser_identity() {
        if(navigator.userAgent.includes("Opera")) {
            return "opera";
        } else if(navigator.userAgent.includes("Chrome")) {
            return "chrome";
        } else if(navigator.userAgent.includes("Safari")) {
            return "safari";
        } else if(navigator.userAgent.includes("Firefox")) {
            return "firefox";
        } else if(navigator.userAgent.includes("MSIE")) {
            return "ie";
        } else {
            return "unknown";
        }
    }

    get_platform_identity() {
        if(navigator.platform.toLowerCase().includes("linux")) {
            return "linux";
        } else if(navigator.platform.toLowerCase().includes("win")) {
            return "windows";
        } else if(navigator.platform.toLowerCase().includes("mac")) {
            return "apple";
        } else if(navigator.platform.toLowerCase().includes("android")) {
            return "android";
        } else if(navigator.platform.toLowerCase().includes("iphone")) {
            return "apple";
        } else {
            return "unknown";
        }
    }

    submit() {
        if(!this.core.websocket.connected) {
            console.error("Attempted to authenticate while disconnected");
            return;
        }
        this.elem_submit.disabled = true;
        let nickname = this.elem_nickname.value;
        let key = this.elem_key.value;
        console.log(`Submit: [${nickname}] [${key}]`);
        this.core.websocket.send_object({
            "type": "auth",
            "name": nickname,
            "key": key,
            "clientinfo": {
                "browser": this.get_browser_identity(),
                "platform": this.get_platform_identity()
            }
        });
    }

    ws_open() {
        this.elem_submit.disabled = false;
        if(this.autosubmit) {
            this.submit();
        }
    }

    ws_close() {
        this.elem_submit.disabled = true;
        this.authenticated = false;
    }

    callback(data) {
        if(data['success']) {
            this.authwindow.className = "auth hidden";
            this.elem_hello.className = "hello";
            this.elem_hellonick.innerText = this.elem_nickname.value;
            this.authenticated = true;
            this.autosubmit = true;
            this.core.controlbar.setadmin(data["admin"]);
            setTimeout(function() {
                this.authwindow.style.display = "none"
            }.bind(this), 500);
        } else {
            this.authwindow.style.display = "block";
            this.authwindow.className = "auth";
            this.elem_error.innerText = data["message"];
            this.elem_submit.disabled = false;
            this.elem_hello.className = "hello hidden";
            this.autosubmit = false;
        }
    }

}
export { Auth }