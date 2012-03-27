#!/usr/bin/python26
from flup.server.fcgi import WSGIServer
from placecorg import app

if __name__ == '__main__':
    WSGIServer(app).run()
