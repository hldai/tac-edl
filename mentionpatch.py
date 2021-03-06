import re
import os
from itertools import izip

from mention import Mention
from doctext import doc_id_from_path, next_doc_text_blocks
from utils import match_raw_text, next_ner_result, load_doc_paths

doc_head = '<?xml version="1.0" encoding="utf-8"?>\n'


def __find_post_authors(text):
    name_list, span_list = list(), list()
    miter_pa = re.finditer('<post.*?author="\s*(.*?)\s*"', text)
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


def __find_post_authors_in_doc(docid, doc_file_text, text_blocks, text_spans):
    pa_mentions = list()
    names, spans = __find_post_authors(doc_file_text)
    for sp in spans:
        m = Mention(name=doc_file_text[sp[0]:sp[1]], beg_pos=sp[0],
                    end_pos=sp[1] - 1, docid=docid, mention_type='NAM', entity_type='PER-PA')
        pa_mentions.append(m)

    names_set = set()
    for name in names:
        if len(name) > 1:
            names_set.add(name)

    mention_names, mention_spans = __find_names_in_text_blocks(names_set, text_blocks, text_spans)
    for mn, ms in izip(mention_names, mention_spans):
        m = Mention(name=mn, beg_pos=ms[0], end_pos=ms[1], docid=docid, mention_type='NAM', entity_type='PER-PA')
        pa_mentions.append(m)

    return pa_mentions


# TODO mentions in text
def __find_nw_author(docid, doc_file_text):
    m = re.search('<AUTHOR>\s*(.*?)\s*</AUTHOR>', doc_file_text)
    if not m:
        return None

    mentions = list()
    # print m.group(1)
    authors = re.split(',\s*', m.group(1))
    for author in authors:
        # print author
        beg_pos = m.group(1).index(author) + m.span(1)[0]
        end_pos = beg_pos + len(author) - 1
        mention = Mention(name=author, beg_pos=beg_pos, end_pos=end_pos, docid=docid,
                          mention_type='NAM', entity_type='PER-PA')
        mentions.append(mention)
    return mentions


def __extract_post_author_mentions(doc_list_file, text_file, dst_post_authors_file):
    f_text = open(text_file, 'r')
    fout = open(dst_post_authors_file, 'wb')
    doc_paths = load_doc_paths(doc_list_file)
    for i, doc_path in enumerate(doc_paths):
        docid_text, texts, text_spans = next_doc_text_blocks(f_text)

        docid = doc_id_from_path(doc_path)
        assert docid_text == docid

        doc_file = open(doc_path, 'r')
        doc_file_text = doc_file.read().decode('utf-8')
        doc_file.close()

        if doc_file_text.startswith(doc_head):
            doc_file_text = doc_file_text[len(doc_head):]

        if '_DF_' in doc_path or 'discussion_forum' in doc_path or 'df' in doc_path:
            mentions = __find_post_authors_in_doc(docid, doc_file_text, texts, text_spans)
        else:
            mentions = __find_nw_author(docid, doc_file_text)

        if mentions:
            for m in mentions:
                m.to_edl_file(fout)

        if (i + 1) % 1000 == 0:
            print i + 1
    fout.close()
    f_text.close()


# TODO use utils.find_phrases_in_words
def __match_names_by_words(names, words):
    hit_spans, hit_indices = list(), list()
    num_words = len(words)
    for i in xrange(num_words):
        for j, name in enumerate(names):
            num_words_in_name = len(name)
            if i + num_words_in_name > num_words:
                continue

            hit = True
            for k in xrange(num_words_in_name):
                if name[k] != words[i + k]:
                    hit = False
                    break

            if hit:
                hit_spans.append((i, i + num_words_in_name))
                hit_indices.append(j)
    return hit_spans, hit_indices


def __load_name_alias_file(name_alias_dict_file):
    names = dict()
    f = open(name_alias_dict_file, 'r')
    for line in f:
        vals = line.rstrip().split('\t')
        names[vals[0].decode('utf-8')] = vals[1]
        for i in xrange(2, len(vals)):
            names[vals[i].decode('utf-8')] = vals[1]
    f.close()
    return names


def __load_name_dict(name_dict_file):
    names = dict()
    f = open(name_dict_file, 'r')
    for line in f:
        vals = line.rstrip().split('\t')
        names[vals[0].decode('utf-8')] = vals[1]
    f.close()
    return names


