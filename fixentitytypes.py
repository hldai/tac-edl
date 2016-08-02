from mention import Mention


def __fix_entity_types_by_mid():
    dataset = 103
    mid_type_file = '/media/dhl/Data/data/el/res/freebase/mid-entity-type.txt'
    if dataset == 75:
        tac_edl_file = 'e:/el/LDC2015E75/data/all-mentions-tac-linked.txt'
        dst_file = 'e:/el/LDC2015E75/data/all-mentions-tac-linked-type.txt'
    else:
        tac_edl_file = '/home/dhl/data/EDL/LDC2015E103/output/sys-link-sm-nl.tab'
        dst_file = '/home/dhl/data/EDL/LDC2015E103/output/sys-link-sm-nl-ft.tab'

    mid_type_dict = dict()
    f = open(mid_type_file, 'r')
    for line in f:
        vals = line[:-1].split('\t')
        mid_type_dict[vals[0]] = vals[1]
    f.close()

    # hitcnt, cnt = 0, 0
    cnt = 0
    mentions = Mention.load_edl_file(tac_edl_file)
    fout = open(dst_file, 'wb')
    for m in mentions:
        if m.mid.startswith('m.'):
            sys_type = mid_type_dict.get(m.mid[2:], '')
            if sys_type:
                m.entity_type = sys_type
        # print m.mid
        fout.write('%s\t%s_%07d\t%s\t%s:%d-%d\t%s\t%s\t%s\t1.0\n' % (
            'ZJU', 'EDL15', cnt, m.name.encode('utf-8'),
            m.docid, m.beg_pos, m.end_pos, m.mid,
            m.entity_type, m.mention_type))
        cnt += 1
    fout.close()


def main():
    __fix_entity_types_by_mid()

if __name__ == '__main__':
    main()
