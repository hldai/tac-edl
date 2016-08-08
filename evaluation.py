import os
from itertools import izip

from mention import Mention


def __write_link_errors(link_errors, dst_file):
    fout = open(dst_file, 'wb')
    for gm, sm in link_errors:
        fout.write('%s\t%s\t%s\t%s\n' % (gm.docid, gm.name.encode('utf-8'), gm.kbid, sm.kbid))
    fout.close()


def __write_type_errors(type_errors, dst_file):
    fout = open(dst_file, 'wb')
    for gm, sm in type_errors:
        fout.write('%s\t%s\t%s\t%s\t%s\t%s\n' % (gm.docid, gm.name, gm.kbid, sm.kbid, gm.entity_type,
                                                 sm.entity_type))
    fout.close()


def __evaluate_edl(gold_edl_file, sys_edl_file, require_type_match, link_error_file,
                   type_error_file):
    gold_mentions = Mention.load_edl_file(gold_edl_file, arrange_by_docid=True)
    sys_mentions = Mention.load_edl_file(sys_edl_file, arrange_by_docid=True)

    link_errors = list()
    type_errors = list()
    sys_cnt, gold_cnt, hit_cnt = 0, 0, 0
    for docid, sys_mentions_doc in sys_mentions.iteritems():
        gold_mentions_doc = gold_mentions.get(docid, list())
        for gm in gold_mentions_doc:
            if not gm.kbid.startswith('NIL'):
                gold_cnt += 1

        hit_list = [False for _ in xrange(len(gold_mentions_doc))]
        for sm in sys_mentions_doc:
            for i, gm in enumerate(gold_mentions_doc):
                if sm.beg_pos == gm.beg_pos and sm.end_pos == gm.end_pos:
                    hit_list[i] = True
                    break

            if sm.kbid.startswith('NIL'):
                continue
            sys_cnt += 1
            for i, gm in enumerate(gold_mentions_doc):
                if sm.beg_pos != gm.beg_pos or sm.end_pos != gm.end_pos:
                    continue

                if gm.mention_type == 'NOM':
                    sys_cnt -= 1
                    break

                if sm.entity_type != gm.entity_type:
                    type_errors.append((gm, sm))

                if sm.kbid == gm.kbid and ((not require_type_match) or sm.entity_type == gm.entity_type):
                    hit_cnt += 1

                if sm.kbid != gm.kbid:
                    link_errors.append((gm, sm))
                    # print '%s\t%s\t%s\t%s' % (docid, sm.mid, gm.mid, gm.name)
                    # print sm.mid, gm.mid, gm.name, docid

    link_errors.sort(key=lambda x: x[0].name)
    __write_link_errors(link_errors, link_error_file)
    type_errors.sort(key=lambda x: x[0].name)
    __write_type_errors(type_errors, type_error_file)
    # for v in errors:
    #     print '%s\t%s\t%s\t%s' % (v[0], v[1], v[2], v[3])

    print '#hit: %d, #sys: %d, #gold: %d' % (hit_cnt, sys_cnt, gold_cnt)
    hit_cnt = float(hit_cnt)
    prec = hit_cnt / sys_cnt
    recall = hit_cnt / gold_cnt
    f1 = 2 * prec * recall / (prec + recall)
    print 'prec: %f, recall: %f, f1: %f' % (prec, recall, f1)


