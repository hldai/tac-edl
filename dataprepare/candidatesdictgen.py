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


def __gen_candidates_dict():
    mid_alias_cnt_file = '/home/dhl/data/EDL/tmpres/mid-alias-cnt-ord-alias-filtered.txt'
    dst_file = '/home/dhl/data/EDL/tmpres/mid-alias-cnt-ord-alias-compact.txt'

    fin = open(mid_alias_cnt_file, 'r')
    fout = open(dst_file, 'wb')
    prev_name = ''
    for i, line in enumerate(fin):
        vals = line.rstrip().split('\t')
        cur_name = vals[1]
        if __name_legal(cur_name):
            fout.write(line)

        prev_name = vals[1]
        # if i == 100000:
        #     break
        if (i + 1) % 1000000 == 0:
            print i + 1
    fin.close()
    fout.close()


def main():
    # __filter_mid_alias_cnt_file()
    __gen_candidates_dict()

if __name__ == '__main__':
    main()
