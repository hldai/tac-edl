import gzip


def find_text(fbfile, text_val):
    f = gzip.open(fbfile, 'rb')
    for line in f:
        if text_val in line:
            print line,
    f.close()


def main():
    fbfile = 'e:/common-res/freebase-rdf-latest.gz'
    # text_val = 'Dilma Rousseff'
    text_val = 'http://rdf.freebase.com/ns/m.026m5c8'
    find_text(fbfile, text_val)

if __name__ == '__main__':
    main()
