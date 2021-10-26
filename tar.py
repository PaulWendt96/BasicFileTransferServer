import tarfile
import os
from io import BytesIO

def get_tar_bytes(path):
    '''

    '''
    if not os.path.exists(path):
        raise FileNotFoundError
    file_obj = BytesIO()
    with tarfile.TarFile(mode = 'w', fileobj=file_obj) as tar:
        tar.add(path, arcname=os.path.basename(path))

    file_obj.seek(0)
    tar_bytes = file_obj.read()
    return tar_bytes


def extract_dir(tar_bytes, path):
    '''

    '''
    tar_object = BytesIO(tar_bytes)
    tar = tarfile.open(fileobj=tar_object)
    tar.extractall(path=path)
