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


def __gen_fb_en_alias_file():
    datadir = 'e:/data/edl'
    all_alias_file = '%s/tmpres/freebase/freebase-alias-full.txt' % datadir
    dst_file = '%s/tmpres/freebase/fb-en-alias.txt' % datadir

    mid_head = '<http://rdf.freebase.com/ns/m.'
    mid_head_len = len(mid_head)

    fin = open(all_alias_file, 'rb')
    fout = open(dst_file, 'wb')
    for line in fin:
        assert line.startswith(mid_head)
        line = line.rstrip()
        if not line.endswith('@en\t.'):
            continue
        vals = line.split('\t')
        fout.write('%s\t%s\n' % (vals[0][mid_head_len:-1], vals[2][1:-4].lower()))
        # break
    fin.close()
    fout.close()


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
    return f.read(num_bytes)


def __candidates_dict():
    candidates_dict_file = 'e:/data/edl/res/prog-gen/candidates-dict.bin'
    # candidates_dict_file = '/home/dhl/data/EDL/tmpres/candidates-dict.bin'

    f = open(candidates_dict_file, 'rb')
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

        if name == 'ccp':
            for x in cur_candidates:
                print x[0], x[1]
            break

        if (i + 1) % 1000000 == 0:
            print i + 1
    f.close()


def __load_title_to_wid(wid_title_file):
    title_wid_dict = dict()
    fin = open(wid_title_file, 'r')
    for line in fin:
        vals = line.rstrip().split('\t')
        title_wid_dict[vals[1]] = int(vals[0])
    fin.close()
    return title_wid_dict


def __gen_wid_redirect_file():
    datadir = 'e:/data/edl'
    wid_title_file = '%s/tmpres/wiki/enwiki-20150403-wid-title-list.txt' % datadir
    redirect_title_file = '%s/tmpres/wiki/redirect_alias_list_cleaned_srt_alias.txt' % datadir
    dst_file = '%s/tmpres/wiki/wid-redirect.txt' % datadir

    print 'Loading %s ...' % wid_title_file
    title_wid_dict = __load_title_to_wid(wid_title_file)
    print 'Done'

    waiting_list = list()
    fin = open(redirect_title_file, 'r')
    fout = open(dst_file, 'wb')
    for line in fin:
        vals = line.rstrip().split('\t')
        wid = title_wid_dict.get(vals[1], -1)
        if wid < 0:
            waiting_list.append((vals[0], vals[1]))
        else:
            fout.write('%d\t%s\n' % (wid, vals[0]))
            title_wid_dict[vals[0]] = wid
    fin.close()

    print len(waiting_list)
    cnt = 0
    while waiting_list:
        af, at = waiting_list.pop(0)
        wid = title_wid_dict.get(at, -1)
        if wid > 0:
            cnt += 1
            fout.write('%s\t%s\n' % (wid, af))
            title_wid_dict[af] = wid
        else:
            print af, at
    print cnt

    fout.close()


def __load_wid_name_files(wid_name_files):
    wid_name_dict = dict()
    for wid_name_file in wid_name_files:
        print 'loading %s ...' % wid_name_file
        f = open(wid_name_file, 'r')
        for line in f:
            vals = line.rstrip().split('\t')
            wid = int(vals[0])
            cur_name = vals[1].lower()
            names = wid_name_dict.get(wid, list())
            if not names:
                wid_name_dict[wid] = names
            if cur_name not in names:
                names.append(cur_name)
        f.close()
    return wid_name_dict


def __gen_wid_alias_cnt_file():
    datadir = 'e:/data/edl'
    anchor_cnts_file = '%s/tmpres/wiki/anchor_cnts.txt' % datadir
    wid_disamb_alias_file = '%s/tmpres/wiki/wid-disamb-alias.txt' % datadir
    wid_title_file = '%s/tmpres/wiki/enwiki-20150403-wid-title-list.txt' % datadir
    wid_redirect_file = '%s/tmpres/wiki/wid-redirect.txt' % datadir
    dst_file = '%s/tmpres/wiki/wid-alias-cnts.txt' % datadir

    wid_name_files = [wid_title_file, wid_disamb_alias_file, wid_redirect_file]
    wid_names_dict = __load_wid_name_files(wid_name_files)
    fin = open(anchor_cnts_file, 'r')
    fout = open(dst_file, 'wb')
    for i, line in enumerate(fin):
        vals = line.rstrip().split('\t')
        wid = int(vals[0])
        cnt = int(vals[2])
        names = wid_names_dict.get(wid, None)
        if names and vals[1] in names:
            cnt += 5
        fout.write('%d\t%s\t%d\n' % (wid, vals[1], cnt))

        if (i + 1) % 1000000 == 0:
            print i + 1
        # if i == 10:
        #     break
    fin.close()
    fout.close()


def main():
    # __gen_wid_redirect_file()
    # __gen_fb_en_alias_file()
    # __filter_mid_alias_cnt_file()
    __gen_wid_alias_cnt_file()
    # __candidates_dict()
    pass

if __name__ == '__main__':
    main()
