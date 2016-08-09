from mention import Mention


def __get_mid_types_in_dataset():
    edl_file = 'e:/data/edl/LDC2015E75/data/gold-eng-mentions.tab'
    mentions = Mention.load_edl_file(edl_file)
    kbid_mentions = Mention.arrange_mentions_by_docid(mentions)
    for kbid, ms in kbid_mentions.iteritems():
        print kbid
        for m in ms:
            print '\t%s' % m.name,
        print


def main():
    __get_mid_types_in_dataset()
    pass

if __name__ == '__main__':
    main()
