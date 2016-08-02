from mention import Mention


def __gen_ttl_dict():
    edl_file = '/home/dhl/data/EDL/LDC2015E103/data/gold-eng-mentions.tab'
    dst_file = '/home/dhl/data/EDL/LDC2015E75/data/ttl-dict.txt'
    mentions = Mention.load_edl_file(edl_file)
    for m in mentions:
        if m.entity_type == 'TTL':
            print m.name, m.entity_type, m.mention_type, m.docid


def main():
    __gen_ttl_dict()

if __name__ == '__main__':
    main()