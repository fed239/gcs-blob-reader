import io

from google.cloud import storage
from google.resumable_media.requests import ChunkedDownload
from google.resumable_media.requests import Download


class BlobReader(io.IOBase):
    def __init__(self, blob, start=0, end=None, client=None):
        self.blob = blob
        self.start = start
        self.end = end
        self.client = client
        self.download = None
        self.file_obj = None

    def _make_download(self):
        self.file_obj = io.BytesIO()
        download_url = self.blob._get_download_url()
        headers = storage.blob._get_encryption_headers(self.blob._encryption_key)
        headers['accept-encoding'] = 'gzip'
        if self.blob.chunk_size is None:
            self.download = Download(
                download_url, stream=self.file_obj, headers=headers,
                start=self.start, end=self.end)
        else:
            self.download = ChunkedDownload(
                download_url, self.blob.chunk_size, self.file_obj, headers=headers,
                start=self.start if self.start else 0, end=self.end)

    def read(self, size=-1):
        value = b''
        if self.file_obj.tell() < len(self.file_obj.getvalue()):
            value = self.file_obj.read(size)
        if len(value) < size or size < 0:
            self.start += self.file_obj.tell()
            self._make_download()
            transport = self.blob._get_transport(self.client)
            if self.blob.chunk_size is None:
                self.download.consume(transport)
            else:
                self.download.consume_next_chunk(transport)
            self.file_obj.seek(0)
            value += self.file_obj.read(size - len(value))
        return value

    def seekable(self):
        return True

    def seek(self, offset, whence=0):
        if whence == 0:
            self.start = offset or 0
            self._make_download()
            return self.start
        elif whence == 1:
            if self.file_obj is None:
                self.start += offset
                return self.start
            pos = self.file_obj.tell() + offset
            if pos < 0 or pos > len(self.file_obj.getvalue()):
                self.start += pos
                self._make_download()
                return self.start
            self.file_obj.seek(offset, 1)
            return self.start + self.file_obj.tell()
        else:
            assert False, "whence == 2 is not supported"
