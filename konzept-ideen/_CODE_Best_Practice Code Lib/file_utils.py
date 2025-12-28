import os
def list_files(path):
    return [os.path.join(path,f) for f in os.listdir(path) if not f.startswith('.')]
