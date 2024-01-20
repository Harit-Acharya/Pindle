#!/usr/bin/python3
from __future__ import with_statement

import io
from pprint import pprint
import datetime
from asyncio import Queue, QueueFull
from tempfile import NamedTemporaryFile
from time import time, sleep
import sys
sys.path.insert(0,'/etc/Pindle/OneDrive/')
import onedrive_auth
from os.path import basename, dirname, join
import stat
import errno
import logging
import onedrivesdk
from multiprocessing import Process
from threading import Lock, Event, Thread
from collections import defaultdict, deque
import os
import http.client as http
import requests
from urllib3.exceptions import RequestError
import fuse
from fuse import FuseError


fuse.fuse_python_api = (0, 2)

# Logging
mail = sys.argv[1]
logger = logging.getLogger(__name__)
handler = logging.FileHandler('/var/log/Pindle/OneDrive/{}_onedrive.log'.format(mail))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

def response_chunk(api, path, offset, length):
    ok_codes = [http.PARTIAL_CONTENT]
    end = offset + length - 1
    logger.info('chunk o %d l %d' % (offset, length))
    url = api.base_url + 'drive/root%3A' + path + '%3A/content'
    headers={'Range': 'bytes=%d-%d' % (offset, end), 'Authorization': 'Bearer %s' % api.auth_provider.access_token}
    r = requests.get(url, stream=True, headers=headers)
    if r.status_code not in ok_codes:
        raise requests.RequestException(r.status, r.text)

    return r

class ReadProxy(object):
    """Dict of stream chunks for consecutive read access of files."""

    def __init__(self, api, open_chunk_limit, timeout, dl_chunk_size):
        self.api = api
        self.lock = Lock()
        self.files = defaultdict(lambda: ReadProxy.ReadFile(open_chunk_limit, timeout, dl_chunk_size))

    class StreamChunk(object):
        """StreamChunk represents a file node chunk as a streamed ranged HTTP response
        which may or may not be partially read."""

        __slots__ = ('offset', 'r', 'end')

        def __init__(self, api, path, offset, length, **kwargs):
            self.offset = offset
            """the first byte position (fpos) available in the chunk"""

            self.r = response_chunk(api, path, offset, length)
            """:type: requests.Response"""

            self.end = offset + int(self.r.headers['content-length']) - 1
            """the last byte position (fpos) contained in the chunk"""

        def has_byte_range(self, offset, length):
            """Tests whether chunk begins at **offset** and has at least **length** bytes remaining."""
            logger.info('s: %d-%d; r: %d-%d'
                         % (self.offset, self.end, offset, offset + length - 1))
            if offset == self.offset and offset + length - 1 <= self.end:
                return True
            return False

        def get(self, length):
            """Gets *length* bytes beginning at current offset.
            :param length: the number of bytes to get
            :raises: Exception if less than *length* bytes were received \
             but end of chunk was not reached"""

            b = next(self.r.iter_content(length))
            logger.debug("type of ")
            self.offset += len(b)
            logger.debug("the b is %d offset %d and end is %d and length %d" % (len(b),self.offset,self.end,length))

            if len(b) < length and self.offset <= self.end:
                logger.warning('Chunk ended unexpectedly.')
                raise Exception
            return b

        def close(self):
            """Closes connection on the stream."""
            self.r.close()

    class ReadFile(object):
        """Represents a file opened for reading.
        Encapsulates at most :attr:`MAX_CHUNKS_PER_FILE` open chunks."""

        __slots__ = ('chunks', 'access', 'lock', 'timeout', 'dl_chunk_size')

        def __init__(self, open_chunk_limit, timeout, dl_chunk_size):
            self.dl_chunk_size = dl_chunk_size
            self.chunks = deque(maxlen=open_chunk_limit)
            self.access = time()
            self.lock = Lock()
            self.timeout = timeout

        def get(self, api, path, offset, length, total):
            """Gets a byte range from existing StreamChunks"""
            with self.lock:
                i = len(self.chunks) - 1
                while i >= 0:
                    c = self.chunks[i]
                    if c.has_byte_range(offset, length):
                        try:
                            bytes_ = c.get(length)
                        except:
                            logger.debug("except block")
                            self.chunks.remove(c)
                        else:
                            return bytes_
                    i -= 1

            try:
                with self.lock:
                    #4 th parameter was self.dl_chunk_size but i changed it to length
                    logger.debug("%d"%offset)
                    chunk = ReadProxy.StreamChunk(api, path, offset, length, timeout=self.timeout)
                    if len(self.chunks) == self.chunks.maxlen:
                        self.chunks[0].close()

                    self.chunks.append(chunk)
                    return chunk.get(length)
            except Exception as e:
                logger.error(e)

        def clear(self):
            """Closes chunks and clears chunk deque."""
            with self.lock:
                for chunk in self.chunks:
                    try:
                        chunk.close()
                    except:
                        pass
                self.chunks.clear()

    def get(self, path, offset, length, total):
        with self.lock:
            f = self.files[path]
        return f.get(self.api, path, offset, length, total)

    def invalidate(self):
        pass

    def release(self, path):
        with self.lock:
            f = self.files.get(path)
        if f:
            f.clear()

