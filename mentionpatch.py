import re
from itertools import izip

from mention import Mention
from doctext import doc_id_from_path, next_doc_text_blocks
from utils import match_raw_text, next_ner_result

doc_head = '<?xml version="1.0" encoding="utf-8"?>\n'


def __load_doc_paths(doc_list_file):
    paths = list()
    f = open(doc_list_file, 'r')
    for line in f:
        paths.append(line[:-1])
    f.close()
    return paths


def __find_post_authors(text):
    name_list, span_list = list(), list()
    miter_pa = re.finditer('<post.*?author="(.*?)"', text)
    for m in miter_pa:
        name_list.append(m.group(1))
        span_list.append(m.span(1))
    return name_list, span_list


def __find_names_in_text_blocks(name_set, texts, spans):
    result_name_list = list()
    result_span_list = list()
    for name in name_set:
        for text, span, in izip(texts, spans):
            miter = re.finditer(re.escape(name), text)
            for m in miter:
                if m.start() > 0 and text[m.start() - 1].isalpha():
                    continue
                if m.end() < len(text) and text[m.end()].isalpha():
                    continue
                result_name_list.append(name)
                result_span_list.append((m.start() + span[0], m.end() + span[0] - 1))
    return result_name_list, result_span_list


def __extract_post_author_mentions(doc_list_file, text_file, dst_post_authors_file):
    f_text = open(text_file, 'r')
    fout = open(dst_post_authors_file, 'wb')
    doc_paths = __load_doc_paths(doc_list_file)
    for doc_path in doc_paths:
        docid_text, texts, text_spans = next_doc_text_blocks(f_text)

        if '_DF_' not in doc_path:
            continue

        doc_file = open(doc_path, 'r')
        doc_file_text = doc_file.read().decode('utf-8')
        doc_file.close()

        docid = doc_id_from_path(doc_path)

        assert docid_text == docid

        names, spans = __find_post_authors(doc_file_text)
        for sp in spans:
            fout.write('%s\t%s\t%d\t%d\tPER\tNAM\n' % (doc_file_text[sp[0]:sp[1]].encode('utf-8'), docid,
                                                       sp[0] - len(doc_head), sp[1] - len(doc_head) - 1))

        names_set = set()
        for name in names:
            names_set.add(name)
        mention_names, mention_spans = __find_names_in_text_blocks(names_set, texts, text_spans)
        for mn, ms in izip(mention_names, mention_spans):
            fout.write('%s\t%s\t%d\t%d\tPER\tNAM\n' % (mn, docid, ms[0], ms[1]))
    fout.close()
    f_text.close()


def __match_names_by_words(names, words):
    hit_spans = list()
    num_words = len(words)
    for i in xrange(num_words):
        for name in names:
            num_words_in_name = len(name)
            if i + num_words_in_name > num_words:
                continue

            hit = True
            for j in xrange(num_words_in_name):
                if name[j] != words[i + j]:
                    hit = False
                    break

            if hit:
                hit_spans.append((i, i + num_words_in_name))
    return hit_spans


def __load_name_dict(name_dict_file):
    names = set()
    f = open(name_dict_file, 'r')
    for line in f:
        names.add(line[:-1].decode('utf-8'))
    f.close()
    return names


def __tokenize_names(names_set):
    tokenized_names = list()
    for name in names_set:
        tokenized_names.append(name.split(' '))
    return tokenized_names


def __extract_name_dict_mentions(name_dict_file, text_file, words_file, dst_adj_gpe_mentions_file):
    names = __load_name_dict(name_dict_file)
    names = __tokenize_names(names)

    fin0 = open(text_file, 'r')
    fin1 = open(words_file, 'r')
    fout = open(dst_adj_gpe_mentions_file, 'wb')
    while True:
        docid, texts, spans = next_doc_text_blocks(fin0)
        if not docid:
            break

        print docid

        for text, span in izip(texts, spans):
            text_new = text.replace('al-', 'Al-')
            words, tags = next_ner_result(fin1)

            pos_spans = match_raw_text(text_new, words)
            hit_idx_spans = __match_names_by_words(names, words)

            for hit_idx_span in hit_idx_spans:
                beg_pos, end_pos = pos_spans[hit_idx_span[0]][0], pos_spans[hit_idx_span[1] - 1][1]
                name = text[beg_pos:end_pos].replace('\n', ' ')
                fout.write('%s\t%s\t%d\t%d\tGPE\tNAM\n' % (name.encode('utf-8'), docid, beg_pos + span[0],
                                                           end_pos + span[0] - 1))
    fin0.close()
    fin1.close()
    fout.close()


