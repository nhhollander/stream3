/* Master file for the streaming server.  All dynamic components of the page
 * are loaded and controlled from here. */

import { Messages } from "./js/messages.js"
import { WebSocketManager } from "./js/websocket.js"

function stream_init() {
    let config = {
        "messages": {},
        "websocket": {
            "noconnect": true, // Debug
            "address": "wss://waffle.internal.crumbcake.cc:4433"
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
        this.messages = new Messages(this.config, this);
        this.websocket = new WebSocketManager(this.config, this);
    }
}