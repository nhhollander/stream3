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

        /*setInterval(function() {
            this.messagebar.scrollBy(0,100);
        }.bind(this), 3);*/
    }

    strip_html(unsafe) {
        let t = document.createElement("div");
        t.innerText = unsafe;
        return t.innerHTML;
    }

    handle_message(data) {
        this.show_message(data["from"], data["class"], data["message"], data["allowhtml"], data["duration"]);
    }

    show_message(from, message_class, text, allow_html, duration) {
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
        this.messagebar.scrollBy(0,1000);
        setTimeout(function() {
            /* After a brief pause, calculate the height of this element.  This
             * allows the element to be smoothly shrunk out of existence at the
             * end of its life */
            let height = this.getBoundingClientRect().height;
            let cstyle = getComputedStyle(this);
            height += parseInt(cstyle['margin-bottom']);
            this.style.setProperty('--msgyeet', `${height*-1}px`);
        }.bind(message), 100);
        // Hide
        console.log(`Showing message for [${duration}] ${Math.max(duration,200)}ms`);
        setTimeout(function() {
            this.className += " hidden";
            setTimeout(function() {
                this.parentElement.removeChild(this);
            }.bind(message), 2000);
        }.bind(message), Math.max(duration, 200));
    }

}
export { Messages }