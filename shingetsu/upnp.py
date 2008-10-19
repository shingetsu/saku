'''UPnP module.
'''
#
# Copyright (c) 2005-2008 shinGETsu Project.
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

import re
import sys
import socket
from urllib import FancyURLopener
from urlparse import urlparse, urljoin
from xml.sax import parse, SAXParseException
from xml.sax.handler import ContentHandler

from compatible import StringIO

__version__ = "$Revision$"
__all__ = ["findrouter"]


def XML(fp):
    length = int(fp.info().getheader("Content-Length", -1))
    sio = StringIO(fp.read(length))
    fp.close()
    return sio


class Agent(FancyURLopener):
    def __init__(self, timeout=0):
        FancyURLopener.__init__(self, proxies={})
        if timeout:
            socket.setdefaulttimeout(timeout)

    def open(self, *args):
        f = FancyURLopener.open(self, *args)
        return XML(f)


class UPnPXMLHandler(ContentHandler):
    elements = ["URLBase", "service", "NewExternalIPAddress"]

    def __init__(self, contype):
        ContentHandler.__init__(self)
        self.items = {}
        self.contype = contype
        self.state = ""

    def startElement(self, name, attrs):
        if name in self.elements:
            self.state = name
        elif name == "serviceType":
            self.state = name
        elif (self.state == "serviceType/wan") and \
             ("wanserv" not in self.items) and \
             (name == "controlURL"):
            self.state = "serviceType/wan/controlURL"
        elif name.find("Response") > 0:
            self.items["hasresponce"] = True

    def endElement(self, name):
        if name in self.elements:
            self.state = ""

    def characters(self, contents):
        if self.state == "URLBase":
            self.items["urlbase"] = contents.strip()
        elif (self.state == "serviceType") and \
             (contents == "urn:schemas-upnp-org:service:%s:1" %
                          self.contype):
            self.state = "serviceType/wan"
        elif self.state == "serviceType/wan/controlURL":
           self.items["wanserv"] = contents.strip()
           self.state = ""
        elif self.state == "NewExternalIPAddress":
            self.items["wanipaddr"] = contents.strip()

class SOAPAgent(Agent):
    def soapaction(self, contype, command):
        return "urn:schemas-upnp-org:service:%s:1#%s" % (contype, command)

    def open(self, url, contype, command, args):
        """Post SOAP XML."""
        self.addheader("SoapAction",
                       self.soapaction(contype, command))
        query = self.mksoap(contype, command, args)
        return Agent.open(self, url, query)

    def mksoap(self, contype, command, elements):
        """Make SOAP XML using elements dictionary."""
        query = ['''<?xml version="1.0"?>
<SOAP-ENV:Envelope
    xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
    SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
<SOAP-ENV:Body>
<m:%s xmlns:m="urn:schemas-upnp-org:service:%s:1">''' %(command, contype)]

        for k in elements:
            query.append("  <%s>%s</%s>\n" % (k, elements[k], k))
        query.extend(('</m:%s>' % command,
                      '</SOAP-ENV:Body>',
                      '</SOAP-ENV:Envelope>'))
        return "\n".join(query) + "\r\n"


