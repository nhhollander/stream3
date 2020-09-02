/* Master file for the streaming server.  All dynamic components of the page
 * are loaded and controlled from here. */

import { Auth } from "./js/auth.js"
import { Messages } from "./js/messages.js"
import { VideoPlayer } from "./js/player.js"
import { WebSocketManager } from "./js/websocket.js"
import { ControlBar } from "./js/controlbar.js"

function stream_init() {
    let config = {
        "messages": {},
        "websocket": {
            "address": "wss://raspberrypi.internal.crumbcake.cc:4433",
            "show_warning_timeout": 4000
        }
    }
    window.core = new Core(config); // Save to global for debugging
}
window.addEventListener("load", stream_init)

/*
 * Core class.
 * This class represents the entire application.  This is a useful comment.
 */
class Core {
    
    constructor(config) {
        this.config = config;

        this.handlers = {}

        this.auth = new Auth(this.config, this);
        this.messages = new Messages(this.config, this);
        this.player = new VideoPlayer(this.config, this);
        this.websocket = new WebSocketManager(this.config, this);
        this.controlbar = new ControlBar(this.config, this);

    }

    register_handler(event, callback) {
        if(!(event in this.handlers)) {
            this.handlers[event] = []
        }
        this.handlers[event].push(callback)
    }

    send_event(event, data=null) {
        if(!(event in this.handlers)) {
            console.error(`Warning: Event [${event}] not handled!`);
            return;
        }
        for(const handler of this.handlers[event]) {
            // TODO: Catch exceptions maybe
            handler(data);
        }
    }
}