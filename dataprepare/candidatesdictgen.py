# -*- coding: utf-8 -*-

import numpy as np


def __name_legal(name):
    if len(name) > 100:
        return False

    has_alpha = False
    for ch in name:
        if ch == '<' or ch == '>':
            return False
        if ch.isalpha():
            has_alpha = True
    if not has_alpha:
        return False

    words = name.split(' ')
    for word in words:
        if len(word) > 20:
            return False
    return True


def __load_mids_file(mids_file):
    print 'Loading %s ...' % mids_file
    mids = set()
    f = open(mids_file, 'r')
    for line in f:
        mids.add(line.rstrip())
    f.close()
    print 'Done'
    return mids


def __filter_mid_alias_cnt_file():
    filter_mids_file = '/home/dhl/data/EDL/tmpres/filter-mids.txt'
    mid_alias_cnt_file = '/home/dhl/data/EDL/tmpres/mid-alias-cnt-ord-mid.txt'
    dst_file = '/home/dhl/data/EDL/tmpres/mid-alias-cnt-ord-mid-filtered.txt'

    filter_mids = __load_mids_file(filter_mids_file)

    fin = open(mid_alias_cnt_file, 'r')
    fout = open(dst_file, 'wb')
    prev_mid = ''
    prev_filtered = False
    for i, line in enumerate(fin):
        vals = line.rstrip().split('\t')

        if vals[0] == prev_mid:
            if not prev_filtered:
                fout.write(line)
        else:
            if vals[0] in filter_mids:
                prev_filtered = True
            else:
                prev_filtered = False
                fout.write(line)
            prev_mid = vals[0]

        # if i == 1000:
        #     break

        if (i + 1) % 1000000 == 0:
            print i + 1
    fin.close()
    fout.close()


def __read_str_with_byte_len(f):
    num_bytes = np.fromfile(f, '>i1', 1)[0]
    # print num_bytes
    return f.read(num_bytes)


def __candidates_dict():
    candidates_dict_file = '/home/dhl/data/EDL/tmpres/candidates-dict.bin'

    f = open(candidates_dict_file, 'r')
    num_names = np.fromfile(f, '>i4', 1)[0]
    total_num_candidates = np.fromfile(f, '>i4', 1)[0]
    print num_names, total_num_candidates
    for i in xrange(num_names):
        name = __read_str_with_byte_len(f)

        cur_candidates = list()

        num_candidates = np.fromfile(f, '>i2', 1)[0]
        for _ in xrange(num_candidates):
            mid = __read_str_with_byte_len(f)
            cmns = np.fromfile(f, '>f4', 1)[0]
            cur_candidates.append((mid, cmns))

        if name == 'clinton':
            for x in cur_candidates:
                print x[0], x[1]
            break
    f.close()


def main():
    # __filter_mid_alias_cnt_file()
    __candidates_dict()

if __name__ == '__main__':
    main()
