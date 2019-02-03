import io
import urllib2
import zipfile

def load_remote_file_in_memory(url):
  inmem_file = io.BytesIO()
  remote_file = urllib2.urlopen(url)
  inmem_file.write(remote_file.read())
  inmem_file.seek(0)
  return inmem_file

def open_from_zipped_url(zip_url, filename):
  inmem_zipfile = load_remote_file_in_memory(zip_url)
  with zipfile.ZipFile(inmem_zipfile) as zip_archive:
    archived_file = io.BytesIO()
    with zip_archive.open(filename) as file_unzipped:
      archived_file.write(file_unzipped.read())
      archived_file.seek(0)
      return archived_file

