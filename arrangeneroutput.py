from itertools import izip

from utils import match_raw_text, next_ner_result
from doctext import next_doc_text_blocks
from mention import Mention


def __write_result(docid, text_orig, text_new, text_pos, words, tags, fout):
    word_span_list = match_raw_text(text_new, words)

    prev_tag = ''
    beg_pos, end_pos = 0, 0

    def __write_mention():
        mention_name = text_orig[beg_pos:end_pos].replace('\n', ' ')
        if '&lt;' in mention_name or 'http:' in mention_name or '&gt;' in mention_name:
            return
        fout.write('%s\t%s\t%d\t%d\t%s\t%s\n' % (mention_name.encode('utf-8'), docid, text_pos + beg_pos,
                                                 text_pos + end_pos - 1, prev_tag, 'NAM'))

    cur_mention_beg_idx = -1
    for i, (word, tag) in enumerate(izip(words, tags)):
        if tag != prev_tag:
            if cur_mention_beg_idx != -1:
                # print words[cur_mention_beg_idx:i], prev_tag
                beg_pos, end_pos = word_span_list[cur_mention_beg_idx][0], word_span_list[i - 1][1]
                __write_mention()
                cur_mention_beg_idx = -1
            if tag != 'O':
                cur_mention_beg_idx = i
        prev_tag = tag

    if cur_mention_beg_idx != -1:
        beg_pos, end_pos = word_span_list[cur_mention_beg_idx][0], word_span_list[-1][1]
        __write_mention()


def __fix_entity_types(mentions):
    for m in mentions:
        if m.entity_type == 'PERSON':
            m.entity_type = 'PER'
        elif m.entity_type == 'ORGANIZATION':
            m.entity_type = 'ORG'
        elif m.entity_type == 'LOCATION':
            m.entity_type = 'GPE'


def __get_mentions(docid, text_orig, text_new, text_pos, words, tags):
    word_span_list = match_raw_text(text_new, words)

    prev_tag = ''
    beg_pos, end_pos = 0, 0
    mentions = list()

    def __add_mention():
        mention_name = text_orig[beg_pos:end_pos].replace('\n', ' ')
        if '&lt;' in mention_name or 'http:' in mention_name or '&gt;' in mention_name:
            return
        m = Mention(name=mention_name, beg_pos=text_pos + beg_pos, end_pos=text_pos + end_pos - 1,
                    docid=docid, entity_type=prev_tag, mention_type='NAM')
        mentions.append(m)

    cur_mention_beg_idx = -1
    for i, (word, tag) in enumerate(izip(words, tags)):
        if tag != prev_tag:
            if cur_mention_beg_idx != -1:
                # print words[cur_mention_beg_idx:i], prev_tag
                beg_pos, end_pos = word_span_list[cur_mention_beg_idx][0], word_span_list[i - 1][1]
                __add_mention()
                cur_mention_beg_idx = -1
            if tag != 'O':
                cur_mention_beg_idx = i
        prev_tag = tag

    if cur_mention_beg_idx != -1:
        beg_pos, end_pos = word_span_list[cur_mention_beg_idx][0], word_span_list[-1][1]
        __add_mention()

    __fix_entity_types(mentions)
    return mentions


def __mention_exist(mention, mentions):
    for m in mentions:
        if m.beg_pos == mention.beg_pos and m.end_pos == mention.end_pos:
            return True


def __write_mentions(mentions, fout):
    for m in mentions:
        fout.write('%s\t%s\t%d\t%d\t%s\t%s\n' % (m.name.encode('utf-8'), m.docid, m.beg_pos, m.end_pos,
                                                    m.entity_type, m.mention_type))


def arrange_ner_result(doc_text_file, ner_result_files, dst_tac_edl_file):
    print ner_result_files

    f_text = open(doc_text_file, 'r')
    f_ners = list()
    for f in ner_result_files:
        f_ners.append(open(f, 'r'))
    fout = open(dst_tac_edl_file, 'wb')
    while True:
        docid, texts, spans = next_doc_text_blocks(f_text)

        if not docid:
            break

        mentions = list()
        for text, span in izip(texts, spans):
            text_new = text.replace('al-', 'Al-')
            for f_ner in f_ners:
                words, tags = next_ner_result(f_ner)
                cur_mentions = __get_mentions(docid, text, text_new, span[0], words, tags)
                for m in cur_mentions:
                    if not __mention_exist(m, mentions):
                        mentions.append(m)
        __write_mentions(mentions, fout)
    f_text.close()
    for f in f_ners:
        f.close()
    fout.close()


def main():
    dataset = 75
    datadir = '/home/dhl/data/EDL/'
    if dataset == 75:
        doc_text_file = datadir + 'LDC2015E75/data/doc-text.txt'
        ner_result_file0 = datadir + 'LDC2015E75/data/ner-result0.txt'
        ner_result_file1 = datadir + 'LDC2015E75/data/ner-result1.txt'
        dst_mention_file = datadir + 'LDC2015E75/data/ner-mentions.txt'
    else:
        doc_text_file = datadir + 'LDC2015E103/data/doc-text.txt'
        ner_result_file0 = datadir + 'LDC2015E103/data/ner-result0.txt'
        ner_result_file1 = datadir + 'LDC2015E103/data/ner-result1.txt'
        dst_mention_file = datadir + 'LDC2015E103/data/ner-mentions.txt'

    arrange_ner_result(doc_text_file, [ner_result_file0, ner_result_file1], dst_mention_file)

if __name__ == '__main__':
    main()
