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


def next_ner_result(fin):
    line = fin.next()
    num_lines = int(line[:-1])
    words, tags = list(), list()
    for i in xrange(num_lines):
        tmp_line = fin.next()
        tmp_vals = tmp_line[:-1].split('\t')
        words.append(tmp_vals[0].decode('utf-8'))
        tags.append(tmp_vals[1])
    return words, tags


def match_raw_text(text, words):
    pos = 0
    span_list = list()
    for w in words:
        w = w.replace('&', '&amp;')
        w = w.replace('<', '&lt;')
        w = w.replace('>', '&gt;')

        np = text.find(w, pos)
        if np > -1:
            pos = np + len(w)
        else:
            print w
            print text
            assert False
        span_list.append((np, pos))

    return span_list


def read_text(fin, num_lines):
    text = ''
    for i in xrange(num_lines):
        text += fin.next()
    return text.decode('utf-8')
