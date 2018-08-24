# gcs-blob-reader
Python file-like reader wrapping google-cloud-storage library for easier access

## How to use

```
from google.cloud import storage
from gcs_blob_reader.reader import BlobReader

sc = storage.Client()
bucket = sc.get_bucket("bucket-name")
blob = bucket.blob("blob-name.bin", chunk_size=256 * 1024)
br = BlobReader(blob)
br.read(100)
br.seek(0)
```
