def add_PATH(*paths):
    for path in reversed(paths):
        $PATH.add(path, front=True)