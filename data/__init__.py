import os
import numpy as np
# import cPickle

_this_dir = os.path.dirname(os.path.realpath(__file__))
_patent_subset = '/'.join([_this_dir, 'adj.p'])

def get_patent_adj():
    return np.load(_patent_subset, mmap_mode='r')

# def pickle_save(filename, obj):
#     with open(filename, 'wb') as outfile:
#         cPickle.dump(obj, outfile)
