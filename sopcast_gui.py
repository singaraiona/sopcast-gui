#!/usr/bin/env python2

import sys
import os
import subprocess
import time
import string

import gtk
import gobject
import pygtk

pygtk.require('2.0')

class MPlayer:
    def __init__(self, path, draw, show_output=True):
        self.path = path
        self.draw = draw
        self.fifo = "/tmp/%s.%d" % (os.path.basename(__file__), time.time())

        # Start mplayer in draw
        cmd = string.split("mplayer -slave -wid %d -input file=%s" % \
                (self.draw.window.xid, self.fifo))
        cmd.append(self.path)
        if show_output:
            process = subprocess.Popen(cmd)
        else:
            self.devnull = open(os.devnull)
            process = subprocess.Popen(cmd, stdout=self.devnull, \
                    stderr=self.devnull)

        self.pid = process.pid

    def __enter__(self):
        os.mkfifo(self.fifo)
        return self

    def __exit__(self, ext_type, exc_value, traceback):
        if hasattr(self, "devnull"):
            self.devnull.close()
        os.unlink(self.fifo)

    # Send cmd to mplayer via fifo
    def exe(self, cmd, *args):
        if not self.pid: return
        full_cmd = "%s %s\n" % (cmd, string.join([str(arg) for arg in args]))
        with open(self.fifo, "w+") as fifo:
            fifo.write(full_cmd)
            fifo.flush()

class MPlayerWrapper:
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.draw = gtk.DrawingArea()
        self.mplayer = None
        self.setup_widgets()

    def setup_widgets(self):
        self.window.connect("destroy", gtk.main_quit)
        self.window.connect("key_press_event", self.key_press_event)
        self.draw.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("black"))
        self.draw.connect("configure_event", self.redraw)
        self.window.add(self.draw)
        self.window.show_all()

    def mplayer_exe(self, cmd, *args):
        if self.mplayer:
            self.mplayer.exe(cmd, *args)

    def key_press_event(self, widget, event, data=None):
        self.mplayer_exe("key_down_event", event.keyval)

    def redraw(self, draw, event, data=None):
        self.draw.queue_draw()

    def play(self, path):
        with MPlayer(path, self.draw, True) as self.mplayer:
            gobject.child_watch_add(self.mplayer.pid, gtk.main_quit)
            gtk.main()

if __name__ == "__main__":
    wrapper = MPlayerWrapper()
    wrapper.play(sys.argv[1])
