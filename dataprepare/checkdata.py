import gzip
import os
from mention import Mention
from processfb import FbToTacTypeMap


def __get_mid_types_in_dataset():
    datadir = 'e:/data/edl'
    edl_file = os.path.join(datadir, 'LDC2015E75/data/gold-eng-mentions.tab')
    mid_types_file = os.path.join(datadir, 'res/freebase/mid-fb-type.gz')
    dst_file = os.path.join(datadir, 'LDC2015E75/output/fb-types.txt')

    mentions = Mention.load_edl_file(edl_file)
    for m in mentions:
        if m.kbid.startswith('m.'):
            m.kbid = m.kbid[2:]
    kbid_mentions = Mention.group_mentions_by_kbid(mentions)

    f = gzip.open(mid_types_file, 'r')
    fout = open(dst_file, 'wb')
    hit = False
    prev_kbid = ''
    for i, line in enumerate(f):
        tab_pos = line.find('\t')
        kbid = line[:tab_pos]

        if hit and prev_kbid == kbid:
            fout.write('\t%s' % line)
        elif prev_kbid != kbid:
            if kbid in kbid_mentions:
                cur_mentions = kbid_mentions[kbid]
                for m in cur_mentions:
                    fout.write('%s\t' % m.name.encode('utf-8'))
                fout.write('\n')
                for m in cur_mentions:
                    fout.write('%s\t' % m.entity_type)
                fout.write('\n\t%s' % line)
                hit = True
            else:
                hit = False

        prev_kbid = kbid

        if (i + 1) % 10000000 == 0:
            print i + 1
    f.close()
    fout.close()


def __count_hit(true_types, sys_type):
    hit_cnt = 0
    for tt in true_types:
        if tt == sys_type:
            hit_cnt += 1
    return hit_cnt


def __try_fb_type_to_tac_type_map():
    datadir = 'e:/data/edl'
    fb_types_file = os.path.join(datadir, 'LDC2015E75/output/fb-types.txt')
    fb_to_tac_type_file = os.path.join(datadir, 'res/fb-types-to-tac-types.txt')

    type_map = FbToTacTypeMap(fb_to_tac_type_file)

    names_line = ''
    tac_types = list()
    fb_types = list()
    hit_cnt = 0
    cnt = 0
    fin = open(fb_types_file, 'r')
    while True:
        try:
            line = fin.next()
        except StopIteration:
            break

        if not line.startswith('\t'):
            if names_line:
                mtype = type_map.get_tac_type(fb_types)
                hc = __count_hit(tac_types, mtype)
                if hc <= len(tac_types) / 2:
                    print names_line,
                    print tac_types, mtype
                    print fb_types
                    print
                hit_cnt += hc

            names_line = line
            types_line = fin.next()
            tac_types = types_line.rstrip().split('\t')
            cnt += len(tac_types)
            fb_types = list()
        else:
            vals = line.strip().split('\t')
            fb_types.append(vals[1])
    fin.close()

    mtype = type_map.get_tac_type(fb_types)
    hc = __count_hit(tac_types, mtype)
    hit_cnt += hc

    print hit_cnt, cnt, float(hit_cnt) / cnt


def main():
    __try_fb_type_to_tac_type_map()
    # __get_mid_types_in_dataset()
    pass

if __name__ == '__main__':
    main()
