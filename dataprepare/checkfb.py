import gzip


def __get_mid_name():
    datadir = 'e:/data/edl'
    fb_name_file = '%s/tmpres/freebase/fb-en-names.txt' % datadir
    kbid = '026zr13'

    beg_str = '%s\t' % kbid
    # fin = gzip.open(fb_name_file)
    fin = open(fb_name_file, 'rb')
    for i, line in enumerate(fin):
        if line.startswith(beg_str):
            print line,
            # break

        if (i + 1) % 10000000 == 0:
            print i + 1

    fin.close()


def __find_entity_types():
    mid_types_file = 'e:/data/edl/res/freebase/mid-fb-type.gz'
    # mid = '010013p2'
    mids = ['0_6t_z8']
    f = gzip.open(mid_types_file, 'r')
    for i, line in enumerate(f):
        tab_pos = line.find('\t')
        if line[:tab_pos] in mids:
            print line,
        if (i + 1) % 10000000 == 0:
            print i + 1
    f.close()


def __find_text():
    fbfile = 'e:/common-res/freebase-rdf-latest.gz'
    text_val = 'http://rdf.freebase.com/ns/m.026m5c8'
    f = gzip.open(fbfile, 'rb')
    for line in f:
        if text_val in line:
            print line,
    f.close()


def main():
    # __find_text()
    __get_mid_name()
    # __find_entity_types()
    pass

if __name__ == '__main__':
    main()
