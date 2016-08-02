from mention import Mention
from itertools import izip


def __evaluate_edl(gold_edl_file, sys_edl_file):
    gold_mentions = Mention.load_edl_file(gold_edl_file, arrange_by_docid=True)
    sys_mentions = Mention.load_edl_file(sys_edl_file, arrange_by_docid=True)

    errors = list()
    sys_cnt, gold_cnt, hit_cnt = 0, 0, 0
    for docid, sys_mentions_doc in sys_mentions.iteritems():
        gold_mentions_doc = gold_mentions.get(docid, list())
        for gm in gold_mentions_doc:
            if not gm.mid.startswith('NIL'):
                gold_cnt += 1

        for sm in sys_mentions_doc:
            if sm.mid.startswith('NIL'):
                continue
            sys_cnt += 1
            for gm in gold_mentions_doc:
                if sm.beg_pos != gm.beg_pos or sm.end_pos != gm.end_pos:
                    continue
                if gm.mention_type == 'NOM':
                    sys_cnt -= 1
                    break

                if sm.entity_type != gm.entity_type:
                    print '%s\t%s\t%s\t%s' % (docid, gm.name, gm.entity_type, sm.entity_type)

                if sm.mid == gm.mid:
                    hit_cnt += 1
                elif not gm.mid.startswith('NIL'):
                    errors.append((docid, sm.mid, gm.mid, gm.name))
                    # print '%s\t%s\t%s\t%s' % (docid, sm.mid, gm.mid, gm.name)
                    # print sm.mid, gm.mid, gm.name, docid

    errors.sort(key=lambda x: x[3])
    # for v in errors:
    #     print '%s\t%s\t%s\t%s' % (v[0], v[1], v[2], v[3])

    print '#hit: %d, #sys: %d, #gold: %d' % (hit_cnt, sys_cnt, gold_cnt)
    hit_cnt = float(hit_cnt)
    prec = hit_cnt / sys_cnt
    recall = hit_cnt / gold_cnt
    f1 = 2 * prec * recall / (prec + recall)
    print 'prec: %f, recall: %f, f1: %f' % (prec, recall, f1)


def evaluate(gold_edl_file, sys_edl_file, fn_file, fp_file, require_type_match=True):
    gold_mentions = Mention.load_edl_file(gold_edl_file, arrange_by_docid=True)
    sys_mentions = Mention.load_edl_file(sys_edl_file, arrange_by_docid=True)

    fout_fn = open(fn_file, 'wb')
    fout_fp = open(fp_file, 'wb')
    sys_cnt, gold_cnt, hit_cnt = 0, 0, 0
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
                type_hit = (sm.entity_type == gm.entity_type) if require_type_match else True
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
                fout_fn.write('%s\t%s\t%d\t%d\n' % (gm.name.encode('utf-8'), docid, gm.beg_pos, gm.end_pos))

    fout_fn.close()
    fout_fp.close()

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
        print '%s\t%s\t%s' % (v[0].name, v[0].entity_type, v[1].entity_type)


def main():
    # dataset = 75
    dataset = 103
    require_type_match = True
    require_kbid_match = True

    data_dir = '/home/dhl/data/EDL/'

    if dataset == 75:
        gold_edl_file = data_dir + 'LDC2015E75/data/tac_kbp_2015_tedl_training_gold_fixed.tab'
        # gold_edl_file = data_dir + 'LDC2015E75/data/gold-eng-mentions.tab'
        sys_edl_file = data_dir + 'LDC2015E75/data/all-mentions-tac.txt'
        sys_edl_file = data_dir + 'LDC2015E75/output/sys-link-gm-new.tab'
        false_pos_file = data_dir + 'LDC2015E75/output/fp.txt'
        false_neg_file = data_dir + 'LDC2015E75/output/fn.txt'
    else:
        # gold_edl_file = data_dir + 'LDC2015E103/data/tac_kbp_2015_tedl_evaluation_gold_standard_entity_mentions.tab'
        gold_edl_file = data_dir + 'LDC2015E103/data/gold-eng-mentions.tab'
        # sys_edl_file = 'e:/el/LDC2015E103/data/ner-result.txt'
        # sys_edl_file = data_dir + 'LDC2015E103/output/all-mentions-tac.txt'
        sys_edl_file = data_dir + 'LDC2015E103/output/sys-link-sm-nl.tab'
        false_pos_file = data_dir + 'LDC2015E103/output/fp.txt'
        false_neg_file = data_dir + 'LDC2015E103/output/fn.txt'

    # evaluate(gold_edl_file, sys_edl_file, false_neg_file, false_pos_file, require_type_match)
    __evaluate_edl(gold_edl_file, sys_edl_file)
    # __find_type_errors(gold_edl_file, sys_edl_file)


if __name__ == '__main__':
    main()
