from itertools import izip
import os
import re

from utils import match_raw_text, next_ner_result
from doctext import next_doc_text_blocks
from mention import Mention


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
        # if docid == 'NYT_ENG_20130426.0196':
        #     print mention_name
        if '&lt;' in mention_name or 'http:' in mention_name or '&gt;' in mention_name or '\t' in mention_name\
                or '<' in mention_name or '>' in mention_name:
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


def __arrange_ner_result(doc_text_file, ner_file0, ner_file1, dst_tac_edl_file):
    f_text = open(doc_text_file, 'r')
    f_ner0 = open(ner_file0, 'r')
    f_ner1 = open(ner_file1, 'r')
    fout = open(dst_tac_edl_file, 'wb')
    cnt = 0
    while True:
        docid, texts, spans = next_doc_text_blocks(f_text)

        if not docid:
            break

        mentions = list()
        for text, span in izip(texts, spans):
            text_new = text.replace('al-', 'Al-')
            text_new = re.sub('\n(\n+)', '.\g<1>', text_new)
            words, tags = next_ner_result(f_ner0)
            # if docid == 'NYT_ENG_20130426.0196':
            #     print
            #     print text
            #     print words
            #     print tags
            mentions += __get_mentions(docid, text, text_new, span[0], words, tags)

            text_new = re.sub('[/-]', ' ', text_new)
            words, tags = next_ner_result(f_ner1)
            tmp_mentions = __get_mentions(docid, text, text_new, span[0], words, tags)
            for m in tmp_mentions:
                if not __mention_exist(m, mentions):
                    mentions.append(m)
        for m in mentions:
            m.to_edl_file(fout)

        cnt += 1
        if cnt % 1000 == 0:
            print cnt, docid
        # __write_mentions(mentions, fout)
    f_text.close()
    f_ner0.close()
    f_ner1.close()
    fout.close()


def __remove_leading_the(metions_file, dst_mentions_edl_file):
    mentions = Mention.load_edl_file(metions_file)
    for m in mentions:
        if m.name.startswith('the '):
            m.name = m.name[4:]
            m.beg_pos += 4

    Mention.save_as_edl_file(mentions, dst_mentions_edl_file)


# def __arrange_stanford_ner(doc_text_file, ner_result_file0, ner_result_file1, dst_mention_file):


def main():
    # dataset = 'LDC2015E75'
    dataset = 'LDC2015E103'
    # dataset = 'LDC2016E63'
    # datadir = '/home/dhl/data/EDL/'
    datadir = 'e:/data/edl/'

    doc_text_file = os.path.join(datadir, dataset, 'data/doc-text.txt')
    ner_result_file0 = os.path.join(datadir, dataset, 'output/ner-result0.txt')
    ner_result_file1 = os.path.join(datadir, dataset, 'output/ner-result1.txt')
    mentions_edl_file = os.path.join(datadir, dataset, 'output/stanford-ner-mentions.tab')

    __arrange_ner_result(doc_text_file, ner_result_file0, ner_result_file1, mentions_edl_file)

    dst_mentions_edl_file = os.path.join(datadir, dataset, 'output/ner-mentions-0.tab')
    __remove_leading_the(mentions_edl_file, dst_mentions_edl_file)

    # zner_edl_file = os.path.join(datadir, dataset, 'output/zhang-ner-mentions.tab')
    # dst_zner_edl_file = os.path.join(datadir, dataset, 'output/ner-mentions-1.tab')
    # __remove_leading_the(zner_edl_file, dst_zner_edl_file)

if __name__ == '__main__':
    main()
