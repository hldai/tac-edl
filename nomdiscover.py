import re
from itertools import izip
from utils import doc_id_from_path, match_raw_text
from mention import Mention
from doctext import next_doc_text_blocks

doc_head = '<?xml version="1.0" encoding="utf-8"?>\n'


def load_nom_dict(nom_dict_file, tolc=True):
    f = open(nom_dict_file, 'r')
    noms = set()
    for line in f:
        vals = line[:-1].split('\t')
        nom_name = vals[0].lower() if tolc else vals[0]
        noms.add(nom_name)
    f.close()
    return noms


def __load_doc_list(doc_list_file):
    doc_list = list()
    f = open(doc_list_file, 'r')
    for line in f:
        doc_list.append(line[:-1])
    f.close()
    return doc_list


def extract_nom_mentions(text, nom_name_list):
    text_lc = text.lower()

    text_len = len(text_lc)
    mention_list = list()
    for nom_name in nom_name_list:
        miter = re.finditer(nom_name, text_lc)
        for m in miter:
            if m.start() > 0 and text_lc[m.start() - 1].isalpha():
                continue

            if m.end() < text_len and text_lc[m.end()].isalpha():
                continue

            exist = False
            for pm in mention_list:
                if pm.beg_pos <= m.start() and pm.end_pos >= m.end():
                    exist = True
                    break

            if not exist:
                mention = Mention(name=m.group(0), beg_pos=m.start(), end_pos=m.end(), entity_type='PER',
                                  mention_type='NOM')
                mention_list.append(mention)

    return mention_list


# def extract_nom_mentions_in_doc(doc_path, noms):
#     f = open(doc_path, 'r')
#     doc_text = f.read()
#     f.close()
#
#     doc_text = doc_text.decode('utf-8')
#     text_span_list = extract_text(doc_text)
#     # text_span_list = [(0, len(doc_text))]
#
#     doc_id = doc_id_from_path(doc_path)
#
#     mention_list = list()
#     for s in text_span_list:
#         cur_mention_list = extract_nom_mentions(doc_text[s[0]:s[1]], noms)
#         for m in cur_mention_list:
#             m.docid = doc_id
#             m.beg_pos += s[0] - len(doc_head)
#             m.end_pos += s[0] - len(doc_head) - 1
#         # for m in cur_mention_list:
#         # for i in xrange(len(cur_mention_list)):
#         #     m = cur_mention_list[i]
#         #     cur_mention_list[i] = (m[0], m[1] + s[0] - len(doc_head), m[2] + s[0] - len(doc_head) - 1)
#             # m[1] += s[0] - len(doc_head)
#             # m[2] += s[0] - len(doc_head) - 1
#         mention_list += cur_mention_list
#     return mention_list


# TODO use method in Mention
# arrange mentions to a dict, { docid -> mentions-in-doc }
def __arrange_mentions_by_docid(mention_list):
    doc_mentions_dict = dict()
    for m in mention_list:
        # if m.mention_type != 'NOM':
        #     continue
        mlist = doc_mentions_dict.get(m.docid, list())
        if mlist:
            mlist.append(m)
        else:
            mlist.append(m)
            doc_mentions_dict[m.docid] = mlist
    return doc_mentions_dict


def __evaluation(sys_mention_list, gold_mention_list):
    doc_sys_mention_dict = __arrange_mentions_by_docid(sys_mention_list)
    doc_gold_mention_dict = __arrange_mentions_by_docid(gold_mention_list)

    result_list = list()
    hit_cnt, sys_cnt, gold_cnt = 0, 0, 0
    for docid, sys_mentions in doc_sys_mention_dict.iteritems():
        gold_mentions = doc_gold_mention_dict.get(docid, list())
        nom_gold_mentions = [m for m in gold_mentions if m.mention_type == 'NOM']

        sys_cnt += len(sys_mentions)
        gold_cnt += len(nom_gold_mentions)
        for sm in sys_mentions:
            hit = False
            for gm in nom_gold_mentions:
                if sm.beg_pos != gm.beg_pos or sm.end_pos != gm.end_pos:
                    continue
                hit = True
                hit_cnt += 1
                break
            result_list.append((docid, sm.name, sm.tags, hit, sm.beg_pos, sm.end_pos))

    result_list.sort(key=lambda x: x[1])
    for docid, name, tags, hit, beg_pos, end_pos in result_list:
        print '%s\t%s\t%s\t%s\t%d\t%d' % (docid, name, tags, hit, beg_pos, end_pos)

    prec = float(hit_cnt) / sys_cnt
    recall = float(hit_cnt) / gold_cnt
    f1 = 2 * prec * recall / (prec + recall)
    print '#hit: %d, #sys: %d, #gold: %d' % (hit_cnt, sys_cnt, gold_cnt)
    print 'prec: %f, recall: %f, f1: %f' % (prec, recall, f1)


