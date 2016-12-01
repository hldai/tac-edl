import os
import re
from mention import Mention

doc_head = '<?xml version="1.0" encoding="utf-8"?>\n'

xml_mention_pattern_str = '<query id=\"(.*?)\">\s*<name>(.*?)</name>\s*<docid>(.*?)</docid>\s*</query>'


def __read_text_file(filename):
    f = open(filename, 'r')
    text = f.read()
    f.close()
    return text


def prev_mentions_format_to_new(tab_file, xml_file, output_file):
    xml_text = __read_text_file(xml_file)
    miter = re.finditer(xml_mention_pattern_str, xml_text)
    mentions_dict = dict()
    beg_pos_dict = dict()
    for m in miter:
        cur_doc_id = m.group(3)
        mention = Mention(name=m.group(2), docid=cur_doc_id, mention_id=m.group(1))
        doc_beg = beg_pos_dict.get(cur_doc_id, 0)  # TODO
        mention.beg_pos = doc_beg
        mention.end_pos = doc_beg + len(mention.name.encode('utf-8')) - 1
        beg_pos_dict[cur_doc_id] = mention.end_pos + 1
        mentions_dict[mention.mention_id] = mention

    f = open(tab_file, 'r')
    for line in f:
        vals = line.strip().split('\t')
        if len(vals) < 3:
            continue
        m = mentions_dict.get(vals[0], None)
        if m:
            m.kbid = vals[1]
            m.entity_type = vals[2]
    f.close()

    Mention.save_as_edl_file(mentions_dict.values(), output_file)


def load_nom_mentions(edl_gold_file):
    nom_list = list()
    f = open(edl_gold_file, 'r')
    for line in f:
        vals = line[:-1].split('\t')
        if vals[6] == 'NOM':
            nom_list.append(vals[2])
    f.close()
    return nom_list


def count_mentions(mention_list):
    cnt_dict = dict()
    for name in mention_list:
        name = name.lower()
        cnt = cnt_dict.get(name, 0)
        cnt_dict[name] = cnt + 1
    return cnt_dict


def gen_nom_list():
    edl_gold_train_file = 'e:/el/LDC2015E75/data/tac_kbp_2015_tedl_' \
                          'training_gold_standard_entity_mentions.tab'
    edl_gold_eval_file = 'e:/el/LDC2015E103/data/tac_kbp_2015_tedl_' \
                         'evaluation_gold_standard_entity_mentions.tab'

    nom_list_train = load_nom_mentions(edl_gold_train_file)
    nom_list_eval = load_nom_mentions(edl_gold_eval_file)
    print '%d nom mentions in eval' % len(nom_list_eval)

    cnt_dict_train = count_mentions(nom_list_train)
    cnt_dict_eval = count_mentions(nom_list_eval)

    eval_hit_cnt = 0
    for name, cnt in cnt_dict_eval.iteritems():
        train_cnt = cnt_dict_train.get(name, 0)
        if train_cnt:
            print name, cnt, train_cnt
            eval_hit_cnt += cnt
    print eval_hit_cnt


def gen_nom_dict():
    edl_gold_file = 'e:/el/LDC2015E75/data/tac_kbp_2015_tedl_' \
                    'training_gold_standard_entity_mentions.tab'
    nom_dict_file = 'e:/el/res/nom-dict-raw.txt'

    nom_list = load_nom_mentions(edl_gold_file)
    nom_cnt_dict = count_mentions(nom_list)
    nom_cnt_list = nom_cnt_dict.items()
    nom_cnt_list.sort(key=lambda x: -x[1])
    fout = open(nom_dict_file, 'wb')
    for nom, cnt in nom_cnt_list:
        fout.write('%s\t%d\n' % (nom, cnt))
    fout.close()