def __tokenize_names(names_set):
    tokenized_names = list()
    for name in names_set:
        tokenized_names.append(name.split(' '))
    return tokenized_names


def __extract_name_dict_mentions(name_alias_file, text_file, words_file, dst_adj_gpe_mentions_file):
    names_dict = __load_name_alias_file(name_alias_file)
    entity_types = names_dict.values()
    names = __tokenize_names(names_dict.keys())

    cnt = 0
    fin0 = open(text_file, 'r')
    fin1 = open(words_file, 'r')
    fout = open(dst_adj_gpe_mentions_file, 'wb')
    while True:
        docid, texts, spans = next_doc_text_blocks(fin0)
        if not docid:
            break

        for text, span in izip(texts, spans):
            text_new = text.replace('al-', 'Al-')
            text_new = re.sub('[/-]', ' ', text_new)
            text_new = text_new.replace('\n\n', '.\n')
            words, tags = next_ner_result(fin1)

            pos_spans = match_raw_text(text_new, words)
            hit_idx_spans, name_indices = __match_names_by_words(names, words)

            for hit_idx_span, name_idx in izip(hit_idx_spans, name_indices):
                beg_pos, end_pos = pos_spans[hit_idx_span[0]][0], pos_spans[hit_idx_span[1] - 1][1]
                name = text[beg_pos:end_pos].replace('\n', ' ')
                m = Mention(name=name, beg_pos=beg_pos + span[0], end_pos=end_pos + span[0] - 1, docid=docid,
                            mention_type='NAM', entity_type=entity_types[name_idx])
                m.to_edl_file(fout)
                # fout.write('%s\t%s\t%d\t%d\t%s\tNAM\n' % (name.encode('utf-8'), docid, beg_pos + span[0],
                #                                           end_pos + span[0] - 1, entity_types[name_idx]))

        cnt += 1
        if cnt % 10 == 0:
            print cnt, docid
    fin0.close()
    fin1.close()
    fout.close()


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
    # doc_mentions = __load_mentions_file(mention_file)
    doc_mentions = Mention.load_edl_file(mention_file, True)
    f_text = open(text_file, 'r')
    fout = open(dst_extra_mentions_file, 'wb')
    cnt = 0
    while True:
        docid, texts, spans = next_doc_text_blocks(f_text)
        if not docid:
            break

        cur_mentions = doc_mentions.get(docid, list())
        extra_mentions = __find_extra_mentions(cur_mentions, texts, spans)
        for m in extra_mentions:
            m.to_edl_file(fout)
            # fout.write('%s\t%s\t%d\t%d\t%s\t%s\n' % (m.name.encode('utf-8'), m.docid, m.beg_pos, m.end_pos,
            #                                          m.entity_type, m.mention_type))

        cnt += 1
        if cnt % 100 == 0:
            print cnt, docid
    f_text.close()
    fout.close()


def main():
    # dataset = 'LDC2015E75'
    dataset = 'LDC2015E103'
    # dataset = 'LDC2016E63'

    ner_tag = '1'

    # datadir = '/home/dhl/data/EDL/'
    datadir = 'e:/data/edl'

    name_alias_file = os.path.join(datadir, 'res/names-dict.txt')

    doc_list_file = os.path.join(datadir, dataset, 'data/eng-docs-list-win.txt')
    text_file = os.path.join(datadir, dataset, 'data/doc-text.txt')
    words_file = os.path.join(datadir, dataset, 'output/ner-result1.txt')
    ner_mentions_file = os.path.join(datadir, dataset, 'output/ner-mentions-%s.tab' % ner_tag)
    dst_post_authors_file = os.path.join(datadir, dataset, 'output/post-authors.tab')
    dst_name_dict_mentions_file = os.path.join(datadir, dataset, 'output/name-dict-mentions.tab')
    dst_extra_mentions_file = os.path.join(datadir, dataset, 'output/ner-expanded-%s.tab' % ner_tag)

    print 'extract post authors'
    # __extract_post_author_mentions(doc_list_file, text_file, dst_post_authors_file)

    print 'extract names in dict'
    # __extract_name_dict_mentions(name_alias_file, text_file, words_file, dst_name_dict_mentions_file)

    print 'expand mentions'
    __mention_expand(text_file, ner_mentions_file, dst_extra_mentions_file)


if __name__ == '__main__':
    main()
