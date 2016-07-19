from itertools import izip

from utils import match_raw_text
from doctext import next_doc_text_blocks


def __next_tokenized_block(fin):
    line = fin.next()
    num_sentences = int(line.rstrip())
    words_sens, tgwords_sens, tags_sens = list(), list(), list()
    for i in xrange(num_sentences):
        words, tgwords, tags = list(), list(), list()
        while True:
            line = fin.next().strip()
            if line == '':
                break
            vals = line.split('\t')
            words.append(vals[0].decode('utf-8'))
            tgwords.append(vals[1].decode('utf-8'))
            tags.append(vals[2])
        words_sens.append(words)
        tgwords_sens.append(tgwords)
        tags_sens.append(tags)
    return words_sens, tgwords_sens, tags_sens


def __get_word_positions(text, text_pos, sentences):
    all_words = list()
    for sentence in sentences:
        all_words += sentence

    word_spans = match_raw_text(text, all_words)

    i = 0
    word_positions_sentences = list()
    for sentence in sentences:
        cur_word_positions = list()
        word_positions_sentences.append(cur_word_positions)
        for word in sentence:
            cur_word_positions.append((word_spans[i][0] + text_pos, word_spans[i][1] + text_pos))
            i += 1
    return word_positions_sentences


def __write_tokenized_sentences(words_sens, tgwords_sens, tags_sens, word_positions_sentences, fout):
    for words, tgwords, tags, word_positions in izip(words_sens, tgwords_sens, tags_sens, word_positions_sentences):
        for word, tgword, tag, word_pos in izip(words, tgwords, tags, word_positions):
            fout.write('%s\t%s\t%s\t%d\t%d\n' % (word.encode('utf-8'), tgword.encode('utf-8'),
                                                 tag, word_pos[0], word_pos[1] - 1))
        fout.write('\n')


def find_word_pos(text_file, words_file, dst_file):
    f_text = open(text_file, 'r')
    f_words = open(words_file, 'r')
    fout = open(dst_file, 'wb')
    while True:
        docid, texts, spans = next_doc_text_blocks(f_text)
        if not docid:
            break

        line = f_words.next()
        vals = line.rstrip().split('\t')
        num_blocks = int(vals[1])

        assert num_blocks == len(texts)
        assert docid == vals[0]

        all_words_sens, all_tgwords_sens, all_tags_sens = list(), list(), list()
        all_words_pos_sens = list()
        for i in xrange(num_blocks):
            words_sens, tgwords_sens, tags_sens = __next_tokenized_block(f_words)
            word_positions_sentences = __get_word_positions(texts[i], spans[i][0], words_sens)

            all_words_sens += words_sens
            all_tgwords_sens += tgwords_sens
            all_tags_sens += tags_sens
            all_words_pos_sens += word_positions_sentences

        fout.write('%s\t%d\n' % (docid, len(all_words_sens)))
        __write_tokenized_sentences(all_words_sens, all_tgwords_sens, all_tags_sens, all_words_pos_sens, fout)
        # break

    f_text.close()
    f_words.close()
    fout.close()


def main():
    dataset = 103
    if dataset == 75:
        text_file = 'e:/el/LDC2015E75/data/doc-text.txt'
        words_file = 'e:/el/LDC2015E75/data/doc-text-words-sen.txt'
        dst_file = 'e:/el/LDC2015E75/data/doc-text-words-pos.txt'
    else:
        text_file = 'e:/el/LDC2015E103/data/doc-text.txt'
        words_file = 'e:/el/LDC2015E103/data/doc-text-words-sen.txt'
        dst_file = 'e:/el/LDC2015E103/data/doc-text-words-pos.txt'

    find_word_pos(text_file, words_file, dst_file)

if __name__ == '__main__':
    main()
