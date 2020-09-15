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

        this.connection_status_warning = document.getElementById("wswarning");

        this.connected = false;

        this.connect();

        setInterval(this.ping.bind(this), 2000);
        this.core.register_handler("message_ping", function(){});
    }

    ping() {
        if(this.connected) {
            this.send_object({
                "type": "ping"
            })
        }
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
        this.stop_connection_warning();
        this.core.send_event("ws_open");
    }

    onclose(event) {
        console.log(`The websocket connection has been closed.  Retrying connection in ${this.retry_timeout} seconds`);
        this.connected = false;
        this.start_connection_warning();
        setTimeout(this.connect.bind(this), this.retry_timeout * 1000);
        if(this.retry_timeout < 10) {
            this.retry_timeout += 1;
        }
    }

    onmessage(event) {
        let data = JSON.parse(event.data);
        this.core.send_event(`message_${data['type']}`, data);
    }

    onerror(event) {
        console.log("The websocket connection has encountered an error");
    }

    send_object(object) {
        this.socket.send(JSON.stringify(object));
    }

    start_connection_warning() {
        if(this.connection_status_warning_started) { return; }
        console.log(`Showing connection status warning in ${this.config['show_warning_timeout']}ms`);
        this.connection_status_warning_started = true;
        this.connection_status_warning_timeout = setTimeout(function() {
            this.connection_status_warning.className = "connectionstatuswarning";
        }.bind(this), this.config['show_warning_timeout']);
    }

    stop_connection_warning() {
        if(!this.connection_status_warning_started) { return; }
        console.log(`Stopping show connection status warning`);
        this.connection_status_warning.className = "connectionstatuswarning hidden";
        this.connection_status_warning_started = false;
        clearTimeout(this.connection_status_warning_timeout);
    }

}
export { WebSocketManager }