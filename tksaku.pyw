#!/usr/bin/python
#
# tksaku.pyw - shinGETsu clone with Tk interface.
# Copyright (c) 2005-2009 shinGETsu Project.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHORS AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHORS OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#
# $Id$
#

import locale
import re
import os
import sys
import time
from threading import Thread
from Tkinter import *
from ScrolledText import ScrolledText

import shingetsu.daemon as daemon
import shingetsu.config as config

__version__ = "$Revision$"

class Browser(Thread):
    def run(self):
        import webbrowser
        webbrowser.open("http://localhost:%d/" % config.port)

class TkSaku(Frame):
    def createWidgets(self):
        self.master.title(u"TkSaku")
        try:
            self.master.iconbitmap(os.path.join(config.docroot, "favicon.ico"))
        except TclError:
            pass

        self.TOP = Frame(self)
        self.TOP.pack(side=TOP)

        self.LABEL = Label(self.TOP, text="Saku/Tk")
        self.LABEL.pack(side=LEFT)

        self.BROWSE = Button(self.TOP, text="Browse", command=self.browse)
        self.BROWSE.pack(side=LEFT)

        self.STOP = Button(self.TOP, text="Stop", command=sys.exit)
        self.STOP.pack(side=LEFT)

        self.TEXT = ScrolledText(self, width=80, height=25, state=DISABLED)
        self.TEXT.pack(expand=True, fill=BOTH)

        self.STATUS = Entry(self, width=80)
        self.STATUS.insert(END, "Status: OK")
        self.STATUS.config(state=DISABLED)
        self.STATUS.pack(side=BOTTOM, fill=X)

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack(expand=True, fill=BOTH)
        self.createWidgets()

    def browse(self):
        b = Browser()
        b.start()

class Logger(daemon.Logger):

    """Save logs to /LOGDIR/%Y-%m-%d and output Tk textarea."""

    def __init__(self, logdir, textarea, statusbar, encoding = 'utf-8'):
        daemon.Logger.__init__(self, logdir)
        self.textarea = textarea
        self.statusbar = statusbar
        self.linesize = 0
        self.lastwarn = 0
        self.haswarn = False
        self.encoding = encoding

    def write(self, msg):
        daemon.Logger.write(self, msg)
        while config.tklog < self.linesize:
            self.linesize -= 1
            self.textarea.delete("1.0", "2.0")
        now = int(time.time())
        if not isinstance(msg, unicode):
            try:
                msg = unicode(msg, self.encoding, 'replace')
            except LookupError:
                self.encoding = 'utf-8'
                msg = unicode(msg, self.encoding, 'replace')
        self.linesize += len(re.findall('\n', msg))
        self.textarea.config(state=NORMAL)
        self.textarea.insert(END, msg)
        lmsg = msg.lower()
        if (lmsg.find('warn') >= 0) or (lmsg.find('error') >= 0):
            self.lastwarn = now
            self.haswarn = True
            self.statusbar.config(state=NORMAL)
            self.statusbar.delete('0', END)
            self.statusbar.insert(END, msg)
            self.statusbar.config(state=DISABLED)
        elif self.haswarn and (self.lastwarn + config.tk_save_warn < now):
            self.haswarn = False
            self.statusbar.config(state=NORMAL)
            self.statusbar.delete('0', END)
            self.statusbar.insert(END, 'Status: OK')
            self.statusbar.config(state=DISABLED)
        self.textarea.config(state=DISABLED)
        self.textarea.yview(END)

    def flush(self):
        pass

    def close(self):
        self.output.close()


class DaemonStarter(Thread):
    def __init__(self, daemon):
        Thread.__init__(self)
        self.daemon = daemon

    def run(self):
        self.daemon.start_daemon()


def set_logger(textarea, statusbar):
    logfile = os.path.join(os.getcwd(), config.log_dir)
    logger = Logger(logfile, textarea, statusbar,
                    locale.getpreferredencoding())
    sys.stderr = logger
    sys.stdout = logger

def main():
    try:
        daemon.setup()
        app = TkSaku()
        set_logger(app.TEXT, app.STATUS)
        try:
            d = DaemonStarter(daemon)
            d.start()
            app.mainloop()
        finally:
            daemon.stop_daemon()
    except KeyboardInterrupt:
        sys.exit()

if __name__ == "__main__":
    main()
