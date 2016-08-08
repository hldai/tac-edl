import gzip
from itertools import izip

from mention import Mention
from utils import doc_id_from_path


def __get_mids(edl_gold_file):
    mids = dict()
    f = open(edl_gold_file, 'r')
    for line in f:
        vals = line[:-1].split('\t')
        if vals[4].startswith('m.'):
            mids[vals[4][2:]] = vals[5]
    f.close()
    return mids


def __get_type_map():
    edl_gold_file = 'e:/el/LDC2015E75/data/tac_kbp_2015_tedl_training_gold_standard_entity_mentions.tab'
    mid_types_file = 'e:/el/res/freebase/mid-fb-type.txt'
    result_file = 'e:/el/res/freebase/dataset-mid-types.txt'

    mids = __get_mids(edl_gold_file)
    f = open(mid_types_file, 'rb')
    fout = open(result_file, 'wb')
    for i, line in enumerate(f):
        vals = line[:-1].split('\t')
        mtype = mids.get(vals[0], '')
        if mtype:
            fout.write('%s\t%s\t%s\n' % (vals[0], mtype, vals[1]))
            # break
        if (i + 1) % 1000000 == 0:
            print i + 1
    f.close()
    fout.close()


def __gold_mention_insight():
    edl_gold_file = 'e:/el/LDC2015E103/data/tac_kbp_2015_tedl_evaluation_gold_standard_entity_mentions.tab'
    mentions = Mention.load_edl_file(edl_gold_file)
    doc_mention_dict = dict()
    for m in mentions:
        if m.docid.startswith('ENG'):
            mlist = doc_mention_dict.get(m.docid, list())
            if not mlist:
                doc_mention_dict[m.docid] = mlist
            mlist.append(m)

    cnt, fncnt = 0, 0
    for docid, doc_mentions in doc_mention_dict.iteritems():
        print docid
        for m0 in doc_mentions:
            if m0.entity_type == 'PER' and ' ' in m0.name:
                fncnt += 1
            for m1 in doc_mentions:
                if m0 == m1:
                    continue
                if m0.beg_pos <= m1.beg_pos and m0.end_pos >= m1.end_pos and m0.entity_type == 'PER':
                    print '\t%s\t%d\t%d' % (m0.name, m0.beg_pos, m0.end_pos)
                    print '\t%s\t%d\t%d' % (m1.name, m1.beg_pos, m1.end_pos)
                    cnt += 1
                    # print m0.name, m0.beg_pos, m0.end_pos
                    # print m1.name, m1.beg_pos, m1.end_pos

    print cnt, fncnt


def __check_mention_fb_types():
    tac_edl_file = 'e:/el/LDC2015E75/data/tac_kbp_2015_tedl_training_gold_fixed.tab'
    fb_type_file = 'e:/el/res/freebase/mid-fb-type.gz'
    result_file = 'e:/el/LDC2015E75/data/mention-fb-types.txt'

    mentions = Mention.load_edl_file(tac_edl_file)
    mid_mentions = dict()
    for m in mentions:
        if m.mid.startswith('NIL'):
            continue
        mid_mentions[m.mid[2:]] = m

    f = gzip.open(fb_type_file, 'r')
    fout = open(result_file, 'wb')
    for i, line in enumerate(f):
        vals = line[:-1].split('\t')
        m = mid_mentions.get(vals[0], None)
        if m:
            # print '%s\t%s\t%s\t%s' % (m.name, vals[0], m.entity_type, vals[1])
            fout.write('%s\t%s\t%s\t%s\n' % (m.name.encode('utf-8'), vals[0], m.entity_type, vals[1]))

        if (i + 1) % 1000000 == 0:
            print i + 1
    f.close()
    fout.close()


