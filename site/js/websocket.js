/*!
 * Websocket communications class.
 * This class contains and manages the websocket interface for the application.
 */
class WebSocketManager {

    constructor(config, core) {
        this.config = config['websocket'];
        this.core = core;
        this.socket = undefined;
        this.retry_timeout = 1;

        this.connectionstatuswarning = document.getElementById("wswarning");

        this.connected = false;

        this.connect();
    }

    connect() {
        if(this.config['noconnect']) { return; }
        console.log("Attempting websocket connection");
        this.socket = new WebSocket(this.config['address'])
        this.socket.onopen = this.onopen.bind(this);
        this.socket.onclose = this.onclose.bind(this);
        this.socket.onmessage = this.onmessage.bind(this);
        this.socket.onerror = this.onerror.bind(this);
        setTimeout(function() {
            if(this.connected) { return; }
            console.error("Connection attempt timeout! Killing...");
            this.socket.close()
        }.bind(this), 2000);
    }

    onopen(event) {
        console.log("The websocket connection has been opened");
        this.retry_timeout = 1;
        this.connected = true;
        this.core.send_event("ws_open");
        this.connectionstatuswarning.className = "connectionstatuswarning hidden";
    }

    onclose(event) {
        console.log(`The websocket connection has been closed.  Retrying connection in ${this.retry_timeout} seconds`);
        this.connected = false;
        setTimeout(this.connect.bind(this), this.retry_timeout * 1000);
        if(this.retry_timeout > 2) {
            this.connectionstatuswarning.className = "connectionstatuswarning";
        }
        if(this.retry_timeout < 10) {
            this.retry_timeout += 1;
        }
    }

    onmessage(event) {
        console.log("A websocket message has been received");
        let data = JSON.parse(event.data);
        this.core.send_event(`message_${data['type']}`, data);
    }

    onerror(event) {
        console.log("The websocket connection has encountered an error");
    }

    send_object(object) {
        this.socket.send(JSON.stringify(object));
    }

}
export { WebSocketManager }