import os
from itertools import izip

from mention import Mention
from nomdiscover import load_nom_dict


def __group_mentions_by_kbid(mentions):
    kbid_mentions_dict = dict()
    for m in mentions:
        cur_mentions = kbid_mentions_dict.get(m.kbid, list())
        if not cur_mentions:
            kbid_mentions_dict[m.kbid] = cur_mentions
        cur_mentions.append(m)
    return kbid_mentions_dict


def __should_merge(mentions0, mentions1):
    for m0 in mentions0:
        for m1 in mentions1:
            if m0.name == m1.name:
                return True
    return False


def __nil_clustering(nom_dict_file, edl_file, dst_file):
    nom_names = load_nom_dict(nom_dict_file)
    all_mentions = Mention.load_edl_file(edl_file)
    nil_mentions = [m for m in all_mentions if m.kbid.startswith('NIL') and m.name.lower() not in nom_names]
    kbid_mentions = __group_mentions_by_kbid(nil_mentions)

    new_kbids, new_mentions_kbids = list(), list()
    for kbid, mentions in kbid_mentions.iteritems():
        merged = False
        for nkbid, nmentions in izip(new_kbids, new_mentions_kbids):
            if __should_merge(mentions, nmentions):
                # for m in mentions:
                #     print '%s\t' % m.name,
                # print
                # for m in nmentions:
                #     print '%s\t' % m.name,
                # print '\n'

                for m in mentions:
                    m.kbid = nkbid
                    nmentions.append(m)
                merged = True
                break

        if not merged:
            new_kbids.append(kbid)
            new_mentions_kbids.append(mentions)

    Mention.save_as_edl_file(all_mentions, dst_file)


def __get_max_nil_id(mentions):
    max_id = 0
    for m in mentions:
        if m.kbid.startswith('NIL'):
            cur_id = int(m.kbid[3:])
            if cur_id > max_id:
                max_id = cur_id
    return max_id


def __link_nom(doc_mentions_dict, cur_max_nil_id):
    for docid, mentions in doc_mentions_dict.iteritems():
        mentions.sort(key=lambda x: x.beg_pos)
        for i, m, in enumerate(mentions):
            if i < len(mentions) - 1 and mentions[i + 1].entity_type == 'PER':
                m.kbid = mentions[i + 1].kbid
                continue
            if i > 0 and mentions[i - 1].entity_type == 'PER':
                m.kbid = mentions[i - 1].kbid
                continue


def __fix_types(mentions):
    for m in mentions:
        if m.entity_type.startswith('PER'):
            m.entity_type = 'PER'


def __post_process(cur_edl_file, new_edl_file):
    mentions = Mention.load_edl_file(cur_edl_file)

    # max_nil_id = __get_max_nil_id(mentions)
    # print max_nil_id
    # doc_mentions_dict = Mention.arrange_mentions_by_docid(mentions)
    # __link_nom(doc_mentions_dict, max_nil_id)
    __fix_types(mentions)
    Mention.save_as_edl_file(mentions, new_edl_file)


def main():
    # dataset = 'LDC2015E75'
    dataset = 'LDC2015E103'
    # dataset = 'LDC2016E63'

    datadir = '/home/dhl/data/EDL/'
    nom_dict_file = os.path.join(datadir, 'res/nom-dict-edit.txt')
    cur_edl_file = os.path.join(datadir, dataset, 'output/sys-link-sm.tab')
    new_edl_file = os.path.join(datadir, dataset, 'output/sys-link-sm-pp.tab')
    # __nil_clustering(nom_dict_file, edl_file, dst_file)
    __post_process(cur_edl_file, new_edl_file)

if __name__ == '__main__':
    main()
