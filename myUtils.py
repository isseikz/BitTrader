import os


def CSVListIn(dir_path):
    files = [path for path in sorted(os.listdir(dir_path)) if path.endswith('.csv')]
    return files
