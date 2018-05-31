import linecache
import numpy as np


class DocIterator:
    def __init__(self, path_doc, max_len=100):
        self.path_doc = path_doc
        with open(path_doc, 'r') as fin:
            self.total_line = sum([1 for _ in fin])
        self.max_len = max_len

    def __len__(self):
        return self.total_line

    def __getitem__(self, line_indices):
        if isinstance(line_indices, slice):
            line_indices = range(line_indices.start, line_indices.stop)
        data = []
        for idx in line_indices:
            line = linecache.getline(self.path_doc, idx + 1)
            if not line:
                continue
            line = line.rstrip('\r\n').split(' ')
            if len(line) > self.max_len:
                keep_indices = np.sort(np.random.choice(range(len(line)), self.max_len, replace=False))
                line = [line[idx] for idx in keep_indices]
            data += [line]
        return data
