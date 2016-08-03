import os

def __merge_mentions(mention_file_list, dst_result_file):
    mention_spans_docs = dict()
    fout = open(dst_result_file, 'wb')
    mention_id = 1
    for mention_file in mention_file_list:
        fin = open(mention_file, 'r')
        for line in fin:
            vals = line[:-1].split('\t')
            # print vals
            mention_span = (int(vals[2]), int(vals[3]))

            docid = vals[1]
            mention_spans = mention_spans_docs.get(docid, set())
            if not mention_spans:
                mention_spans_docs[docid] = mention_spans

            if mention_span in mention_spans:
                continue

            mention_spans.add(mention_span)
            fout.write('%s\t%s_%07d\t%s\t%s:%s-%s\t%s\t%s\t%s\t1.0\n' % ('ZJU', 'EDL15', mention_id, vals[0],
                                                                         vals[1], vals[2], vals[3], 'NIL',
                                                                         vals[4], vals[5]))
            mention_id += 1
        fin.close()

    fout.close()


def main():
    # dataset = 'LDC2015E75'
    dataset = 'LDC2015E103'
    # dataset = 'LDC2016E63'

    datadir = '/home/dhl/data/EDL/'

    ner_mentions_file = os.path.join(datadir, dataset, 'output/ner-mentions.txt')
    name_dict_mentions_file = os.path.join(datadir, dataset, 'output/name-dict-mentions.txt')
    post_author_file = os.path.join(datadir, dataset, 'output/post-authors.txt')
    extra_mentions_file = os.path.join(datadir, dataset, 'output/ner-expanded.txt')
    nom_mentions_file = os.path.join(datadir, dataset, 'output/nom-mentions.txt')
    all_mentions_tac_edl_file = os.path.join(datadir, dataset, 'output/all-mentions-tac.tab')
    all_mentions_tac_edl_file = os.path.join(datadir, dataset, 'output/nom-mentions.tab')

    # __merge_mentions([dst_ner_tac_edl_file0, dst_ner_tac_edl_file1, post_author_file], all_mentions_tac_edl_file)
    # __merge_mentions([dst_ner_tac_edl_file0, dst_ner_tac_edl_file1, post_author_file,
    #                   name_dict_mentions_file], all_mentions_tac_edl_file)
    __merge_mentions([nom_mentions_file], all_mentions_tac_edl_file)
    # __merge_mentions([name_dict_mentions_file, ner_mentions_file, post_author_file,
    #                   extra_mentions_file], all_mentions_tac_edl_file)
    # __merge_mentions([name_dict_mentions_file, nom_mentions_file, ner_mentions_file, post_author_file,
    #                   extra_mentions_file], all_mentions_tac_edl_file)

if __name__ == '__main__':
    main()