def __fix_edl_file_positions():
    edl_file = 'e:/el/LDC2015E75/data/tac_kbp_2015_tedl_training_gold_standard_entity_mentions.tab'
    dst_edl_file = 'e:/el/LDC2015E75/data/tac_kbp_2015_tedl_training_gold_fixed.tab'

    fin = open(edl_file, 'r')
    fout = open(dst_edl_file, 'wb')
    for line in fin:
        vals = line[:-1].split('\t')
        tmp_vals0 = vals[3].split(':')
        tmp_vals1 = tmp_vals0[1].split('-')
        beg_pos, end_pos = int(tmp_vals1[0]) - len(doc_head), int(tmp_vals1[1]) - len(doc_head)
        fout.write('%s\t%s\t%s\t%s:%d-%d' % (vals[0], vals[1], vals[2], tmp_vals0[0], beg_pos, end_pos))
        for val in vals[4:]:
            fout.write('\t%s' % val)
        fout.write('\n')
    fin.close()
    fout.close()


def __gen_docs_list():
    # dataset = 'LDC2015E75'
    # dataset = 'LDC2015E103'
    # dataset = 'LDC2016E63'

    # docs_dir = 'e:/data/edl'
    # docs_dir = 'e:/data/el/LDC2015E19/data/2009/eval/source_documents'
    # docs_list_file = 'e:/data/el/LDC2015E19/data/2009/eval/data/eng-docs-list-win.txt'
    docs_dir = 'e:/data/el/LDC2015E19/data/2010/eval/source_documents'
    docs_list_file = 'e:/data/el/LDC2015E19/data/2010/eval/data/eng-docs-list-win.txt'
    # docs_dir = 'e:/data/el/LDC2015E19/data/2011/eval/source_documents'
    # docs_list_file = 'e:/data/el/LDC2015E19/data/2011/eval/data/eng-docs-list-win.txt'
    # docs_dir = os.path.join(datadir, 'source_documents')
    # docs_dir = os.path.join(datadir, 'data/eng')
    # docs_list_file = os.path.join(datadir, 'data/eng-docs-list-win.txt')

    dir_list = [docs_dir]
    fout = open(docs_list_file, 'wb')
    while dir_list:
        d = dir_list.pop()
        file_names = [f for f in os.listdir(d)]
        file_names.sort()
        for f in file_names:
            cur_path = os.path.join(d, f)
            if os.path.isdir(cur_path):
                dir_list.append(cur_path)
            if os.path.isfile(cur_path):
                assert cur_path.endswith('xml')
                fout.write('%s\n' % cur_path)
    fout.close()


def __transform_mentions_file():
    # tab_file = 'e:/data/el/LDC2015E19/data/2009/eval/' \
    #            'tac_kbp_2009_english_entity_linking_evaluation_KB_links.tab'
    # xml_file = 'e:/data/el/LDC2015E19/data/2009/eval/' \
    #            'tac_kbp_2009_english_entity_linking_evaluation_queries.xml'
    # dst_file = 'e:/data/el/LDC2015E19/data/2009/eval/data/mentions.tab'

    tab_file = 'e:/data/el/LDC2015E19/data/2010/eval/' \
               'tac_kbp_2010_english_entity_linking_evaluation_KB_links.tab'
    xml_file = 'e:/data/el/LDC2015E19/data/2010/eval/' \
               'tac_kbp_2010_english_entity_linking_evaluation_queries.xml'
    dst_file = 'e:/data/el/LDC2015E19/data/2010/eval/data/mentions.tab'

    # tab_file = 'e:/data/el/LDC2015E19/data/2011/eval/' \
    #            'tac_kbp_2011_english_entity_linking_evaluation_KB_links.tab'
    # xml_file = 'e:/data/el/LDC2015E19/data/2011/eval/' \
    #            'tac_kbp_2011_english_entity_linking_evaluation_queries.xml'
    # dst_file = 'e:/data/el/LDC2015E19/data/2011/eval/data/mentions.tab'
    prev_mentions_format_to_new(tab_file, xml_file, dst_file)


def main():
    # gen_nom_dict()
    __gen_docs_list()
    # __transform_mentions_file()
    # __fix_edl_file_positions()

if __name__ == '__main__':
    main()
