import os
from itertools import izip

from mention import Mention
from nomdiscover import load_nom_dict
from utils import load_doc_paths, doc_id_from_path, read_text


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


def __load_mid_to_type_file(mid_type_file):
    mid_type_dict = dict()
    f = open(mid_type_file, 'r')
    for line in f:
        vals = line[:-1].split('\t')
        mid_type_dict[vals[0]] = vals[1]
    f.close()
    return mid_type_dict


def __fix_entity_types_by_mid(mid_type_file, mentions):
    mid_type_dict = __load_mid_to_type_file(mid_type_file)

    # hitcnt, cnt = 0, 0
    for m in mentions:
        if m.kbid.startswith('m.'):
            sys_type = mid_type_dict.get(m.kbid[2:], '')
            if sys_type:
                # print sys_type
                m.entity_type = sys_type


def __is_normal_name(author_name):
    for ch in author_name:
        if ch != '?':
            return True
    return False


def __nil_author_clustering(mentions):
    author_mentions_dict = dict()
    for m in mentions:
        if m.entity_type == 'PER-PA':
            cur_author_mentions = author_mentions_dict.get(m.name, list())
            if not cur_author_mentions:
                author_mentions_dict[m.name] = cur_author_mentions
            cur_author_mentions.append(m)

    for author_name, author_mentions in author_mentions_dict.iteritems():
        # if not __is_normal_name(author_name):  # TODO test
        #     continue

        kbid = author_mentions[0].kbid
        # print author_name, kbid
        # for m in author_mentions:
        #     print m.docid,
        # print
        for m in author_mentions:
            m.kbid = kbid


def __fix_special_types(mentions):
    for m in mentions:
        if m.entity_type.startswith('PER'):
            m.entity_type = 'PER'


def __fix_type_diff_of_same_kbid(mentions):
    mention_groups = __group_mentions_by_kbid(mentions)
    for kbid, ms in mention_groups.iteritems():
        type_cnts = dict()
        for m in ms:
            cnt = type_cnts.get(m.entity_type, 0)
            type_cnts[m.entity_type] = cnt + 1
        if len(type_cnts) < 2:
            continue

        major_type = ''
        max_cnt = 0
        for t, cnt in type_cnts.iteritems():
            if cnt > max_cnt:
                max_cnt = cnt
                major_type = t
        for m in ms:
            m.entity_type = major_type


def __validate_mentions(doc_list_file, mentions, dst_miss_match_file):
    print 'checking miss match'
    doc_mentions = Mention.arrange_mentions_by_docid(mentions)
    doc_paths = load_doc_paths(doc_list_file)
    doc_head = '<?xml version="1.0" encoding="utf-8"?>\n'
    miss_match_cnt = 0
    fout = open(dst_miss_match_file, 'wb')
    for doc_path in doc_paths:
        docid = doc_id_from_path(doc_path)
        cur_doc_mentions = doc_mentions.get(docid, list())
        if not cur_doc_mentions:
            continue

        doc_text = read_text(doc_path, True)
        if doc_text.startswith(doc_head):
            doc_text = doc_text[len(doc_head):]

        for m in cur_doc_mentions:
            name_in_doc = doc_text[m.beg_pos:m.end_pos + 1]
            if name_in_doc != m.name:
                miss_match_cnt += 1
                fout.write('%s\t%s\t%d\t%d\t%s\n' % (docid, m.name.encode('utf-8'), m.beg_pos, m.end_pos,
                                                     name_in_doc.encode('utf-8')))
                # print '%s\t%s\t%d\t%d\t%s' % (docid, m.name, m.beg_pos, m.end_pos, name_in_doc)
    fout.close()
    print miss_match_cnt, 'miss match'


def __fix_pos_error(mentions):
    cnt = 0
    for i in xrange(len(mentions) - 1, -1, -1):
        if mentions[i].beg_pos > mentions[i].end_pos:
            cnt += 1
            del mentions[i]
    print '%d pos errors' % cnt


def main():
    # dataset = 'LDC2015E75'
    dataset = 'LDC2015E103'
    # dataset = 'LDC2016E63'
    mentions_tag = '0'
    run_id = 4

    # datadir = '/home/dhl/data/EDL/'
    datadir = 'e:/data/edl'

    doc_list_file = os.path.join(datadir, dataset, 'data/eng-docs-list-win.txt')
    mid_type_file = os.path.join(datadir, 'res/freebase/mid-entity-type.txt')
    cur_edl_file = os.path.join(datadir, dataset, 'output/sys-link-sm-%s.tab' % mentions_tag)
    miss_match_mentions_file = os.path.join(datadir, dataset, 'output/miss-match-mentions-%s.txt' % mentions_tag)
    new_edl_file = os.path.join(datadir, dataset, 'output/sys-link-sm-pp-ft-%d.tab' % run_id)
    # __nil_clustering(nom_dict_file, edl_file, dst_file)
    mentions = Mention.load_edl_file(cur_edl_file)

    # __link_nom(doc_mentions_dict, max_nil_id)

    __nil_author_clustering(mentions)
    __fix_special_types(mentions)
    __fix_entity_types_by_mid(mid_type_file, mentions)
    # __fix_type_diff_of_same_kbid(mentions)
    __validate_mentions(doc_list_file, mentions, miss_match_mentions_file)
    __fix_pos_error(mentions)
    Mention.save_as_edl_file(mentions, new_edl_file, runid='WednesdayGo%d' % run_id)

if __name__ == '__main__':
    main()
