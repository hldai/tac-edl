# get clean text from tac documents

import re
from itertools import izip
from bs4 import BeautifulSoup
import os

from utils import doc_id_from_path

docid_patterns = ['<doc\s+id="(.*?)"', '<DOC\s+id="(.*?)"']

nw_headline_pattern = '<HEADLINE>\s*(.*?)\s*</HEADLINE>'
df_headline_pattern = '<headline>\s*(.*?)\s*</headline>'
dateline_pattern = '<DATELINE>\s*(.*?)\s*</DATELINE>'
datetime_pattern = '<DATETIME>\s*(.*?)\s*</DATETIME>'

nw_text_patterns = ['<P>\s*(.*?)\s*</P>', '<POST>\s*<POSTER>.*?</POSTER>\s*<POSTDATE>.*?</POSTDATE>\s*(.*?)\s*</POST>',
                    '<TEXT>\s*(.*?)\s*</TEXT>']

df_text_pattern = '<post.*?>\s*(.*?)\s*</post>'

quote_beg = '<quote'
quote_end = '</quote>'

doc_head = '<?xml version="1.0" encoding="utf-8"?>\n'


def read_text(fin, num_lines):
    text = ''
    for i in xrange(num_lines):
        text += fin.next()
    return text[:-1].decode('utf-8')


def next_doc_text_blocks(fin):
    try:
        line = fin.next()
        vals = line[:-1].split('\t')
        docid = vals[0]
        num_text_blocks = int(vals[1])
        texts = list()
        spans = list()
        for i in xrange(num_text_blocks):
            line = fin.next()
            vals = line[:-1].split('\t')
            num_lines, beg_pos, end_pos = int(vals[0]), int(vals[1]), int(vals[2])
            text = read_text(fin, num_lines)
            texts.append(text)
            spans.append((beg_pos, end_pos))
        return docid, texts, spans
    except StopIteration:
        return None, None, None


# remove quote
def __text_in_post(post_text, start_pos):
    text_list = list()
    text_beg, p = 0, 0
    quote_cnt = 0
    post_text_len = len(post_text)
    while p < post_text_len:
        cur_text = post_text[p:]

        if cur_text.startswith(quote_beg):
            if quote_cnt == 0 and p - text_beg > 0:
                text_list.append((text_beg + start_pos, p + start_pos))
            quote_cnt += 1
            p += len(quote_beg)

        if cur_text.startswith(quote_end):
            assert quote_cnt > 0
            quote_cnt -= 1
            p += len(quote_end)

            if quote_cnt == 0:
                text_beg = p + 1

        p += 1
    assert quote_cnt == 0

    text_list.append((text_beg + start_pos, p + start_pos))
    return text_list


def __get_text_spans(xml_text, text_pattern):
    text_span_list = list()
    miter = re.finditer(text_pattern, xml_text, re.DOTALL)
    for m in miter:
        text_span_list.append(m.span(1))
    return text_span_list


def __extract_text_nw(xml_text):
    head_line_spans = __get_text_spans(xml_text, nw_headline_pattern)
    dateline_spans = __get_text_spans(xml_text, dateline_pattern)
    datetime_spans = __get_text_spans(xml_text, datetime_pattern)
    if dateline_spans or datetime_spans:
        print xml_text
        exit()

    all_text_spans = head_line_spans + dateline_spans + datetime_spans

    for text_pattern in nw_text_patterns:
        text_spans = __get_text_spans(xml_text, text_pattern)
        if text_spans:
            all_text_spans += text_spans
            break

    assert all_text_spans
    return all_text_spans


def __extract_text_df(xml_text):
    head_line_spans = __get_text_spans(xml_text, df_headline_pattern)
    text_span_list = head_line_spans

    miter = re.finditer(df_text_pattern, xml_text, re.DOTALL)
    for m in miter:
        cur_text = m.group(1)
        post_text_span_list = __text_in_post(cur_text, m.span(1)[0])
        text_span_list += post_text_span_list

    # for text_span in text_span_list:
    #     print xml_text[text_span[0]:text_span[1]]
    #     print '############'
    #     print cur_text[text_start:]
    #     print '############'

    assert text_span_list
    return text_span_list


