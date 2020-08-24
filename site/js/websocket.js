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
    }

    onopen(event) {
        console.log("The websocket connection has been opened");
        this.retry_timeout = 1;
        this.connected = true;
        this.core.send_event("ws_open");
    }

    onclose(event) {
        console.log(`The websocket connection has been closed.  Retrying connection in ${this.retry_timeout} seconds`);
        this.connected = false;
        setTimeout(this.connect.bind(this), this.retry_timeout * 1000);
        if(this.retry_timeout < 10) {
            this.retry_timeout += 1;
        }
    }

    onmessage(event) {
        console.log("A websocket message has been received");
    }

    onerror(event) {
        console.log("The websocket connection has encountered an error");
    }

}
export { WebSocketManager }