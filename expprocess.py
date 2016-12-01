def process_for_eval(edl_file, gold_file, fix_type, dst_file):
    docs = set()
    f = open(gold_file, 'r')
    for line in f:
        vals = line.split('\t')
        docid = vals[3].split(':')[0]
        docs.add(docid)
    f.close()

    f = open(edl_file, 'r')
    fout = open(dst_file, 'wb')
    for line in f:
        vals = line.strip().split('\t')
        if len(vals) < 8:
            print line
            print 'something wrong'
        docid = vals[3].split(':')[0]
        if docid in docs:
            if fix_type:
                entity_type = vals[5]
                if entity_type.startswith('PER'):
                    entity_type = 'PER'
                fout.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (vals[0], vals[1], vals[2], vals[3], vals[4],
                                                                 entity_type, vals[6], vals[7]))
            else:
                fout.write(line)
            # fout.write('\n')
        # else:
        #     print line
    f.close()
    fout.close()


def main():
    fix_type = False
    edl_file = 'e:/data/edl/LDC2016E63/output/all-mentions-nnom-1.tab'
    gold_file = 'e:/data/edl/LDC2016E68/data/gold-eng-mentions.tab'
    dst_file = 'e:/data/edl/LDC2016E63/output/all-mentions-nnom-1-exp.tab'

    # edl_file = 'e:/data/edl/LDC2015E103/output/all-mentions-1.tab'
    # gold_file = 'e:/data/edl/LDC2015E103/data/gold-eng-mentions.tab'
    # dst_file = 'e:/data/edl/LDC2015E103/output/all-mentions-1-eval.tab'

    process_for_eval(edl_file, gold_file, fix_type, dst_file)

if __name__ == '__main__':
    main()
