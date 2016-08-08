import gzip


def __find_entity_types():
    mid_types_file = 'e:/data/edl/res/freebase/mid-fb-type.gz'
    mid = '0dg3n1'
    f = gzip.open(mid_types_file, 'r')
    for i, line in enumerate(f):
        tab_pos = line.find('\t')
        if mid == line[:tab_pos]:
            print line,
        if (i + 1) % 1000000 == 0:
            print i + 1
    f.close()


def main():
    __find_entity_types()

if __name__ == '__main__':
    main()
