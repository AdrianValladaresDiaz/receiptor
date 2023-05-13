from multiprocessing import Value, Lock

"""Update (2019-01-23): a reader (Jeremy Cohn) points out that Value provides a way to store a lock on itself with the lock keyword argument, which could then be accessed with get_lock() method. This could simplify the code in this post a bit."""
class Counter(object):
    def __init__(self, initval=0):
        self.val = Value('i', initval)
        self.lock = Lock()

    def increment(self):
        with self.lock:
            self.val.value += 1

    def value(self):
        with self.lock:
            return self.val.value
        
    def decrement(self):
         with self.lock:
            self.val.value -= 1
