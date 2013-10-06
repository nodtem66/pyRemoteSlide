//controller
(function(){

var sock = new SockJS('http://{{ host }}:{{ port }}/echo');
sock.onopen = function() {
    sock.send('Hi');
    alert('Start Touch!');
}
sock.onmessage = function(e) {
    if (e.data == '0') {
        document.body.style.background = "#EEEEEE";
    } else if (e.data == '2') {
        document.body.style.background = "#00CCFF";
    } else if (e.data == '1') {
        document.body.style.background = "#333333";
    }
}
sock.onclose = function() {
    alert('Bye');
}
var state = "NONE";

Hammer(document)
.on('dragstart', function(e) {
    g = e.gesture;
    state = "DRAG"
    sock.send('0:' + parseInt(g.deltaX) + ':' + parseInt(g.deltaY));
    g.preventDefault();
    return false;
})
.on('drag', function(e) {
    g = e.gesture;
    state = "DRAG"
    sock.send('1:' + parseInt(g.deltaX) + ':' + parseInt(g.deltaY));
    g.preventDefault();
    return false;
})
.on('dragend', function(e) {
    g = e.gesture;
    sock.send('2:' + parseInt(g.deltaX) + ':' + parseInt(g.deltaY));
    e.gesture.preventDefault();
    return false;
})
.on('hold', function(e) {
    sock.send('3');
    state = "HOLD";
    e.gesture.preventDefault();
    return false;
})
.on('touch', function(e) {
    state = "TOUCH"
    e.gesture.preventDefault();
    return false;
})
.on('release', function(e) {
    if (state == "TOUCH") {
        //tab
        sock.send('4');
    }
    state = "NONE";
    e.gesture.preventDefault();
    return false;
})
.on('transform', function(e) {
    sock.send('5')
    e.gesture.preventDefault();
    return false;  
});

}());