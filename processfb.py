import gzip

num_lines_fb = 3130753066


filter_types = ['music.single', 'music.recording', 'base.type_ontology.animate',
                'base.type_ontology.agent', 'base.type_ontology.inanimate',
                'music.release_track', 'common.topic', 'base.type_ontology.non_agent',
                'base.type_ontology.abstract', 'music.track_contribution']


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


def __filter_fb_types():
    keep_types = {'people.person', 'location.country', 'location.administrative_division',
                  'location.statistical_region', 'organization.organization',
                  'location.location', 'architecture.structure'}
    fin = gzip.open('e:/el/res/freebase/mid-fb-type.gz', 'r')
    fout = open('e:/el/res/freebase/mid-fb-type-filtered.txt', 'wb')
    for i, line in enumerate(fin):
        vals = line[:-1].split('\t')
        if vals[1] in keep_types:
            fout.write('%s\t%s\n' % (vals[0], vals[1]))

        if (i + 1) % 1000000 == 0:
            print i + 1
    fin.close()
    fout.close()


def __fb_types_to_entity_types():
    mid_fb_type_file = 'e:/el/res/freebase/mid-fb-type-filtered.txt'
    dst_mid_entity_type_file = 'e:/el/res/freebase/mid-entity-type.txt'

    fb_types = ['people.person', 'location.country', 'location.administrative_division',
                'location.statistical_region', 'organization.organization', 'location.location',
                'architecture.structure']
    type_idx_dict = dict()
    for i, fb_type in enumerate(fb_types):
        type_idx_dict[fb_type] = i

    fb_type_mids = [set() for _ in xrange(len(fb_types))]

    print 'loading fb types ...'
    all_mids = set()
    fin = open(mid_fb_type_file, 'r')
    for i, line in enumerate(fin):
        vals = line[:-1].split('\t')
        idx = type_idx_dict[vals[1]]
        fb_type_mids[idx].add(vals[0])
        all_mids.add(vals[0])
        # if i == 1000:
        #     break
    fin.close()

    fout = open(dst_mid_entity_type_file, 'wb')
    for mid in all_mids:
        if mid in fb_type_mids[0]:
            fout.write('%s\t%s\n' % (mid, 'PER'))
        elif mid in fb_type_mids[1] or mid in fb_type_mids[2] or mid in fb_type_mids[3]:
            fout.write('%s\t%s\n' % (mid, 'GPE'))
        elif mid in fb_type_mids[4]:
            fout.write('%s\t%s\n' % (mid, 'ORG'))
        elif mid in fb_type_mids[5]:
            fout.write('%s\t%s\n' % (mid, 'LOC'))
        elif mid in fb_type_mids[6]:
            fout.write('%s\t%s\n' % (mid, 'FAC'))
        else:
            print mid, 'not found'
    fout.close()


def main():
    # count_predicates()
    # sort_predicates()
    # filter_fb()
    # __gen_predicates()
    # fliter_predicates()
    # predicates_insight()
    __fb_types_to_entity_types()

if __name__ == '__main__':
    main()
