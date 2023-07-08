from os import listdir
from os.path import isfile, join, splitext
from multiprocessing import Queue

allowed_extensions = [".jpg"]


def gather_files(path: str) -> Queue:
    files = [f for f in listdir(path) if isfile(join(path, f))]
    images = [f for f in files if splitext(f)[1] in allowed_extensions]

    imgQueue = Queue()
    [imgQueue.put(join(path, f)) for f in images]

    return imgQueue
