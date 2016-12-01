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


# split by \n+, return spans
def __split_mention_name(mention_name, docid, mention_beg_pos, entity_type):
    beg_pos = 0
    end_pos = 1
    name_len = len(mention_name)
    tmp_spans = list()
    while beg_pos < name_len:
        while end_pos < name_len and mention_name[end_pos] != '\n':
            end_pos += 1
        tmp_spans.append((beg_pos, end_pos - 1))

        beg_pos = end_pos
        while beg_pos < name_len and mention_name[beg_pos] == '\n':
            beg_pos += 1
        end_pos = beg_pos + 1

    mentions = list()
    for sp in tmp_spans:
        beg_pos, end_pos = sp
        while beg_pos <= end_pos and mention_name[beg_pos].isspace():
            beg_pos += 1
        while end_pos >= beg_pos and mention_name[end_pos].isspace():
            end_pos -= 1
        if end_pos >= beg_pos:
            # if docid == 'ENG_DF_001503_20130716_G00A0AUYI':
            #     print '###name:', mention_name[beg_pos:end_pos + 1]
            m = Mention(name=mention_name[beg_pos:end_pos + 1], beg_pos=mention_beg_pos + beg_pos,
                        end_pos=mention_beg_pos + end_pos, docid=docid, entity_type=entity_type,
                        mention_type='NAM')
            mentions.append(m)
    return mentions


def __handle_mention(docid, text_orig, text_pos, beg_pos, end_pos, entity_type, dst_mentions):
    tmp_mention_name = text_orig[beg_pos:end_pos]

    if '&lt;' in tmp_mention_name or 'http:' in tmp_mention_name or '&gt;' in tmp_mention_name \
            or '\t' in tmp_mention_name or '<' in tmp_mention_name or '>' in tmp_mention_name:
        return

    num_nls = tmp_mention_name.count('\n')
    # if docid == 'ENG_DF_001503_20130716_G00A0AUYI':
    #     print num_nls, text_pos, beg_pos, end_pos, tmp_mention_name
    if num_nls == 0:
        m = Mention(name=tmp_mention_name, beg_pos=text_pos + beg_pos, end_pos=text_pos + end_pos - 1,
                    docid=docid, entity_type=entity_type, mention_type='NAM')
        dst_mentions.append(m)
    elif num_nls == 1:
        if beg_pos > 0 and text_orig[beg_pos - 1] == '\n':
            dst_mentions += __split_mention_name(tmp_mention_name, docid, text_pos + beg_pos, entity_type)
        else:
            tmp_mention_name = tmp_mention_name.replace('\n', ' ')
            m = Mention(name=tmp_mention_name, beg_pos=text_pos + beg_pos, end_pos=text_pos + end_pos - 1,
                        docid=docid, entity_type=entity_type, mention_type='NAM')
            dst_mentions.append(m)
    else:
        # if docid == 'ENG_DF_001503_20130716_G00A0AUYI':
        #     print 'TTTTT'
        dst_mentions += __split_mention_name(tmp_mention_name, docid, text_pos + beg_pos, entity_type)


def __get_mentions(docid, text_orig, text_new, text_pos, words, tags):
    word_span_list = match_raw_text(text_new, words)

    prev_tag = ''
    beg_pos, end_pos = 0, 0
    mentions = list()

    # def __add_mention():
    #     mention_name = text_orig[beg_pos:end_pos].replace('\n', ' ')
    #     # if docid == 'NYT_ENG_20130426.0196':
    #     #     print mention_name
    #     if '&lt;' in mention_name or 'http:' in mention_name or '&gt;' in mention_name or '\t' in mention_name\
    #             or '<' in mention_name or '>' in mention_name:
    #         return
    #     m = Mention(name=mention_name, beg_pos=text_pos + beg_pos, end_pos=text_pos + end_pos - 1,
    #                 docid=docid, entity_type=prev_tag, mention_type='NAM')
    #     mentions.append(m)

    cur_mention_beg_idx = -1
    for i, (word, tag) in enumerate(izip(words, tags)):
        if tag != prev_tag:
            if cur_mention_beg_idx != -1:
                # print words[cur_mention_beg_idx:i], prev_tag
                beg_pos, end_pos = word_span_list[cur_mention_beg_idx][0], word_span_list[i - 1][1]
                # __add_mention()
                __handle_mention(docid, text_orig, text_pos, beg_pos, end_pos, prev_tag, mentions)
                cur_mention_beg_idx = -1
            if tag != 'O':
                cur_mention_beg_idx = i
        prev_tag = tag

    if cur_mention_beg_idx != -1:
        beg_pos, end_pos = word_span_list[cur_mention_beg_idx][0], word_span_list[-1][1]
        # __add_mention()
        __handle_mention(docid, text_orig, text_pos, beg_pos, end_pos, prev_tag, mentions)

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

        # if docid != 'ENG_DF_001487_20150628_F001000DV':
        #     continue

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


def main():
    # dataset = 'LDC2015E75'
    dataset = 'LDC2015E103'
    # dataset = 'LDC2016E63'
    # datadir = '/home/dhl/data/EDL/'
    datadir = 'e:/data/edl/'

    doc_text_file = os.path.join(datadir, dataset, 'data/doc-text.txt')
    ner_result_file0 = os.path.join(datadir, dataset, 'output/ner-result0.txt')
    ner_result_file1 = os.path.join(datadir, dataset, 'output/ner-result1.txt')
    mentions_edl_file = os.path.join(datadir, dataset, 'output/ner-mentions-0-tmp.tab')

    __arrange_ner_result(doc_text_file, ner_result_file0, ner_result_file1, mentions_edl_file)

    dst_mentions_edl_file = os.path.join(datadir, dataset, 'output/ner-mentions-0.tab')
    __remove_leading_the(mentions_edl_file, dst_mentions_edl_file)

    # zner_edl_file = os.path.join(datadir, dataset, 'output/zhang-ner-mentions.tab')
    # dst_zner_edl_file = os.path.join(datadir, dataset, 'output/ner-mentions-1.tab')
    # __remove_leading_the(zner_edl_file, dst_zner_edl_file)

if __name__ == '__main__':
    main()
