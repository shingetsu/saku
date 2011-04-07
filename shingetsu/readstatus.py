''' Read Status
    licence: same as saku.
'''
# $Id: $
__version__ = '$Revison: $'

import os

import config


class ReadStatus(object):
    '''
    ReadStatus['VirtualFileName'] = Cache.count
    Key is virtual file name that encoded UTF-8.
    '''

    path = config.read_status
    status = {}

    def __init__(self):
        self._load_status()

    def _load_status(self):
        """return True: successful
              return False: Failed
        """
        if not os.path.exists(self.path):
            return False
        f = open(self.path, "r")
        for line in f:
            vfile, count = line.split("<>")
            self.status[vfile] = int(count)
        f.close()
        return True

    def _save_status(self):
        f = open(self.path, "w")
        for count, vfile in enumerate(self.status):
            f.write(vfile + "<>" + str(count) + "\n")
            f.flush()
        f.close()

    def __getitem__(self, vfile):
        tmp = vfile.split("_")
        if  len(tmp) == 2 and tmp[1] != "":    # Is filename valid?
            return int(self.status[vfile])
        else:
            raise IndexError("Wrong filename")

    def __setitem__(self, vfile, count):
        tmp = vfile.split("_")
        if len(tmp) == 2 and tmp[1] != "":    # Is filename valid?
            self.status[vfile] = int(count)
        else:
            raise IndexError("Wrong filename")

    def __delitem__(self, vfile):
        tmp = vfile.split("_")
        if len(tmp) == 2 and tmp[1] != "":
            del self.status[vfile]
        else:
            raise IndexError("Wrong filename")

    def __len__(self):
        return len(self.status)

    def sync(self):
        self._save_status()

    def keys(self):
        return self.status.keys()
