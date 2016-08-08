class Mention:
    # arrange mentions to a dict, { docid -> mentions-in-doc }
    @staticmethod
    def arrange_mentions_by_docid(mention_list):
        doc_mentions_dict = dict()
        for m in mention_list:
            # if m.mention_type != 'NOM':
            #     continue
            mlist = doc_mentions_dict.get(m.docid, list())
            if mlist:
                mlist.append(m)
            else:
                mlist.append(m)
                doc_mentions_dict[m.docid] = mlist
        return doc_mentions_dict

    # TODO remove
    @staticmethod
    def write_mentions(mentions, dst_file):
        fout = open(dst_file, 'wb')
        for m in mentions:
            fout.write('%s\t%d\t%d\t%s\t%s\n' % (m.docid, m.beg_pos, m.end_pos, m.name.encode('utf-8'), m.entity_type))
        fout.close()

    @staticmethod
    def save_as_edl_file(mentions, dst_file, runid='ZJU'):
        fout = open(dst_file, 'wb')
        for m in mentions:
            m.to_edl_file(fout, runid)
        fout.close()

    def to_edl_file(self, fout, runid='ZJU'):
        fout.write('%s\t%s\t%s\t%s:%d-%d\t%s\t%s\t%s\t1.0\n' % (
            runid, self.mention_id, self.name.encode('utf-8'), self.docid, self.beg_pos,
            self.end_pos, self.kbid, self.entity_type, self.mention_type))

    @staticmethod
    def load_edl_file(filename, arrange_by_docid=False):
        mentions = list()
        f = open(filename, 'r')
        for line in f:
            vals = line[:-1].split('\t')
            pos_vals = vals[3].split(':')
            pos_in_doc_vals = pos_vals[1].split('-')
            m = Mention(name=vals[2].decode('utf-8'), beg_pos=int(pos_in_doc_vals[0]), end_pos=int(pos_in_doc_vals[1]),
                        docid=pos_vals[0], mention_type=vals[6], entity_type=vals[5], kbid=vals[4], mention_id=vals[1])
            mentions.append(m)
            # mentions.append((vals[1], vals[2], pos_vals[0], int(pos_in_doc_vals[0]),
            #                  int(pos_in_doc_vals[1]), vals[4], vals[5], vals[6]))
        f.close()

        if arrange_by_docid:
            return Mention.arrange_mentions_by_docid(mentions)
        return mentions

    def __init__(self, name=u'', beg_pos=-1, end_pos=-1, docid='', mention_type='',
                 entity_type='', kbid='NIL', mention_id='TEDL_000001'):
        self.mention_id = mention_id
        self.name = name
        self.beg_pos = beg_pos
        self.end_pos = end_pos
        self.docid = docid
        self.mention_type = mention_type
        self.entity_type = entity_type
        self.kbid = kbid

        # debug
        self.tags = None
