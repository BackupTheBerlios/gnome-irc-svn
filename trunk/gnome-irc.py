#!/usr/bin/python

import sys
import socket
import pygtk
pygtk.require('2.0')
import gtk, gtk.glade, gobject

class IRCNetwork:
    def __init__(self):
        self.server = "irc.freenode.net";
        self.port = 6667;

class IRCConnection:
    def __init__(self, identity, network, buffer):
        self.network = network
        self.identity = identity
        self.buffer = buffer
        self.readbuffer = ""

    def connect(self):
        self.socket = socket.socket()
        gobject.io_add_watch(self.socket, gobject.IO_IN, self.data_in)
        self.socket.connect((self.network.server, self.network.port))
        self.socket.send("NICK %s\r\n" % self.identity.nick)
        self.socket.send("USER %s %s bla :%s\r\n" % (self.identity.ident,
                    self.network.server, self.identity.realname))
    
    def data_in(self, socket, condition):
        self.readbuffer += socket.recv(1024)
        lines = self.readbuffer.split("\n")
        self.readbuffer = lines.pop()
        for line in lines:
            sys.stdout.write(line + "\n")
            if line.startswith(":"):
                # we have a prefix
                prefix, command, params = line[1:].split(None, 2)
            else:
                command, params = line.split(None, 1)
                prefix = ""
            lparams = []
            while len(params) > 0 and " " in params and not params.startswith(":"):
                param, params = params.split(None, 1)
                lparams.append(param)
            if params.startswith(":"):
                lparams.append(params[1:])
            else:
                lparams.append(params)
            sys.stdout.write("Prefix:\t%s\nCommand:\t%s\nParams:\t\t%s\n" % (prefix,
                        command, ", ".join(lparams)))
            self.buffer.insert(self.buffer.get_end_iter(), line + "\n")
        return True

    def send(self, line):
        self.socket.send(line + "\r\n")

class IRCIdentity:
    def __init__(self):
        self.nick = "ska-fans-python-client"
        self.ident = "ident"
        self.realname = "realname"
        
class MainWindow:
    def __init__(self):
        self.wTree = gtk.glade.XML("gnome-irc.glade", "window1")
        self.entry1 = self.wTree.get_widget("entry1")
        self.textview1 = self.wTree.get_widget("textview1")
        self.wTree.signal_autoconnect({ \
                "destroy": self.destroy, \
                "button1_clicked": self.button1_clicked \
                })
        self.network = IRCNetwork()
        self.identity = IRCIdentity()
        self.connection = IRCConnection(self.identity, self.network,
                self.textview1.get_buffer())
        self.connection.connect()

    def destroy(self, widget, data = None):
        gtk.main_quit()

    def button1_clicked(self, event, data = None):
        if self.entry1.get_text() != "":
            self.connection.send(self.entry1.get_text())
            self.entry1.set_text("")

    def main(self):
        gtk.main()

if __name__ == "__main__":
    mainwindow = MainWindow()
    mainwindow.main()

