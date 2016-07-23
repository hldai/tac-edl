# get clean text from tac documents

import re
from itertools import izip
from bs4 import BeautifulSoup

text_patterns = ['<HEADLINE>\s*(.*?)\s*</HEADLINE>', '<P>\s*(.*?)\s*</P>',
                 '<headline>\s*(.*?)\s*</headline>',
                 '<POST>\s*<POSTER>.*?</POSTER>\s*<POSTDATE>.*?</POSTDATE>\s*(.*?)\s*</POST>']
df_text_pattern = '<post id=.*?>\s*(.*?)\s*</post>'

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


def doc_id_from_path(doc_path):
    doc_id = ''
    last_slash = doc_path.rfind('/')
    last_rslash = doc_path.rfind('\\')
    beg_pos = last_slash + 1 if last_slash > last_rslash else last_rslash + 1
    if doc_path.endswith('.nw.xml') or doc_path.endswith('.df.xml'):
        doc_id = doc_path[beg_pos:-7]
    elif doc_path.endswith('.xml'):
        doc_id = doc_path[beg_pos:-4]
    else:
        assert False
    return doc_id


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


def __extract_text(xml_text):
    text_span_list = list()

    for p in text_patterns:
        miter = re.finditer(p, xml_text, re.DOTALL)
        # print p
        for m in miter:
            text_span_list.append(m.span(1))
            # print m.span(1), len(m.group(1))
            # print m.group(1)
        # break

    miter = re.finditer(df_text_pattern, xml_text, re.DOTALL)
    for m in miter:
        cur_text = m.group(1)
        # text_list.append(cur_text)
        # print m.span(1), len(m.group(1))
        # print m.group(1)
        post_text_span_list = __text_in_post(cur_text, m.span(1)[0])
        text_span_list += post_text_span_list

    # for text_span in text_span_list:
    #     print xml_text[text_span[0]:text_span[1]]
    #     print '############'
        # print cur_text[text_start:]
        # print '############'

    assert text_span_list

    return text_span_list


def __find_post_authors(text):
    pa_list = list()
    miter_pa = re.finditer('<post.*?author="(.*?)"', text)
    for m in miter_pa:
        pa_list.append(m.span(1))
    return pa_list


def __extract_text_from_docs(doc_list_file, dst_text_file):
    fin_paths = open(doc_list_file, 'r')
    fout = open(dst_text_file, 'wb')
    for line in fin_paths:
        doc_path = line[:-1]
        # if doc_path.endswith('.nw.xml'):
        #     continue
        # if not doc_path.endswith('ENG_DF_000200_20150702_F001000DW.df.xml'):
        #     continue

        # read file
        doc_file = open(doc_path, 'r')
        doc_file_text = doc_file.read().decode('utf-8')
        doc_file.close()

        docid = doc_id_from_path(doc_path)
        print docid

        # post_author_spans = __find_post_authors(doc_file_text)
        # for sp in post_author_spans:
        #     fout_pa.write('%s\t%s\t%d\t%d\tPER\tNAM\n' % (doc_file_text[sp[0]:sp[1]].encode('utf-8'), docid,
        #                                                   sp[0] - len(doc_head), sp[1] - len(doc_head) - 1))

        text_span_list = __extract_text(doc_file_text)

        fout.write('%s\t%d\n' % (docid, len(text_span_list)))
        for sp in text_span_list:
            cur_text = doc_file_text[sp[0]:sp[1]]
            num_lines = cur_text.count('\n') + 1
            fout.write('%d\t%d\t%d\n%s\n' % (num_lines, sp[0] - len(doc_head), sp[1] - len(doc_head) - 1,
                                             cur_text.encode('utf-8')))
            # fout.write('%d\t%s\t%d\t%d\n%s\n' % (num_lines, docid,
            #                                      sp[0] - len(doc_head), sp[1] - len(doc_head) - 1,
            #                                      cur_text.encode('utf-8')))
        # break
    fin_paths.close()
    fout.close()


def __in_text_process(prev_text_file, dst_text_file, keep_web_addr=True, split_by_doc=True):
    f = open(prev_text_file, 'r')
    fout = open(dst_text_file, 'wb')

    while True:
        docid, texts, spans = next_doc_text_blocks(f)
        if not docid:
            break

        print docid
        if split_by_doc:
            fout.write('%s\t%d\n' % (docid, len(texts)))

        for cur_text, span in izip(texts, spans):
            cur_text = cur_text.replace('&lt;', '<')
            cur_text = cur_text.replace('&gt;', '> ')
            soup = BeautifulSoup(cur_text, 'html.parser')
            cur_text = soup.get_text()
            if not keep_web_addr:
                cur_text = re.sub('https?://\S*', ' ', cur_text)

            new_num_lines = cur_text.count('\n') + 1
            if split_by_doc:
                fout.write('%d\n%s\n' % (new_num_lines, cur_text.encode('utf-8')))
            else:
                fout.write('%d\t%s\t\n%s\n' % (new_num_lines, docid, cur_text.encode('utf-8')))
    f.close()
    fout.close()


def main():
    dataset = 75
    datadir = '/home/dhl/data/EDL/'

    if dataset == 75:
        doc_list_file = datadir + 'LDC2015E75/data/eng-docs-list.txt'
        dst_text_file0 = datadir + 'LDC2015E75/data/doc-text.txt'
        dst_text_file1 = datadir + 'LDC2015E75/data/doc-text-pd.txt'
    else:
        doc_list_file = datadir + 'LDC2015E103/data/eng-docs-list.txt'
        dst_text_file0 = datadir + 'LDC2015E103/data/doc-text.txt'
        dst_text_file1 = datadir + 'LDC2015E103/data/doc-text-pd.txt'

    # __extract_text_from_docs(doc_list_file, dst_text_file0)
    __in_text_process(dst_text_file0, dst_text_file1, False, True)

if __name__ == '__main__':
    main()