def __get_docid(xml_text):
    for p in docid_patterns:
        m = re.search(p, xml_text)
        if m:
            return m.group(1)
    return ''


def __extract_text_from_docs(doc_list_file, dst_text_file):
    fin_paths = open(doc_list_file, 'r')
    fout = open(dst_text_file, 'wb')
    for i, line in enumerate(fin_paths):
        doc_path = line[:-1]
        # if '_NW_' in doc_path:
        #     continue
        # if not doc_path.endswith('ENG_DF_000200_20150702_F001000DW.df.xml'):
        #     continue

        # read file
        doc_file = open(doc_path, 'r')
        doc_file_text = doc_file.read().decode('utf-8')
        doc_file.close()

        docid = __get_docid(doc_file_text)
        docid_path = doc_id_from_path(doc_path)
        if (i + 1) % 1000 == 0:
            print i + 1, docid

        assert docid == docid_path

        if 'nw' in doc_path:
            text_span_list = __extract_text_nw(doc_file_text)
        else:
            text_span_list = __extract_text_df(doc_file_text)

        doc_text_start_pos = 0
        if doc_file_text.startswith(doc_head):
            doc_text_start_pos = len(doc_head)

        fout.write('%s\t%d\n' % (docid, len(text_span_list)))
        for sp in text_span_list:
            cur_text = doc_file_text[sp[0]:sp[1]]
            num_lines = cur_text.count('\n') + 1
            fout.write('%d\t%d\t%d\n%s\n' % (num_lines, sp[0] - doc_text_start_pos, sp[1] - doc_text_start_pos - 1,
                                             cur_text.encode('utf-8')))
        # break
    fin_paths.close()
    fout.close()


def __in_text_process(prev_text_file, dst_text_file, keep_web_addr=True, split_by_doc=True):
    f = open(prev_text_file, 'r')
    fout = open(dst_text_file, 'wb')

    i = 0
    while True:
        docid, texts, spans = next_doc_text_blocks(f)
        if not docid:
            break

        if (i + 1) % 1000 == 0:
            print i + 1, docid
        i += 1

        if split_by_doc:
            fout.write('%s\t%d\n' % (docid, len(texts)))

        for cur_text, span in izip(texts, spans):
            cur_text = cur_text.replace('&lt;', '<')
            cur_text = cur_text.replace('&gt;', '>')
            cur_text = cur_text.replace('>', '> ')
            soup = BeautifulSoup(cur_text, 'html.parser')
            cur_text = soup.get_text()
            if not keep_web_addr:
                cur_text = re.sub('https?://\S*', ' ', cur_text)

            new_num_lines = cur_text.count('\n') + 1
            if split_by_doc:
                fout.write('%d\n%s\n' % (new_num_lines, cur_text.encode('utf-8')))
            else:
                fout.write('%d\t%s\t\n%s\n' % (new_num_lines, docid, cur_text.encode('utf-8')))
        # break
    f.close()
    fout.close()


def main():
    dataset = 'LDC2015E75'
    dataset = 'LDC2015E103'
    # dataset = 'LDC2016E63'

    datadir = '/home/dhl/data/EDL'

    doc_list_file = os.path.join(datadir, dataset, 'data/eng-docs-list.txt')
    dst_text_file0 = os.path.join(datadir, dataset, 'data/doc-text.txt')
    dst_text_file1 = os.path.join(datadir, dataset, 'data/doc-text-clean.txt')

    __extract_text_from_docs(doc_list_file, dst_text_file0)
    # __in_text_process(dst_text_file0, dst_text_file1, False, True)

if __name__ == '__main__':
    main()
