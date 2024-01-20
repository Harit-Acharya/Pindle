#!/usr/bin/python3
from __future__ import with_statement

import errno
import http.client as http
import io
import logging
import os
import stat
from collections import defaultdict, deque
from os.path import basename, dirname, join
from tempfile import NamedTemporaryFile
from threading import Lock
from time import time
import fuse
import requests
from fusepy import FuseOSError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import sys
sys.path.insert(0, '/etc/Pindle/GDrive/')
import googledrive_auth

fuse.fuse_python_api = (0, 2)

# Logging
MAIL = sys.argv[1]
logger = logging.getLogger(__name__)
handler = logging.FileHandler('/var/log/Pindle/GDrive/{}_gdrive.log'.format(MAIL))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


def response_chunk(api, path, offset, length):
    ok_codes = [http.PARTIAL_CONTENT]
    end = offset + length - 1
    id = authed_usr.file_list[path]['id']
    logger.info('chunk o %d l %d' % (offset, length))
    url = "https://www.googleapis.com/drive/v3/files/" + id + "?alt=media"
    headers={'Range': 'bytes=%d-%d' % (offset, end), 'Authorization': 'Bearer %s' % authed_usr.token}
    r = requests.get(url, stream=True, headers=headers)
    if r.status_code not in ok_codes:
        raise requests.RequestException(r.text)
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

class GDrive():
    def __init__(self):
        self.notvalid_mimetypes = ['application/vnd.google-apps.audio',
                                  'application/vnd.google-apps.document',
                                  'application/vnd.google-apps.drive-sdk',
                                  'application/vnd.google-apps.drawing',
                                  'application/vnd.google-apps.file',
                                  'application/vnd.google-apps.form',
                                  'application/vnd.google-apps.fusiontable',
                                  'application/vnd.google-apps.map',
                                  'application/vnd.google-apps.photo',
                                  'application/vnd.google-apps.presentation',
                                  'application/vnd.google-apps.script',
                                  'application/vnd.google-apps.shortcut',
                                  'application/vnd.google-apps.site',
                                  'application/vnd.google-apps.spreadsheet',
                                  'application/vnd.google-apps.unknown',
                                  'application/vnd.google-apps.video']
        print("authenticating")
        self.client,self.token = googledrive_auth.authenticate(MAIL)
        print("authentiated ")
        logger.debug("%s %s" % (self.client,self.token))
        self.file_list= defaultdict(dict)
        self.file_list['/'] = {'mimeType':'application/vnd.google-apps.folder'}

    def get_children(self,parent):
        query = "'{}' in parents".format(parent)
        children = []
        page_token = None
        while True:
            print("in loop")
            response = self.client.files().list(q=query,
                                        spaces='drive',
                                        fields='nextPageToken, files(id, name, size, mimeType)',
                                        pageToken=page_token).execute()
            for file in response.get('files', []):
                children.append(file)
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
        return children

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


