import os

doc_head = '<?xml version="1.0" encoding="utf-8"?>\n'


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


def __gen_docs_list():
    docs_dir = '/home/dhl/data/EDL/LDC2015E103/data/eng-docs'
    docs_list_file = '/home/dhl/data/EDL/LDC2015E103/data/eng-docs-list.txt'

    # docs_dir = '/home/dhl/data/EDL/LDC2015E75/data/eng-docs'
    # docs_list_file = '/home/dhl/data/EDL/LDC2015E75/data/eng-docs-list.txt'

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
                fout.write('%s\n' % cur_path)
    fout.close()


def fix_edl_file_positions():
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


def main():
    # gen_nom_dict()
    __gen_docs_list()
    # fix_edl_file_positions()

if __name__ == '__main__':
    main()
