import gzip
import os

num_lines_fb = 3130753066


class FbToTacTypeMap:
    def __init__(self, fb_to_tac_type_file):
        self.fb_types_list = list()
        self.tac_type_list = list()
        fin = open(fb_to_tac_type_file, 'r')
        for line in fin:
            tac_type = line.rstrip()
            self.tac_type_list.append(tac_type)

            line = fin.next()
            cur_fb_types = line.rstrip().split()
            self.fb_types_list.append(cur_fb_types)
        fin.close()

    def get_tac_type(self, cur_entity_fb_types):
        for i, fb_types in enumerate(self.fb_types_list):
            for ft in fb_types:
                if ft in cur_entity_fb_types:
                    return self.tac_type_list[i]
        return 'UNKNOW'


filter_types = ['music.single', 'music.recording', 'base.type_ontology.animate',
                'base.type_ontology.agent', 'base.type_ontology.inanimate',
                'music.release_track', 'common.topic', 'base.type_ontology.non_agent',
                'base.type_ontology.abstract', 'music.track_contribution']


# hand crafted mid to type
def __load_hf_mid_types(hf_mid_type_file):
    mid_type_dict = dict()
    f = open(hf_mid_type_file, 'r')
    for line in f:
        vals = line.rstrip().split('\t')
        mid_type_dict[vals[0]] = vals[1]
    f.close()
    return mid_type_dict


def __gen_fb_types_file(triples_file, dst_type_file):
    f = gzip.open(triples_file, 'rb')
    fout = open(dst_type_file, 'wb')
    cnt = 0
    for i, line in enumerate(f):
        if '\t<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>\t' in line:
            fout.write(line)
            # print line,
            cnt += 1
            # if cnt == 1000000:
            #     break
        if (i + 1) % 10000000 == 0:
            print (i + 1), float(i + 1) / num_lines_fb
    f.close()
    fout.close()


def __gen_mid_types_file(all_types_file, dst_mid_type_file):
    type_head = '<http://rdf.freebase.com/ns/'
    mid_head = '<http://rdf.freebase.com/ns/m.'
    mid_head_len = len(mid_head)
    type_head_len = len(type_head)

    f = open(all_types_file, 'rb')
    fout = open(dst_mid_type_file, 'wb')
    cnt = 0
    for i, line in enumerate(f):
        line = line[:-1]
        # print line[:-3]
        # break
        hit = False
        for ft in filter_types:
            if line[:-3].endswith(ft):
                # print line
                hit = True
                break

        if hit:
            continue

        if line.startswith(mid_head):
            vals = line.split('\t')
            fout.write('%s\t%s\n' % (vals[0][mid_head_len:-1], vals[2][type_head_len:-1]))
            cnt += 1
            # if cnt % 10000 == 0:
            #     break
        if (i + 1) % 1000000 == 0:
            print i + 1
    f.close()
    fout.close()


def filter_fb():
    triples_file = 'e:/common-res/freebase-rdf-latest.gz'
    all_type_file = 'e:/el/res/freebase/fb-type.txt'
    mid_file = 'e:/el/res/freebase/mid-fb-type.txt'

    # __gen_fb_types_file(triples_file, all_type_file)
    __gen_mid_types_file(all_type_file, mid_file)


def sort_predicates():
    count_predicates_file = 'e:/el/res/freebase/predicates-count.txt'
    sort_predicates_file = 'e:/el/res/freebase/predicates-count-sort.txt'
    pcnts = list()
    f = open(count_predicates_file, 'r')
    for line in f:
        vals = line.split('\t')
        pcnts.append((vals[0], int(vals[1])))
    f.close()

    pcnts.sort(key=lambda x: -x[1])

    fout = open(sort_predicates_file, 'wb')
    for p, cnt in pcnts:
        fout.write('%s\t%d\n' % (p, cnt))
    fout.close()


def count_predicates():
    predicates_file = 'e:/el/res/freebase/predicates-filter.txt'
    triples_file = 'e:/common-res/freebase-rdf-latest.gz'
    count_predicates_file = 'e:/el/res/freebase/predicates-count.txt'
    predicates = dict()
    f = open(predicates_file, 'r')
    for line in f:
        predicates[line[:-1]] = 0
    f.close()

    f = gzip.open(triples_file, 'rb')
    cnt = 0
    for cnt, line in enumerate(f):
        vals = line[:-1].split('\t')
        if vals[1] in predicates:
            # print vals[1]
            predicates[vals[1]] += 1
        if (cnt + 1) % 1000000 == 0:
            print cnt + 1
        # if cnt == 100:
        #     break
    f.close()
    print cnt + 1, 'lines'

    fout = open(count_predicates_file, 'wb')
    for p, v in predicates.iteritems():
        fout.write('%s\t%d\n' % (p, v))
    fout.close()


def predicates_insight():
    triples_file = 'e:/common-res/freebase-rdf-latest.gz'
    result_file = 'e:/el/res/freebase/insight.txt'
    dst_str = '<http://rdf.freebase.com/key/user.'
    f = gzip.open(triples_file, 'rb')
    fout = open(result_file, 'wb')
    val_cnt = 0
    for line in f:
        if dst_str in line:
            # print line[:-1]
            fout.write(line)
            val_cnt += 1
            if val_cnt == 100000:
                break
            if (val_cnt + 1) % 1000 == 0:
                print val_cnt + 1
    f.close()
    fout.close()


