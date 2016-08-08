

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


def main():
    __get_mid_name()
    pass

if __name__ == '__main__':
    main()