def __evaluate_ed(gold_edl_file, sys_edl_file, fn_file, fp_file, require_type_match=True):
    gold_mentions = Mention.load_edl_file(gold_edl_file, arrange_by_docid=True)
    sys_mentions = Mention.load_edl_file(sys_edl_file, arrange_by_docid=True)

    fout_fp = open(fp_file, 'wb')
    sys_cnt, gold_cnt, hit_cnt = 0, 0, 0
    fn_mentions = list()
    for docid, sys_mentions_doc in sys_mentions.iteritems():
        sys_cnt += len(sys_mentions_doc)

        all_gold_mentions_in_doc = gold_mentions.get(docid, list())
        # nam_gold_mentions = [m for m in all_gold_mentions_in_doc if m.mention_type == 'NAM']
        nam_gold_mentions = all_gold_mentions_in_doc
        gold_hit_tags = [False] * len(nam_gold_mentions)
        gold_cnt += len(nam_gold_mentions)

        for sm in sys_mentions_doc:
            hit = False
            for i, gm in enumerate(nam_gold_mentions):
                type_hit = (sm.entity_type.startswith(gm.entity_type)) if require_type_match else True
                if sm.beg_pos == gm.beg_pos and sm.end_pos == gm.end_pos and type_hit:
                    hit = True
                    hit_cnt += 1
                    gold_hit_tags[i] = True
                    break

            if not hit:
                fout_fp.write('%s\t%s\t%d\t%d\n' % (sm.name.encode('utf-8'), docid, sm.beg_pos, sm.end_pos))
        # break

        for gm, hit in izip(nam_gold_mentions, gold_hit_tags):
            if not hit:
                fn_mentions.append(gm)
                # fout_fn.write('%s\t%s\t%d\t%d\n' % (gm.name.encode('utf-8'), docid, gm.beg_pos, gm.end_pos))

    fout_fp.close()

    fn_mentions.sort(key=lambda x: x.name)
    Mention.write_mentions(fn_mentions, fn_file)

    print '#hit: %d, #sys: %d, #gold: %d' % (hit_cnt, sys_cnt, gold_cnt)
    hit_cnt = float(hit_cnt)
    prec = hit_cnt / sys_cnt
    recall = hit_cnt / gold_cnt
    f1 = 2 * prec * recall / (prec + recall)
    print 'prec: %f, recall: %f, f1: %f' % (prec, recall, f1)


def __find_type_errors_of_docs(docid, gold_mentions, sys_mentions):
    error_list = list()
    for sm in sys_mentions:
        for gm in gold_mentions:
            if sm.beg_pos == gm.beg_pos and sm.end_pos == gm.end_pos and sm.entity_type != gm.entity_type:
                error_list.append((sm, gm))
    return error_list


def __find_type_errors(gold_edl_file, sys_edl_file):
    gold_mentions_docs = Mention.load_edl_file(gold_edl_file, arrange_by_docid=True)
    sys_mentions_docs = Mention.load_edl_file(sys_edl_file, arrange_by_docid=True)

    all_errors = list()
    for docid, sys_mentions in sys_mentions_docs.iteritems():
        gold_mentions = gold_mentions_docs[docid]
        all_errors += __find_type_errors_of_docs(docid, gold_mentions, sys_mentions)
    all_errors.sort(key=lambda x: x[0].name.lower())
    for v in all_errors:
        print '%s\t%s\t%s\t%s' % (v[0].name, v[0].entity_type, v[1].entity_type, v[0].docid)


def main():
    dataset = 'LDC2015E75'
    # dataset = 'LDC2015E103'
    # dataset = 'LDC2016E63'
    require_type_match = True
    require_kbid_match = True

    # data_dir = '/home/dhl/data/EDL/'
    data_dir = 'e:/data/edl'

    gold_edl_file = os.path.join(data_dir, dataset, 'data/gold-eng-mentions.tab')
    # gold_edl_file = os.path.join(data_dir, dataset, 'data/gold-eng-nom-mentions.tab')
    # sys_ed_file = os.path.join(data_dir, dataset, 'output/post-authors.tab')
    # sys_ed_file = os.path.join(data_dir, dataset, 'output/ner-mentions.tab')
    sys_ed_file = os.path.join(data_dir, dataset, 'output/all-mentions.tab')
    sys_edl_file = os.path.join(data_dir, dataset, 'output/sys-link-sm-pp-ft.tab')
    false_pos_file = os.path.join(data_dir, dataset, 'error/fp.txt')
    false_neg_file = os.path.join(data_dir, dataset, 'error/fn.txt')
    link_error_file = os.path.join(data_dir, dataset, 'error/link-error.txt')
    type_error_file = os.path.join(data_dir, dataset, 'error/type-error.txt')

    # __evaluate_ed(gold_edl_file, sys_ed_file, false_neg_file, false_pos_file, require_type_match)
    __evaluate_edl(gold_edl_file, sys_edl_file, require_type_match, link_error_file, type_error_file)
    # __find_type_errors(gold_edl_file, sys_edl_file)


if __name__ == '__main__':
    main()