def fliter_predicates():
    predicate_file = 'e:/el/res/freebase/predicates.txt'
    nonisbn_predicate_file = 'e:/el/res/freebase/predicates-filter.txt'
    cnt = 0
    fin = open(predicate_file, 'rb')
    fout = open(nonisbn_predicate_file, 'wb')
    for line in fin:
        if 'isbn' in line or 'key/user' in line:
            continue
        cnt += 1
        fout.write(line)
    fin.close()
    fout.close()

    print cnt


def __gen_predicates():
    predicate_set = set()
    triples_file = 'e:/common-res/freebase-rdf-latest.gz'
    dst_file = 'e:/el/res/freebase/predicates.txt'
    f = gzip.open(triples_file, 'rb')
    cnt = 0
    for cnt, line in enumerate(f):
        vals = line[:-1].split('\t')
        predicate_set.add(vals[1])
        # print vals

        if (cnt + 1) % 1000000 == 0:
            print cnt + 1, len(predicate_set)

        # if i < 100:
        #     print vals[1]

        # if cnt == 500000:
        #     break
    f.close()

    print cnt, 'lines'
    print len(predicate_set)
    fout = open(dst_file, 'wb')
    for predicate in predicate_set:
        fout.write('%s\n' % predicate)
    fout.close()
    # print predicate_set


def __fb_types_to_tac_types():
    datadir = 'e:/data/edl'
    fb_to_tac_type_file = os.path.join(datadir, 'res/fb-types-to-tac-types.txt')
    mid_fb_type_file = os.path.join(datadir, 'res/freebase/mid-fb-type.gz')
    hf_mid_type_file = os.path.join(datadir, 'res/handcraft/mid-type.txt')
    dst_mid_entity_type_file = os.path.join(datadir, 'res/freebase/mid-entity-type.txt')

    hf_mid_type_dict = __load_hf_mid_types(hf_mid_type_file)
    type_map = FbToTacTypeMap(fb_to_tac_type_file)

    fin = gzip.open(mid_fb_type_file, 'r')
    fout = open(dst_mid_entity_type_file, 'wb')
    pre_kbid = ''
    fb_types = list()
    for i, line in enumerate(fin):
        vals = line.rstrip().split('\t')
        if pre_kbid and pre_kbid != vals[0]:
            cur_tac_type = hf_mid_type_dict.get(pre_kbid, '')
            if cur_tac_type:
                fout.write('%s\t%s\n' % (pre_kbid, cur_tac_type))
            else:
                cur_tac_type = type_map.get_tac_type(fb_types)
                if cur_tac_type != 'UNKNOW':
                    fout.write('%s\t%s\n' % (pre_kbid, cur_tac_type))
            fb_types = list()

        pre_kbid = vals[0]
        fb_types.append(vals[1])

        if (i + 1) % 10000000 == 0:
            print i + 1
        # if i == 10000:
        #     break

    cur_tac_type = type_map.get_tac_type(fb_types)
    if cur_tac_type != 'UNKNOW':
        fout.write('%s\t%s\n' % (pre_kbid, cur_tac_type))

    fin.close()
    fout.close()


def __filter_fb_names():
    datadir = 'e:/data/edl'
    fb_name_file = '%s/tmpres/freebase/freebase-names-all.gz' % datadir
    dst_file = '%s/tmpres/freebase/freebase-names.txt' % datadir

    mid_head = '<http://rdf.freebase.com/ns/m.'

    f = gzip.open(fb_name_file, 'r')
    fout = open(dst_file, 'wb')
    for i, line in enumerate(f):
        if line.startswith(mid_head):
            vals = line.split('\t')
            fout.write('%s\t%s\n' % (vals[0][len(mid_head):-1], vals[2]))
            # break
        if (i + 1) % 10000000 == 0:
            print i + 1
    f.close()
    fout.close()


def __gen_fb_en_names():
    datadir = 'e:/data/edl'
    fb_names_file = '%s/tmpres/freebase/freebase-names.gz' % datadir
    dst_file = '%s/tmpres/freebase/fb-en-names.txt' % datadir

    fin = gzip.open(fb_names_file, 'r')
    fout = open(dst_file, 'wb')
    for i, line in enumerate(fin):
        if line.endswith('@en\n'):
            vals = line[:-1].split('\t')
            name = vals[1][1:-4].lower()
            assert '\t' not in name
            fout.write('%s\t%s\n' % (vals[0], name))
            # break
        if (i + 1) % 10000000 == 0:
            print i + 1
    fin.close()
    fout.close()


def main():
    # count_predicates()
    # sort_predicates()
    # filter_fb()
    # __gen_predicates()
    # fliter_predicates()
    # predicates_insight()

    # __filter_fb_names()
    # __gen_fb_en_names()

    # __fb_types_to_tac_types()
    pass

if __name__ == '__main__':
    main()
