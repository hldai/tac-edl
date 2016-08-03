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
        print doc_path
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
        prew = w
        movelen = len(w)
        if '&' in w or '<' in w or '>' in w:
            np0 = text.find(w, pos)

            w = w.replace('&', '&amp;')
            w = w.replace('<', '&lt;')
            w = w.replace('>', '&gt;')
            np1 = text.find(w, pos)
            if np0 < 0 and np1 < 0:
                np = -1
            else:
                if np1 > -1 and (np1 < np0 or np0 < 0):
                    np = np1
                    movelen = len(w)
                else:
                    np = np0
        else:
            np = text.find(w, pos)

        if np > -1:
            pos = np + movelen
        else:
            print w, prew
            print text
            print '----------------'
            print text[:pos]
            print text.find(w, pos)
            assert False
        span_list.append((np, pos))

    return span_list


# def read_text(fin, num_lines):
#     text = ''
#     for i in xrange(num_lines):
#         text += fin.next()
#     return text.decode('utf-8')


def read_text(filename):
    f = open(filename, 'r')
    text = f.read()
    f.close()
    return text


def find_phrases_in_words(phrases, words, allow_nest):
    hit_spans, hit_indices = list(), list()
    num_words = len(words)
    i = 0
    while i < num_words:
        for j, phrase in enumerate(phrases):
            num_words_in_phrase = len(phrase)
            if i + num_words_in_phrase > num_words:
                continue

            hit = True
            for k in xrange(num_words_in_phrase):
                if phrase[k] != words[i + k]:
                    hit = False
                    break

            if hit:
                hit_spans.append((i, i + num_words_in_phrase))
                hit_indices.append(j)
                if not allow_nest:
                    i += num_words_in_phrase - 1
                    break
        i += 1
    return hit_spans, hit_indices