def __load_mentions_file(mention_file):
    mentions_of_docs = dict()
    f = open(mention_file, 'r')
    for line in f:
        vals = line[:-1].split('\t')
        m = Mention(name=vals[0].decode('utf-8'), docid=vals[1],
                    beg_pos=int(vals[2]), end_pos=int(vals[3]), entity_type=vals[4],
                    mention_type=vals[5])
        cur_doc_mentions = mentions_of_docs.get(vals[1], list())
        if not cur_doc_mentions:
            mentions_of_docs[vals[1]] = cur_doc_mentions
        cur_doc_mentions.append(m)
    f.close()
    return mentions_of_docs


def __match_name_in_text(name, text):
    match_spans = list()
    miter = re.finditer(re.escape(name), text)
    for m in miter:
        if m.start() > 0 and text[m.start() - 1].isalpha():
            continue
        if m.end() < len(text) and text[m.end()].isalpha():
            continue
        match_spans.append((m.start(), m.end() - 1))
    return match_spans


def __mention_exist(mention, mentions):
    for m in mentions:
        if m.beg_pos <= mention.beg_pos and m.end_pos >= mention.end_pos:
            return True


def __find_extra_mentions(cur_mentions, texts, text_pos_spans):
    for i in xrange(len(texts)):
        texts[i] = texts[i].replace('\n', ' ')

    extra_mention_candidates = list()
    met_mention_names = set()
    for m in cur_mentions:
        if m.name in met_mention_names:
            continue

        met_mention_names.add(m.name)

        for text, text_pos_span in izip(texts, text_pos_spans):
            match_spans = __match_name_in_text(m.name, text)
            for span in match_spans:
                em = Mention(name=m.name, beg_pos=span[0] + text_pos_span[0],
                             end_pos=span[1] + text_pos_span[0], docid=m.docid, mention_type=m.mention_type,
                             entity_type=m.entity_type)
                extra_mention_candidates.append(em)

    extra_mentions = list()
    for mc in extra_mention_candidates:
        if not __mention_exist(mc, cur_mentions):
            extra_mentions.append(mc)
    return extra_mentions


def __mention_expand(text_file, mention_file, dst_extra_mentions_file):
    doc_mentions = __load_mentions_file(mention_file)
    f_text = open(text_file, 'r')
    fout = open(dst_extra_mentions_file, 'wb')
    while True:
        docid, texts, spans = next_doc_text_blocks(f_text)
        if not docid:
            break

        print docid

        cur_mentions = doc_mentions.get(docid, list())
        extra_mentions = __find_extra_mentions(cur_mentions, texts, spans)
        for m in extra_mentions:
            fout.write('%s\t%s\t%d\t%d\t%s\t%s\n' % (m.name.encode('utf-8'), m.docid, m.beg_pos, m.end_pos,
                                                     m.entity_type, m.mention_type))
    f_text.close()
    fout.close()


def main():
    dataset = 103

    if dataset == 75:
        doc_list_file = 'e:/el/LDC2015E75/data/eng-docs-list.txt'
        text_file = 'e:/el/LDC2015E75/data/doc-text.txt'
        words_file = 'e:/el/LDC2015E75/data/ner-result1.txt'
        ner_mentions_file = 'e:/el/LDC2015E75/data/ner-mentions.txt'
        dst_post_authors_file = 'e:/el/LDC2015E75/data/post-authors.txt'
        dst_name_dict_mentions_file = 'e:/el/LDC2015E75/data/name-dict-mentions.txt'
        dst_extra_mentions_file = 'e:/el/LDC2015E75/data/ner-expanded.txt'
    else:
        doc_list_file = 'e:/el/LDC2015E103/data/eng-docs-list.txt'
        text_file = 'e:/el/LDC2015E103/data/doc-text.txt'
        words_file = 'e:/el/LDC2015E103/data/ner-result1.txt'
        ner_mentions_file = 'e:/el/LDC2015E103/data/ner-mentions.txt'
        dst_name_dict_mentions_file = 'e:/el/LDC2015E103/data/name-dict-mentions.txt'
        dst_post_authors_file = 'e:/el/LDC2015E103/data/post-authors.txt'
        dst_extra_mentions_file = 'e:/el/LDC2015E103/data/ner-expanded.txt'

    print 'extract post authors'
    # __extract_post_author_mentions(doc_list_file, text_file, dst_post_authors_file)

    name_dict_file = 'e:/el/res/name-dict.txt'
    print 'extract adj gpe mentions'
    # __extract_name_dict_mentions(name_dict_file, text_file, words_file, dst_name_dict_mentions_file)

    print 'expand mentions'
    __mention_expand(text_file, ner_mentions_file, dst_extra_mentions_file)

if __name__ == '__main__':
    main()