class onedrive():
    #class properties
    def __init__(self):
        self.client = onedrive_auth.LoadSession(mail)
        self.listofdir = defaultdict(list)
        self.name_to_id = {"/":"root"}
        self.fileorfolder = {'folder': ['/'], 'file': []}
        logger.info("creating object")

class DriveStat(fuse.Stat):
    def __init__(self, **kw):
        """
        The following stat structure members are implemented.
        """
        super().__init__(**kw)
        self.st_mode  = 0      # (protection bits)
        self.st_ino   = 0      # (inode number)
        self.st_dev   = 0      # (device)
        self.st_nlink = 0      # (number of hard links)
        self.st_uid   = 0      # (user ID of owner)
        self.st_gid   = 0      # (group ID of owner)
        self.st_size  = 0      # (size of file, in bytes)
        self.st_atime = 0      # (time of most recent access)
        self.st_mtime = 0      # (time of most recent content modification)
        self.st_ctime = 0      # (time of most recent metadata change)


class OnedriveFs(fuse.Fuse):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.rp = ReadProxy(authed_usr.client, 2**48, 1, 2**48)
        #self.wp = WriteProxy(authed_usr.client,)
        self.fh = 1
        """file handle counter\n\n :type: int"""
        self.fh_lock = Lock()
        self.handles = {}

    def getattr(self, path, fh=None):
        logger.info("[getattr] (path=%s)" % path)
        st = DriveStat()
        if path in authed_usr.fileorfolder['folder']:
            st.st_mode = stat.S_IFDIR | 0o755
            st.st_nlink = 2
        elif path in authed_usr.fileorfolder['file']:
            st.st_mode = stat.S_IFREG | 0o666
            st.st_nlink = 1
            st.st_size = authed_usr.client.item(path=path).get().size
        else:
            return -errno.ENOENT
        return st

    def readdir(self, path, offset):
        try:
            #   authed_usr.update("root")
            logger.info("[readdir] (path=%s, offset=%s)" % (path, offset))
            childrens = ['.','..']
            items_iter = authed_usr.client.item(id=authed_usr.name_to_id.get(path)).children.get()
            logger.debug("got childrens")
            for item in items_iter:
                logger.debug("item = {}".format(item.name))
                childrens.append(item.name)
                if item.folder is None:
                    authed_usr.fileorfolder['file'].append(join(path,item.name))
                else:
                    authed_usr.fileorfolder['folder'].append(join(path,item.name))
                    authed_usr.name_to_id[join(path,item.name)] = item.id

            logger.debug(authed_usr.fileorfolder)
            logger.debug(authed_usr.listofdir)
            authed_usr.listofdir[path] = childrens

            res = authed_usr.listofdir.get(path)
            for directory in res:
                yield fuse.Direntry(directory)
        except:
            pass

    def open(self, path, flags):
        logger.debug("[open] %s" %path)
        pass

    def read(self, path, length, offset):
        """Read ```length`` bytes from ``path`` at ``offset``."""
        logger.debug("[read] (path=%s, length=%s, offset=%s)" % (path, length, offset))

        item = authed_usr.client.item(path=path).get()
        if not item:
            raise fuse.FuseError(errno.ENOENT)

        if item.size <= offset:
            return b''

        if item.size < offset + length:
            length = item.size - offset

        return self.rp.get(path, offset, length, item.size)

    def rmdir(self, path):
        logger.debug("[Removedir] (path=%s)" % path)
        if path not in authed_usr.fileorfolder['folder']:
            logger.debug("this is not folder")
            raise fuse.FuseError(errno.ENOTDIR)
        elif authed_usr.listofdir.get(path) != []:
            logger.debug("this is not empty")
            raise fuse.FuseError(errno.ENOTEMPTY)
        authed_usr.client.item(path=path).delete()
        del authed_usr.listofdir[path]
        authed_usr.listofdir[dirname(path)].remove(basename(path))

    def mkdir(self, path, mode):
        logger.debug("[mkdir] in path=%s %d" % (path,mode))
        item = onedrivesdk.Item()
        item.name = basename(path)
        item.folder = onedrivesdk.Folder()
        authed_usr.client.item(path=dirname(path)).children.add(item)
        authed_usr.fileorfolder['folder'].append(path)
        authed_usr.listofdir[path] = []
        authed_usr.listofdir[dirname(path)].append(item.name)

    def rename(self, old, new):
        if old == new:
            return
        old_id = authed_usr.client.item(path=old).get().id
        renamed_item = onedrivesdk.Item()
        renamed_item.name = basename(new)
        renamed_item.id = old_id
        authed_usr.client.item(id=renamed_item.id).update(renamed_item)
        authed_usr.listofdir[dirname(old)].remove(basename(old))
        authed_usr.listofdir[dirname(new)].append(basename(new))
        if old in authed_usr.fileorfolder['folder']:
            authed_usr.fileorfolder['folder'].remove(old)
            authed_usr.fileorfolder['folder'].append(new)
        else:
            authed_usr.fileorfolder['file'].remove(old)
            authed_usr.fileorfolder['file'].append(new)

    def create(self, path, mode, fi=None):
        logger.debug("[create] (path={} and dirname = {})".format(path, dirname(path)))
        if dirname(path) not in authed_usr.fileorfolder['folder']:
            raise FuseError(errno.ENOTDIR)
        with NamedTemporaryFile() as tmp:
            logger.debug("create file")
            authed_usr.client.item(path=dirname(path)).children[basename(path)].upload(tmp.name)
        authed_usr.listofdir[dirname(path)].append(basename(path))
        authed_usr.fileorfolder['file'].append(path)
        logger.debug("File created in cloud")

    def write(self, path, buf, offset):
        logger.debug("[write] (path={}) ".format(path))
        # Create/modify file, upload it with tmp name
        with NamedTemporaryFile() as tmp:
            logger.debug("[inside tmp write]")
            if basename(path) not in authed_usr.fileorfolder['file']:
                url = authed_usr.client.base_url + 'drive/root%3A' + path + '%3A/content'
                headers = {'Authorization': 'Bearer %s' % authed_usr.client.auth_provider.access_token}
                r = requests.get(url, stream=True, headers=headers)
                with open(tmp.name, 'wb') as fd:
                    for chunk in r.iter_content(2**16):
                        fd.write(chunk)
                logger.debug("[write to tmp completed]")
            logger.debug('offset writing')
            if offset: tmp.seek(offset)
            tmp.write(buf)
            tmp.flush()
            logger.debug('tmp flush completed')
            authed_usr.client.item(path=dirname(path)).children[basename(path)].upload(tmp.name)
            logger.debug('writing to cloud done')
        return len(buf)

    def truncate(self, path, size):
        logger.debug("[truncating]")
        with NamedTemporaryFile() as tmp:
            url = authed_usr.client.base_url + 'drive/root%3A' + path + '%3A/content'
            headers = {'Authorization': 'Bearer %s' % authed_usr.client.auth_provider.access_token}
            r = requests.get(url, stream=True, headers=headers)
            with open(tmp.name, 'wb') as fd:
                for chunk in r.iter_content(2**16):
                    fd.write(chunk)
            logger.debug("[write to tmp completed]")
            tmp.truncate(size)
            authed_usr.client.item(path=dirname(path)).children[basename(path)].upload(tmp.name)
            logger.debug("completed this opt")

    def flush(self, path, fi=None):
        # flush would sync the file back to Google Drive,
        # if not done yet
        return

    def chmod(self, path, mode):
        """Not implemented."""
        pass

    def chown(self, path, uid, gid):
        """Not implemented."""
        pass

    def utimens(self, path, times, *args):
        """Not implemented."""
        pass

    def release(self, path, fh):
        item = None
        try:
            if path in (authed_usr.fileorfolder['folder'] or authed_usr.fileorfolder['file']):
                item = True
        except:
            item = None
        if item:
            self.rp.release(path)
        else:
            raise fuse.FuseError(errno.ENOENT)

    def unlink(self, path):
        if path in authed_usr.fileorfolder['folder']:
            raise FuseError(errno.EISDIR)
        else:
            authed_usr.client.item(path=path).delete()

if __name__ == '__main__':
    authed_usr = onedrive()
   # authed_usr.update("root")
    onedrivefs = OnedriveFs(version = '%prog ' + '0.0.1',
               usage = 'Onedrive filesystem ' + fuse.Fuse.fusage,
               dash_s_do = 'setsingle')
    onedrivefs.parse(errex = 1)
    onedrivefs.flags = 0
    onedrivefs.main()
