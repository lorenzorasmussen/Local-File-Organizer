import os
import hashlib
from collections import defaultdict
from tqdm import tqdm

def find_duplicates(directory):
    """
    Finds duplicate files in a given directory based on file size and hash.
    """
    file_sizes = defaultdict(list)
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            path = os.path.join(dirpath, filename)
            if os.path.isfile(path):
                size = os.path.getsize(path)
                file_sizes[size].append(path)

    duplicates = []
    for size in tqdm(file_sizes, desc="Finding duplicates", unit=" group"):
        if len(file_sizes[size]) > 1:
            file_hashes = defaultdict(list)
            for path in file_sizes[size]:
                try:
                    with open(path, 'rb') as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()
                        file_hashes[file_hash].append(path)
                except (IOError, OSError):
                    continue

            for file_hash in file_hashes:
                if len(file_hashes[file_hash]) > 1:
                    duplicates.append(file_hashes[file_hash])

    return duplicates