import os

from mention import Mention


def __merge_mentions(mention_file_list, dst_result_file):
    mention_spans_docs = dict()
    fout = open(dst_result_file, 'wb')
    mention_id = 1
    for mention_file in mention_file_list:
        mentions = Mention.load_edl_file(mention_file)
        for m in mentions:
            mention_span = (m.beg_pos, m.end_pos)
            mention_spans = mention_spans_docs.get(m.docid, set())
            if not mention_spans:
                mention_spans_docs[m.docid] = mention_spans

            if mention_span in mention_spans:
                continue

            mention_spans.add(mention_span)
            m.mention_id = 'EDL_%07d' % mention_id
            # if m.entity_type.startswith('PER'):
            #     m.entity_type = 'PER'
            m.to_edl_file(fout)

            mention_id += 1

    fout.close()


def main():
    # dataset = 'LDC2015E75'
    dataset = 'LDC2015E103'
    # dataset = 'LDC2016E63'

    ner_tag = '1'

    # datadir = '/home/dhl/data/EDL/'
    datadir = 'e:/data/edl'

    ner_mentions_file = os.path.join(datadir, dataset, 'output/ner-mentions-%s.tab' % ner_tag)
    name_dict_mentions_file = os.path.join(datadir, dataset, 'output/name-dict-mentions.tab')
    post_author_file = os.path.join(datadir, dataset, 'output/post-authors.tab')
    extra_mentions_file = os.path.join(datadir, dataset, 'output/ner-expanded-%s.tab' % ner_tag)
    nom_mentions_file = os.path.join(datadir, dataset, 'output/nom-mentions.tab')
    all_mentions_tac_edl_file = os.path.join(datadir, dataset, 'output/all-mentions-%s.tab' % ner_tag)
    # all_mentions_tac_edl_file = os.path.join(datadir, dataset, 'output/ner-mentions-m.tab')
    # all_mentions_tac_edl_file = os.path.join(datadir, dataset, 'output/nom-mentions.tab')

    # __merge_mentions([post_author_file, name_dict_mentions_file, ner_mentions_file,
    #                   extra_mentions_file], all_mentions_tac_edl_file)
    __merge_mentions([post_author_file, name_dict_mentions_file, nom_mentions_file, ner_mentions_file,
                      extra_mentions_file], all_mentions_tac_edl_file)

if __name__ == '__main__':
    main()
