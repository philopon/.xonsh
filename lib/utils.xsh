import os
import warnings

def add_PATH(*paths):
    for path in reversed(paths):
        path = os.path.expanduser(path)
        if os.path.isdir(path):
            $PATH.add(path, front=True)
        else:
            warnings.warn(f"{path} is not fould. skip adding to PATH")
