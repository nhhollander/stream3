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
            "key": key
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
    }

    callback(data) {
        if(data['success']) {
            this.authwindow.className = "auth hidden";
            this.elem_hello.className = "hello";
            this.elem_hellonick.innerText = this.elem_nickname.value;
            setTimeout(function() {
                this.authwindow.style.display = "none"
            }.bind(this), 500);
        } else {
            this.authwindow.style.display = "block";
            this.authwindow.className = "auth";
            this.elem_error.innerText = data["message"];
            this.elem_submit.disabled = false;
            this.elem_hello.className = "hello hidden";
        }
    }

}
export { Auth }