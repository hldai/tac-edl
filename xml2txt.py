#!/bin/env python
#-*- coding: utf-8 -*-

import sys
import os
import re
import cPickle as pk
from xml.dom.minidom import parse
from xml.parsers.expat import ExpatError

Folder = [
        'folder1', 'folder2', 'folder3', 'folder4', 'folder5',
        'folder6', 'folder7', 'folder8', 'folder9', 'folder10'
        ]

def parseNode(root):
    rtn = ''
    for node in root.childNodes:
        val = node.nodeValue
        if val != None:
            rtn += val
        rtn += parseNode(node)
    return rtn

def filterXML(txt):
    letter_rm = pk.load(open('script/letter_rm.pk', 'r'))
    letter_sp = pk.load(open('script/letter_sp.pk', 'r'))
    special_tag = '\n'

    # find <docid>, <doctype>, <datatime>
    txt = re.sub(r'(<docid.*?>.*?</docid>)|(<doctype.*?>.*?</doctype>)|(<datetime.*?>.*?</datetime>)|<dateline.*?>.*?</dateline>', special_tag, txt, flags = re.I)

    ner = []
    # find <post author="">
    pos = 0
    tmp = txt
    post = re.search(r'(<post author=")(.+?)(" .+?>)', tmp, re.M|re.I)
    while post:
        mention = post.group(2)
        beg = pos + post.start() + len(post.group(1))
        end = pos + post.start() + len(post.group(1)) + len(mention) - 1
        if not re.search(r'\d', mention):
            ner.append({'name':mention, 
                   'beg':beg,
                   'end':end})
        #print mention, beg, end
        tmp = tmp[post.end():]
        pos += post.end()
        post = re.search(r'(<post author=")(.+?)(" .+?>)', tmp, re.M|re.I)

    pos = 0
    tmp = txt
    post = re.search(r'(<post id=".+?" author=")(.+?)" .*?>', tmp, re.M|re.I)
    while post:
        mention = post.group(2)
        beg = pos + post.start() + len(post.group(1))
        end = pos + post.start() + len(post.group(1)) + len(mention) - 1
        if not re.search(r'\d', mention):
            ner.append({'name':mention, 
                   'beg':beg,
                   'end':end})
        #print mention, beg, end
        tmp = tmp[post.end():]
        pos += post.end()
        post = re.search(r'(<post id=".+?" author=")(.+?)" .*?>', tmp, re.M|re.I)

    txt = re.sub(r'<quote orig_author=".*?">.*?</quote>', '', txt, flags=re.DOTALL)

    txt = re.sub(r'<.+?>', special_tag, txt, flags = re.M|re.S)
    #txt = txt.replace('\n', special_tag)
    txt = re.sub(r'https?://[^ \n]*', special_tag, txt)
    # find time 2015-01-01T09:35:34
    txt = re.sub(r'\d\d\d\d-\d\d-\d\d[T ]\d\d:\d\d:\d\d', special_tag, txt)
    for i in letter_rm:
        txt = txt.replace(i, ' ')
    for i in letter_sp:
        txt = re.sub(i+'+', i[-1], txt, flags = re.M|re.S)
    txt = re.sub(r'&\w{2,4};', ' ', txt)

    txt = re.sub(r' +', ' ', txt, flags = re.M|re.S)
    txt = re.sub(r'(\n )+', '\n', txt, flags = re.M|re.S)
    txt = re.sub(r'\n+', '\n', txt, flags = re.M|re.S)
    txt = txt.strip()
    
    return (txt, ner)

def parseXML(filename):
    return filterXML(open(filename, 'r').read().decode('utf-8'))
    #try:
        #dom = parse(filename)
        #txt = parseNode(dom)
        #return txt.encode('utf-8').replace('\n', '')
    #except ExpatError: 
        #return filterXML(open(filename, 'r').read().replace('\n', ''))

def main():
    dom = parse('test.xml')
    txt = parseNode(dom)
    print txt

def batch(src, dst, ner_path):
    tmp = []
    ners = []
    files = os.listdir(src)
    print 'Total', len(files)
    for i, xml in enumerate(files):
        #with open(os.path.join(dst, Folder[i%len(Folder)], xml.rstrip('.xml') + '.txt'), 'w') as f:
        with open(os.path.join(dst, xml.rstrip('.xml') + '.txt'), 'w') as f:
            txt, ner = parseXML(os.path.join(src, xml))
            txt = txt.encode('utf-8')
            for item in ner:
                item['filename'] = xml.rstrip('.xml')
            f.write(txt)
            ners.extend(ner)
            tmp.append(txt)
        print 'Finished', i 
    pk.dump(ners, open(os.path.join(ner_path, 'per_in_post.pk'), 'w'))
    print 'Post Author Saved'
    #pk.dump(tmp, open('tmp.pk', 'w'))
    
def clean_dst(folder):
    for fd in os.listdir(folder):
        for f in os.path.join(folder, fd):
            os.remove(os.path.join(folder, fd, f))

if __name__ == '__main__':
    if len(sys.argv) == 4:
        #clean_dst(sys.argv[2])
        batch(sys.argv[1], sys.argv[2], sys.argv[3])

