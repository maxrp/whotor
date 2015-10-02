#!/usr/bin/python3

import fdb
import sys

from glob import glob
from os import path
from ctypes.util import find_library
from stem.descriptor.reader import DescriptorReader

DESCRIPTORS = path.abspath('./collector.torproject.org')
DESCRIPTOR_NAME = 'server-descriptors-%Y-%m.tar.xz'


def findlib(name):
    libname = find_library(name)
    # if the lib exists, get the path (only supports linux)
    if libname:
        libpath = path.join('/usr/lib', libname)
        lib64path = path.join('/usr/lib64', libname)
        if path.exists(lib64path):
            return lib64path
        elif path.exists(libpath):
            return libpath
        else:
            return False
    else:
        return False


def fdbembedded_connect(dsn, charset):
    fbembed_path = findlib('fbembed')
    if not fbembed_path:
        print("You must have the fbembed shared object to run this script.")
        sys.exit(255)
    else:
        return fdb.connect(dsn=dsn,
                           charset=charset,
                           fb_library_name=fbembed_path)


def main():
    if len(sys.argv) > 1:
        # do we want a subgroup, i.e. "server-descriptors-2015*"
        desc_pattern = path.join(DESCRIPTORS, sys.argv[1])
    else:
        # otherwise assume we want everything in the descriptors cache
        desc_pattern = path.join(DESCRIPTORS, '*')

    descriptors = list(map(lambda x: path.join(DESCRIPTORS, x),
                           glob(desc_pattern)))
    print(descriptors)

    # connect to the db
    con = fdbembedded_connect('./tor-exits.fdb', 'UTF8')
    cur = con.cursor()
    insert_exit = cur.prep("insert into exits (observed,ip) values (?,?);")
    with DescriptorReader(descriptors) as reader:
        for desc in reader:
            # extract the date part from the archive name, add day value
            date = "{}-01".format(path.basename(desc.get_path())[19:26])
            cur.execute(insert_exit, (date, desc.address))
        con.commit()


if __name__ == '__main__':
    main()