# def __extract_nom_mentions_for_dataset():
#     nom_dict_file = 'e:/el/res/nom-dict-edit.txt'
#     doc_list_file = 'e:/el/LDC2015E103/data/eng-docs-list.txt'
#     edl_gold_file = 'e:/el/LDC2015E103/data/tac_kbp_2015_tedl_evaluation_gold_standard_entity_mentions.tab'
#
#     all_gold_mentions = Mention.load_edl_file(edl_gold_file)
#
#     noms = load_nom_dict(nom_dict_file)
#     sys_mention_list = list()
#     doc_list = __load_doc_list(doc_list_file)
#     # print doc_list[:10]
#     hit_cnt, sys_cnt, gold_cnt = 0, 0, 0
#     for doc_path in doc_list:
#         # if doc_path.endswith('.df.xml'):
#         #     continue
#         print doc_path
#
#         mention_list = extract_nom_mentions_in_doc(doc_path, noms)
#         sys_mention_list += mention_list
#         sys_cnt += len(mention_list)
#         # break
#
#     __evaluation(sys_mention_list, all_gold_mentions)


def __read_text(num_lines, f):
    text = ''
    for i in xrange(num_lines):
        text += f.next()
    return text.decode('utf-8')


def __read_tagged_words(num_lines, f):
    words, tags = list(), list()
    for i in xrange(num_lines):
        tmp_line = f.next()
        tmp_vals = tmp_line[:-1].split('\t')
        words.append(tmp_vals[0].decode('utf-8'))
        tags.append(tmp_vals[1])
    return words, tags


def __find_words(text_beg, text_end, word_span_list, words):
    beg_idx, end_idx = -1, -1
    for i, p in enumerate(word_span_list):
        if p[0] == text_beg:
            beg_idx = i

        if p[1] == text_end:
            end_idx = i + 1
            break

    if end_idx == -1 or beg_idx == -1:
        beg_idx, end_idx = -1, -1
    return beg_idx, end_idx


def __nom_mentions_to_file(mention_list, dst_file):
    fout = open(dst_file, 'wb')
    for m in mention_list:
        fout.write('%s\t%s\t%d\t%d\t%s\tNOM\n' % (m.name, m.docid, m.beg_pos, m.end_pos, m.entity_type))
    fout.close()


def __extract_nom_mentions_et():
    datadir = '/home/dhl/data/EDL/'
    nom_dict_file = datadir + 'res/nom-dict-edit.txt'
    text_file = datadir + 'LDC2015E103/data/doc-text.txt'
    tagged_words_file = datadir + 'LDC2015E103/data/doc-text-pos.txt'
    edl_gold_file = datadir + 'LDC2015E103/data/tac_kbp_2015_tedl_evaluation_gold_standard_entity_mentions.tab'
    dst_nom_mentions_file = datadir + 'LDC2015E103/result/nom-mentions.txt'

    all_gold_mentions = Mention.load_edl_file(edl_gold_file)

    noms = load_nom_dict(nom_dict_file)
    nom_name_list = [n for n in noms]
    nom_name_list.sort(key=lambda x: -len(x))

    mention_list = list()

    pre_docid = ''
    f_text = open(text_file, 'r')
    f_tw = open(tagged_words_file, 'r')
    while True:
        docid, texts, text_pos_spans = next_doc_text_blocks(f_text)
        if not docid:
            break
        print docid

        for text, text_pos_span in izip(texts, text_pos_spans):
            line = f_tw.next()
            vals = line.rstrip().split('\t')
            num_lines = int(vals[0])
            assert docid == vals[1]

            words, tags = __read_tagged_words(num_lines, f_tw)
            word_span_list = match_raw_text(text, words)
            tmp_mention_list = extract_nom_mentions(text, nom_name_list)
            for m in tmp_mention_list:
                beg_idx, end_idx = __find_words(m.beg_pos, m.end_pos, word_span_list, words)
                m.tags = tags[beg_idx:end_idx]
                # print m.name, m.tags
                if 'NN' not in m.tags:
                    continue

                m.docid = docid
                m.beg_pos += text_pos_span[0]
                m.end_pos += text_pos_span[0] - 1
                mention_list.append(m)
    f_text.close()
    f_tw.close()

    __nom_mentions_to_file(mention_list, dst_nom_mentions_file)
    __evaluation(mention_list, all_gold_mentions)


def main():
    # __extract_nom_mentions_for_dataset()
    __extract_nom_mentions_et()


if __name__ == '__main__':
    main()
