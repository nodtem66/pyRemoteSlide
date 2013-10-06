from tornado import web, ioloop
from sockjs.tornado import SockJSConnection, SockJSRouter
import sys
import os
import socket
from time import sleep
from ctypes import windll

PORT = 9999


class IndexHandler(web.RequestHandler):
    def get(self):
        if "main.js" in self.request.path:
            self.set_header("Content-Type", "application/javascript")
            html = self.render_string("static/main.js", host=HOST, port=PORT)
            self.finish(html)
        else:
            self.render("client.html")


class EchoConnection(SockJSConnection):

    def __init__(self, session):
        SockJSConnection.__init__(self, session)
        self.mode = 0
        self.drawmode = False
        self.isRotate = False
        self.x = 0
        self.y = 0

    def switchMode(self):
        self.mode = (self.mode + 1) % 3
        print 'change to', self.mode
        self.send(self.mode)

    def on_message(self, message):
        if message[:1] == u"0":
            x, y = message.split(":")[1:]
            self.x, self.y = int(x), int(y)
        elif message[:1] == u"1":
            if self.mode != 1:
                #move mouse
                x, y = message.split(":")[1:]
                windll.user32.mouse_event(0x0003 if self.mode == 2 else 0x0001,
                                          (int(x) - int(self.x)),
                                          (int(y) - int(self.y)),
                                          0,
                                          0)
                self.x, self.y = int(x), int(y)
        elif message[:1] == u"2":
            if self.mode == 2:
                    windll.user32.mouse_event(0x0004, 0, 0, 0, 0)
            if self.isRotate:
                    self.switchMode()
                    self.isRotate = False
            elif self.mode == 1:
                if int(message.split(":")[1]) >= 0:
                    #press next button 0x25
                    #print "next"
                    windll.user32.keybd_event(0x25, 0x45, 0x0001, 0)
                    sleep(0.000001)
                    windll.user32.keybd_event(0x25, 0x45, 0x0003, 0)
                else:
                    #press prev button 0x27
                    #print "prev"
                    windll.user32.keybd_event(0x27, 0x45, 0x0001, 0)
                    sleep(0.000001)
                    windll.user32.keybd_event(0x27, 0x45, 0x0003, 0)
            
        elif message[:1] == u"3":
            if self.mode == 0:
                windll.user32.mouse_event(0x0008, 0, 0, 0, 0)
                sleep(0.000001)
                windll.user32.mouse_event(0x0010, 0, 0, 0, 0)
        elif message[:1] == u"4":
            if self.mode == 0:
                windll.user32.mouse_event(0x0002, 0, 0, 0, 0)
                sleep(0.000001)
                windll.user32.mouse_event(0x0004, 0, 0, 0, 0)
        elif message[:1] == u"5":
            self.isRotate = True
        


def getLocalIPAdress():
    for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
        if not ip.startswith("127."):
            return ip
    return "127.0.0.1"

if __name__ == "__main__":
    global HOST
    global SCRIPT_PATH

    HOST = getLocalIPAdress()
    SCRIPT_PATH = os.path.dirname(sys.argv[0])
    static_path = SCRIPT_PATH + os.sep + "static"

    EchoRouter = SockJSRouter(EchoConnection, "/echo")
    handlers = [
        (r"/static/main.js", IndexHandler),
        (r"/static/(.*)", web.StaticFileHandler, {"path": static_path}),
        (r"/", IndexHandler)
    ]
    handlers += EchoRouter.urls

    app = web.Application(handlers)

    app.listen(PORT)
    print "server started {}:{}".format(HOST, PORT)
    ioloop.IOLoop.instance().start()
