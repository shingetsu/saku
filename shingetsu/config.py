"""Saku Configuration.
"""
#
# Copyright (c) 2005-2024 shinGETsu Project.
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

import re
import os.path
import configparser

def _get_value(parser, section, key, default, vtype=''):
    """Get config value or default value."""
    try:
        if vtype == 'int':
            return parser.getint(section, key)
        elif vtype == 'path':
            return os.path.expanduser(parser.get(section, key))
        elif vtype == 'boolean':
            return parser.getboolean(section, key)
        else:
            return parser.get(section, key)
    except (configparser.NoOptionError, configparser.NoSectionError):
        return default

def _get_version():
    """Get Saku version for useragent and servername.
    """
    version = '5.0.0'
    version_file = os.path.join(docroot, file_dir, 'version.txt')
    if os.path.isfile(version_file):
        try:
            f = open(version_file, encoding='utf-8', errors='replace')
            version += '; git/%s' % f.read().strip()
            f.close()
        except (IOError, OSError):
            pass
    return 'shinGETsu/0.7 (Saku/%s)' % version


# External config files.
_extconf = configparser.ConfigParser()
_extconf.read(['file/saku.ini',
               '/usr/local/etc/saku/saku.ini',
               '/etc/saku/saku.ini',
               os.path.expanduser('~/.saku/saku.ini')])

# Application types
types = ("thread",)

bind_addr = _get_value(_extconf, 'Network', 'bind_addr', '')
port = _get_value(_extconf, 'Network', 'port', 8000, 'int')
dat_port = _get_value(_extconf, 'Network', 'dat_port', 8001, 'int')
max_connection = _get_value(_extconf, 'Network', 'max_connection', 20, 'int')
use_x_forwarded_for = _get_value(_extconf, 'Network', 'use_x_forwarded_for', False, 'boolean') # set true if behind a reverse proxy.

docroot = _get_value(_extconf, 'Path', 'docroot', './www', 'path')
log_dir = _get_value(_extconf, 'Path', 'log_dir', './log', 'path')
run_dir = _get_value(_extconf, 'Path', 'run_dir', '../run', 'path')
file_dir = _get_value(_extconf, 'Path', 'file_dir', '../file', 'path')
cache_dir = _get_value(_extconf, 'Path', 'cache_dir', '../cache', 'path')
template_dir = _get_value(_extconf, 'Path', 'template_dir',
                          '../template', 'path')
spam_list = _get_value(_extconf, 'Path', 'spam_list',
                       '../file/spam.txt', 'path')
initnode_list = _get_value(_extconf, 'Path', 'initnode_list',
                       '../file/initnode.txt', 'path')
node_allow = _get_value(_extconf, 'Path', 'node_allow',
                        '../file/node_allow.txt', 'path')
node_deny = _get_value(_extconf, 'Path', 'node_deny',
                        '../file/node_deny.txt', 'path')
apache_docroot = _get_value(_extconf, 'Path', 'apache_docroot',
                       '/var/local/www/shingetsu', 'path')
archive_dir = _get_value(_extconf, 'Path', 'archive_dir',
                       '/var/local/www/archive', 'path')

admin = _get_value(_extconf, 'Gateway', 'admin', r'^127')
friend = _get_value(_extconf, 'Gateway', 'friend', r'^127')
visitor = _get_value(_extconf, 'Gateway', 'visitor', r'.')
server_name = _get_value(_extconf, 'Gateway', 'server_name', '')
gateway_protocol = _get_value(_extconf, 'Gateway', 'protocol', 'http')
tag_size = _get_value(_extconf, 'Gateway', 'tag_size', 20, 'int')
rss_range = _get_value(_extconf, 'Gateway', 'rss_range', 3*24*60*60, 'int')
top_recent_range = _get_value(_extconf, 'Gateway',
                              'top_recent_range', 3*24*60*60, 'int')
recent_range = _get_value(_extconf, 'Gateway', 'recent_range',
                          31*24*60*60, 'int')
record_limit = _get_value(_extconf, 'Gateway', 'record_limit', 2048, 'int')
proxy_destination = _get_value(_extconf, 'Gateway', 'proxy_destination', '')
archive_uri = _get_value(_extconf, 'Gateway', 'archive_uri',
                         'https://archive.shingetsu.info/')