def __type_eval():
    tac_edl_file = 'e:/el/LDC2015E75/data/tac_kbp_2015_tedl_training_gold_fixed.tab'
    mid_type_file = 'e:/el/res/freebase/mid-entity-type.txt'

    mid_type_dict = dict()
    f = open(mid_type_file, 'r')
    for line in f:
        vals = line[:-1].split('\t')
        mid_type_dict[vals[0]] = vals[1]
    f.close()

    hitcnt, cnt = 0, 0
    mentions = Mention.load_edl_file(tac_edl_file)
    for m in mentions:
        if not m.mid.startswith('m.'):
            continue
        # print m.mid
        cnt += 1
        sys_type = mid_type_dict.get(m.mid[2:], 'ORG')
        if sys_type == m.entity_type:
            hitcnt += 1
        else:
            print m.mid, m.entity_type, sys_type
    print hitcnt, cnt
    print float(hitcnt) / cnt


def __pseudo_link():
    dataset = 103
    if dataset == 75:
        gold_mention_file = 'e:/el/LDC2015E75/data/tac_kbp_2015_tedl_training_gold_fixed.tab'
        sys_mention_file = 'e:/el/LDC2015E75/data/all-mentions-tac.txt'
        dst_file = 'e:/el/LDC2015E75/data/all-mentions-tac-linked.txt'
    else:
        gold_mention_file = 'e:/el/LDC2015E103/data/tac_kbp_2015_tedl_' \
                            'evaluation_gold_standard_entity_mentions.tab'
        sys_mention_file = 'e:/el/LDC2015E103/data/all-mentions-tac.txt'
        dst_file = 'e:/el/LDC2015E103/data/all-mentions-tac-linked.txt'

    gold_mentions_docs = Mention.load_edl_file(gold_mention_file, arrange_by_docid=True)
    sys_mentions_docs = Mention.load_edl_file(sys_mention_file, arrange_by_docid=True)

    cnt = 0
    fout = open(dst_file, 'wb')
    for docid, sys_mentions in sys_mentions_docs.iteritems():
        gold_mentions = gold_mentions_docs.get(docid, list())
        for sm in sys_mentions:
            for gm in gold_mentions_docs:
                if gm.docid == sm.docid and gm.beg_pos == sm.beg_pos and gm.end_pos == sm.end_pos:
                    sm.mid = gm.mid
            fout.write('%s\t%s_%07d\t%s\t%s:%s-%s\t%s\t%s\t%s\n' % (
                'ZJU', 'EDL15', cnt + 1, sm.name.encode('utf-8'),
                sm.docid, sm.beg_pos, sm.end_pos, sm.mid,
                sm.entity_type, sm.mention_type))
            cnt += 1
    fout.close()


def __get_mid_name():
    fb_name_file = '/media/dhl/Data/data/el/tmpres/freebase/full_freebase_name_en.txt'
    fb_name_file = 'e:/data/edl/tmpres/freebase/full_freebase_name_en.txt'
    fb_name_file = 'e:/data/edl/tmpres/full_freebase_name_alias_merged_en_lc_ord_mid_name.txt'
    dst_id = '02189'

    dst_beg = dst_id + '\t'
    fin = open(fb_name_file)
    for i, line in enumerate(fin):
        if line.startswith(dst_beg):
            print line
            # print 'end'
            # break

        if (i + 1) % 10000000 == 0:
            print i + 1

    fin.close()


def __missing_docs_in_edl_file():
    datadir = 'e:/data/edl'
    edl_file = '%s/LDC2016E63/output/all-mentions.tab' % datadir
    doc_list_file = '%s/LDC2016E63/data/eng-docs-list-win.txt' % datadir

    mentions = Mention.load_edl_file(edl_file)
    docids = set()
    for m in mentions:
        docids.add(m.docid)

    f = open(doc_list_file, 'r')
    for line in f:
        doc_path = line.rstrip()
        docid = doc_id_from_path(doc_path)
        if docid not in docids:
            print docid
    f.close()


def main():
    # __get_type_map()
    # __gold_mention_insight()
    # __check_mention_fb_types()
    # __type_eval()
    # __pseudo_link()
    __get_mid_name()
    # __missing_docs_in_edl_file()
    pass

if __name__ == '__main__':
    main()