class GoogleDriveFS(fuse.Fuse):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.rp = ReadProxy(authed_usr.client, 2 ** 48, 1, 2 ** 48)
        self.created = set()

    def getattr(self, path,fh=None):
        logger.info("[getattr] (path=%s)" % path)
        st = DriveStat()
        try:
            check = authed_usr.file_list[path]['mimeType']
        except:
            check = None

        if check == 'application/vnd.google-apps.folder':
            st.st_mode = stat.S_IFDIR | 0o755
            st.st_nlink = 2
        elif check != None:
            st.st_mode = stat.S_IFREG | 0o644
            st.st_nlink = 1
            st.st_size = int(authed_usr.file_list[path]['size'])
        else:
             return -errno.ENOENT
        return st

    def unlink(self, path):
        try:
            gfile = authed_usr.file_list[path]
            fid = gfile['id']
            mime = gfile['mimeType']
        except:
            return FuseOSError(errno.EEXIST)
        if mime == 'application/vnd.google-apps.folder':
            raise FuseOSError(errno.EISDIR)
        else:
            authed_usr.client.files().delete(fileId=fid).execute()

    def open(self, path, flags):
        logger.debug("[open] (path = %s)" %path)

    def read(self, path, length, offset):
        """Read ```length`` bytes from ``path`` at ``offset``."""
        logger.debug("[read] (path=%s, length=%s, offset=%s)" % (path, length, offset))
        try:
            item = authed_usr.file_list[path]
        except:
            raise fuse.FuseError(errno.ENOENT)

        size = int(item['size'])

        if size <= offset:
            return b''

        if size < offset + length:
            length = size - offset

        return self.rp.get(path, offset, length, size)

    def readdir(self, path, offset):
        logger.debug("[readdir] (path = %s)" %path)
        try:
            logger.debug("try")
            dirents = ['.', '..']
            if path == "/":
                parent = "root"
            else:
                gfile = authed_usr.file_list[path]
                parent = gfile['id']

            items = authed_usr.get_children(parent)

            for item in items:
                if item['mimeType'] not in authed_usr.notvalid_mimetypes:
                    p = join(path, item['name'])
                    authed_usr.file_list[p] = item
                    dirents.append(item['name'])

            for directory in dirents:
                yield fuse.Direntry(directory)
        except:
            pass

    def rmdir(self, path):
        try:
            if path == "/":
                parent = "root"
            else:
                gfile = authed_usr.file_list[path]
                parent = gfile['id']
            logger.debug("[removedir] (path=%s)" % path)
            if authed_usr.file_list[path]['mimeType'] != 'application/vnd.google-apps.folder':
                logger.debug("this is not folder")
                raise fuse.FuseError(errno.ENOTDIR)
            elif len(authed_usr.get_children(parent)) != 0 :
                logger.debug("this is not empty")
                raise fuse.FuseError(errno.ENOTEMPTY)
            else:
                try:
                    authed_usr.client.files().delete(fileId=parent).execute()
                except:
                    logger.debug('An error occurred: while rmdir %s'%parent)
        except:
            pass

    def mkdir(self, path, mode):
        logger.debug("[mkdir] in path=%s %d" % (path, mode))
        if dirname(path) == "/":
            parent = "root"
        else:
            gfile = authed_usr.file_list[dirname(path)]
            parent = gfile['id']

        file_metadata = {
            'name': os.path.basename(path),
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent]
        }
        file = authed_usr.client.files().create(body=file_metadata,
                                            fields='id').execute()

    def rename(self, old, new):
        logger.debug("[rename] (old=%s, new=%s)" % (old,new))
        if old == new:
            return
        else:
            gfile = authed_usr.file_list[old]
            parent = gfile['id']
            logger.debug(parent)
        body = {
            'name':basename(new)
        }
        authed_usr.file_list['name'] = basename(new)
        authed_usr.client.files().update(fileId=parent,body=body).execute()

    def create(self, path, mode, fi=None):
        logger.debug("[create] (path={} and dirname = {})".format(path,dirname(path)))
        try:
            if dirname(path) == "/":
                fid = "root"
                mime = 'application/vnd.google-apps.folder'
            else:
                gfile = authed_usr.file_list[dirname(path)]
                fid = gfile['id']
                mime = gfile['mimeType']
            logger.debug("fileid = {}, mime={}".format(fid,mime))
        except:
            mime = ""
        if not mime == 'application/vnd.google-apps.folder':
            raise FuseOSError(errno.ENOTDIR)
        file_metadata = {
            "name": basename(path),
            "parents": [fid]
        }
        with NamedTemporaryFile() as tmp:
            logger.debug("create file")
            media = MediaFileUpload(tmp.name, resumable=True)
            logger.debug("create file 2")
            file = authed_usr.client.files().create(body=file_metadata, media_body=media, fields='id, name, size, mimeType').execute()
        authed_usr.file_list[path] = file
        logger.debug("File created in cloud")

    def write(self, path, buf, offset):
        logger.debug("[write] (path={}) ".format(path))
        if dirname(path) == "/":
            parent = "root"
        else:
            gfile = authed_usr.file_list[dirname(path)]
            parent = gfile['id']
        try:
            gfile = authed_usr.file_list[path]
            path_id = gfile['id']
        except:
            path_id = None
        logger.info("[file id received]")
        # Create/modify file, upload it with tmp name
        with NamedTemporaryFile() as tmp:
            logger.debug("[inside tmp write] pathid = {}".format(path_id))
            if path_id != None:
                request = authed_usr.client.files().get_media(fileId=path_id)
                fhh = io.BytesIO()
                downloader = MediaIoBaseDownload(fd=fhh, request=request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                fhh.seek(0)
                tmp.write(fhh.read())
                logger.debug("[write to tmp completed]")
            logger.debug('offset writing')
            if offset: tmp.seek(offset)
            tmp.write(buf)
            tmp.flush()
            logger.debug('tmp flush completed')
            file_metadata = {
                "name": basename(path)
            }
            media = MediaFileUpload(tmp.name, resumable=True)
            file = authed_usr.client.files().update(fileId=path_id, body=file_metadata, media_body=media, fields='id').execute()
            logger.debug('writing to cloud done')
        return len(buf)

    def truncate(self, path, size):
        logger.debug("[truckating]")
        #if path in self.created: return
        try:
            gfile = authed_usr.file_list[path]
            path_id = gfile['id']
        except:
            return

        with NamedTemporaryFile() as tmp:
            request = authed_usr.client.files().get_media(fileId=path_id)
            fhh = io.BytesIO()
            downloader = MediaIoBaseDownload(fd=fhh, request=request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
            fhh.seek(0)
            tmp.write(fhh.read())
            logger.debug("[write to tmp completed]")
            tmp.truncate(size)
            file_metadata = {
                "name": basename(path)
            }
            media = MediaFileUpload(tmp.name, resumable=True)
            file = authed_usr.client.files().update(fileId=path_id, body=file_metadata, media_body=media,
                                                    fields='id').execute()

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

    def utimens(self,path,times,*args):
        """Not implemented."""
        pass

    def release(self, path, fh):
        try:
            gfile = authed_usr.file_list[basename(path)]
            item = gfile['id']
        except:
            item = None
        if item:
            self.rp.release(path)
        else:
            raise fuse.FuseError(errno.ENOENT)

if __name__ == '__main__':
    print("in main file")
    authed_usr = GDrive()
    gdrivefs = GoogleDriveFS(version = '%prog ' + '0.0.1',
               usage = 'GoogleDrive Filesystem ' + fuse.Fuse.fusage,
               dash_s_do = 'setsingle')
    gdrivefs.parse(errex = 1)
    gdrivefs.flags = 0
    gdrivefs.main()