enable2ch = _get_value(_extconf, 'Gateway', 'enable_2ch', False, 'boolean')
re_admin = re.compile(admin)
re_friend = re.compile(friend)
re_visitor = re.compile(visitor)
template_suffix = '.txt'


# Seconds; 0 for infinity
save_record = {}
save_size = {}      # It is not seconds, but number.
get_range = {}
sync_range = {}
save_removed = {}
for type in types:
    ctype = 'Application %s' % type.capitalize()
    save_record[type] = \
        _get_value(_extconf, ctype, 'save_record', 0, 'int')
    save_size[type] = \
        _get_value(_extconf, ctype, 'save_size', 1, 'int')
    get_range[type] = \
        _get_value(_extconf, ctype, 'get_range', 31*24*60*60, 'int')
    sync_range[type] = \
        _get_value(_extconf, ctype, 'sync_range', 10*24*60*60, 'int')
    save_removed[type] = \
        _get_value(_extconf, ctype, 'save_removed', 50*24*60*60, 'int')

thread_page_size = _get_value(_extconf,
                              'Application Thread',
                              'page_size', 50, 'int')
thumbnail_size = _get_value(_extconf,
                            'Application Thread',
                            'thumbnail_size', None, '')
force_thumbnail = _get_value(_extconf,
                             'Application Thread',
                             'force_thumbnail', False, 'boolean')

client_cycle = 5*60         # Seconds; Access client.cgi
ping_cycle = 5*60           # Seconds; Check nodes
sync_cycle = 5*60*60        # Seconds; Check cache
init_cycle = 20*60          # Seconds; Check initial node
update_range = 24*60*60     # Seconds
wait_update = 10            # Seconds
time_error = 60             # Seconds
search_timeout = 10*60      # Seconds
timeout = 20                # Seconds; Timeout for TCP
get_timeout = 2*60          # Seconds; Timeout for /get
client_timeout = 30*60      # Seconds; client_timeout < sync_cycle
tk_save_warn = 5*60         # Seconds
retry = 5                   # Times; Common setting
retry_join = 2              # Times; Join network
nodes = 5                   # Nodes keeping in node list
share_nodes = 5             # Nodes having the file
search_depth = 30           # Search node size
tiedfile_cache_size = 30

broadcast = "../tool/broadcast.py"  # Broadcast script path

rss = "1"                                   # RSS version; must be "1"
language = "en"                             # Language code (see RFC3066)

# regexp
robot = r"Google|bot|Yahoo|archiver|Wget|Crawler|Yeti|Baidu"

dnsname = _get_value(_extconf, 'Network', 'dnsname', '')
                                        # Server name for shinGETsu protocol
query_separator = "/"                   # Must be "/"
root_path = "/"                         # path of URI for root

motd = file_dir + "/motd.txt"
node = run_dir + "/node.txt"
search = run_dir + "/search.txt"
update = run_dir + "/update.txt"
recent = run_dir + "/recent.txt"
client_log = run_dir + "/client.txt"
use_client_log = _get_value(_extconf,'Path','use_client_log', True, 'boolean')

lock = run_dir + "/lock.txt"
search_lock = run_dir + "/touch.txt"
admin_search = run_dir + "/admintouch.txt"
admin_sid = run_dir + "/sid.txt"
pid = run_dir + "/pid.txt"
lookup = run_dir + "/lookup.txt"
taglist = run_dir + "/tag.txt"
sugtag = run_dir + "/sugtag.txt"
read_status = run_dir + '/readstatus.txt'

server = root_path + "server.cgi"
client = root_path + "client.cgi"
gateway = root_path + "gateway.cgi"
thread_cgi = root_path + "thread.cgi"
admin_cgi = root_path + "admin.cgi"
xsl = root_path + "rss1.xsl"
root_index = _get_value(_extconf, 'Gateway', 'root_index', gateway)

application = {"thread": thread_cgi}

title_limit = 30                        # Charactors

# asis, md5, sha1, sha224, sha256, sha384, or sha512
cache_hash_method = 'asis'

version = _get_version()

init_node = ['node.shingetsu.info:8000/server.cgi']

flags = []          # It is set by script
