import gzip


def __get_mid_name():
    fb_name_file = '/media/dhl/Data/data/el/tmpres/freebase/full_freebase_name_en.txt'
    dst_id = '09b6zr'

    dst_beg = dst_id + '\t'
    fin = open(fb_name_file)
    for i, line in enumerate(fin):
        if line.startswith(dst_beg):
            print line
            break

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


def main():
    # __get_mid_name()
    __find_entity_types()

if __name__ == '__main__':
    main()
