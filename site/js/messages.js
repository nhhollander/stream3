/*
 * Message management class.
 * Messages that are shown in the corner of the interface are generated using
 * this class.
 */
class Messages {

    constructor(config, core) {
        this.config = config['messages'];
        this.core = core;

        this.messagebar = document.getElementById("messagebar");

        this.core.register_handler("message_message", this.handle_message.bind(this));

        setInterval(function() {
            this.messagebar.scrollBy(0,1);
        }.bind(this), 3);
    }

    strip_html(unsafe) {
        let t = document.createElement("div");
        t.innerText = unsafe;
        return t.innerHTML;
    }

    handle_message(data) {
        this.show_message(data["from"], data["class"], data["message"], data["allowhtml"]);
    }

    show_message(from, message_class, text, allow_html) {
        // Create the message
        let message = document.createElement("div");
        message.className = `message message_${message_class}`;
        let head = document.createElement("div");
        head.className = "from";
        head.innerText = from;
        message.appendChild(head);
        let body = document.createElement("div");
        body.className = "body";
        if(allow_html) {
            body.innerHTML = text;
        } else {
            body.innerText = text;
        }
        message.appendChild(body);
        this.messagebar.appendChild(message);
    }

}
export { Messages }