class Router(dict):
    """Router supporting UPnP."""

    def __init__(self, devicexml, contype, timeout=0):
        dict.__init__(self)
        self.devicexml = devicexml
        self.contype = contype
        self.timeout = timeout
        self.readdevice()
        #self.wan = self.getwan()

    def __str__(self):
        try:
            return self["urlbase"]
        except KeyError:
            return self.devicexml

    def readdevice(self):
        """Read device XML and search controlURL."""
        try:
            agent = Agent(timeout=self.timeout)
            xmlobject = agent.open(self.devicexml)
            handler = UPnPXMLHandler(self.contype)
            parse(xmlobject, handler)
            xmlobject.close()
        except (IOError, SAXParseException, socket.error, socket.timeout), err:
            sys.stderr.write("upnp %s: %s\n" % (self, err))
            return

        if "urlbase" in handler.items:
            self["urlbase"] = handler.items["urlbase"]
        else:
            tmp = urlparse(self.devicexml)
            self["urlbase"] = "%s://%s" % (tmp[0], tmp[1])
        if "wanserv" in handler.items:
            self["wanserv"] = urljoin(self["urlbase"],
                                      handler.items["wanserv"])
        else:
            self["wanserv"] = urljoin(self["urlbase"],
                                      "/upnp/service/WANPPPConnection")

    def soapopen(self, command, args):
        if "wanserv" not in self:
            sys.stderr.write("upnp do not get service controler\n")
            return None
        agent = SOAPAgent(timeout=self.timeout)
        f = agent.open(self["wanserv"], self.contype, command, args)
        return f

    def getwan(self):
        """Get external IP address."""
        try:
            xmlobject = self.soapopen("GetExternalIPAddress", {})
            handler = UPnPXMLHandler(self.contype)
            parse(xmlobject, handler)
            xmlobject.close()
            if "wanipaddr" in handler.items:
                return handler.items["wanipaddr"]
        except (IOError, SAXParseException, socket.error, socket.timeout), err:
            sys.stderr.write("upnp %s: %s\n" % (self, err))
            return None

    def sendsoap(self, command, args):
        try:
            xmlobject = self.soapopen(command, args)
            handler = UPnPXMLHandler(self.contype)
            parse(xmlobject, handler)
            xmlobject.close()
            return "hasresponce" in handler.items
        except (IOError, SAXParseException, socket.error, socket.timeout), err:
            sys.stderr.write("upnp %s: %s\n" % (self, err))
            return False

    def openport(self, port, protocol="TCP", description=""):
        try:
            if self.timeout:
                socket.setdefaulttimeout(self.timeout)
            localaddr = socket.gethostbyname(socket.gethostname())
        except (IOError, socket.error, socket.timeout), err:
            sys.stderr.write("upnp %s: %s\n" % (self, err))
            return False
        return self.sendsoap("AddPortMapping",
                             {"NewRemoteHost": "",
                             "NewExternalPort": port,
                             "NewProtocol": protocol,
                             "NewInternalPort": port,
                             "NewInternalClient": localaddr,
                             "NewEnabled": 1,
                             "NewPortMappingDescription": description,
                             "NewLeaseDuration": 0})

    def closeport(self, port, protocol="TCP"):
        return self.sendsoap("DeletePortMapping",
                             {"NewRemoteHost": "",
                              "NewExternalPort": port,
                              "NewProtocol": protocol})


class SSDP:
    """Search router device XML using multicast."""

    search_req = 'M-SEARCH * HTTP/1.1\r\n' + \
                 'MX: 3\r\n' + \
                 'HOST: 239.255.255.250:1900\r\n' + \
                 'MAN: "ssdp:discover"\r\n' + \
                 'ST: urn:schemas-upnp-org:service:%s:1\r\n' + \
                 '\r\n'
    bcast_addr = ("239.255.255.250", 1900)

    def __init__(self, timeout=5):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(timeout)

    def search(self, contype):
        self.sock.sendto(self.search_req % contype, self.bcast_addr)
        f = self.sock.makefile()
        location = ""
        try:
            for line in f:
                line = line.strip()
                found = re.search("Location:\s*(.+)", line, re.I)
                if found:
                    location = found.group(1)
                elif not line:
                    break
            self.sock.close()
        except socket.timeout:
            sys.stderr.write("upnp timed out\n")
        f.close()
        return location


def findrouter(timeout=5):
    """Search router supporting UPnP.

    If router is not found, return None.
    """
    ssdp = SSDP(timeout=timeout)
    for contype in ("WANPPPConnection", "WANIPConnection"):
        try:
            devicexml = ssdp.search(contype)
            if devicexml:
                return Router(devicexml, contype, timeout=timeout)
        except socket.error, err:
            sys.stderr.write("upnp error: %s\n" % err)
    return None


def test():
    port = int(sys.argv[1])
    router = findrouter()
    router.openport(port, "TCP", "test%d" % port)
    router.closeport(port, "TCP")

if __name__ == "__main__":
    test()
