import codecs
import re
import cPickle as pk

beg_p = r'\d+\-'
end_p = r'\-\d+'

def nomlink(file_path, out_path):
    file = codecs.open(file_path, 'rb', encoding='utf-8')
    out_file = codecs.open(out_path, 'wb', encoding='utf-8')
    info = file.readline().strip()
    total_list = {}
    while info != '':
        info = info.split('\t')
        word = info[2]
        doc_name = info[3]
        if doc_name[:3] == "ENG":
            cur_info = {}
            cur_info['beg'] = int(re.findall(beg_p, doc_name)[0][:-1])
            cur_info['end'] = int(re.findall(end_p, doc_name)[0][1:])
            doc_name = doc_name[:32]
            if total_list.has_key(doc_name) == False:
                total_list.setdefault(doc_name,[])
            cur_info['word'] = word
            cur_info['nilno'] = info[4]
            cur_info['ner'] = info[5]
            cur_info['flag'] = info[6]
            total_list[doc_name].append(cur_info)
        info = file.readline()

    count = 1
    total_count = 0
    corr_count = 0
    for doc in total_list:
        def beg_sort(l):
            return l['beg']

        def examine(index, l):
            count_big = index + 1
            count_small = index - 1
            find_NAM = True
            while find_NAM:

                while count_small >= 0 and (l[count_small]['flag'] != 'NAM' or l[count_small]['ner'] != 'PER'):
                    count_small -= 1
                while count_big < len(l) and (l[count_big]['flag'] != 'NAM' or l[count_big]['ner'] != 'PER'):
                    count_big += 1
                if count_small < 0:
                    return count_big
                if count_big > len(l) - 1:
                    return count_small
                if (l[index]['beg'] - l[count_small]['end']) < (l[count_big]['beg'] - l[index]['end']):
                    return count_small
                else:
                    return count_big

        l = sorted(total_list[doc], key=beg_sort)

        for index, cur_info in enumerate(l):
            if cur_info['flag'] == 'NOM':
                total_count += 1
                index_s = index - 1
                index_l = index + 1
                if index_l < len(l) and l[index_l]['flag'] == 'NAM' and l[index_l]['ner'] == 'PER':
                    if cur_info['nilno'] == l[index_l]['nilno']:
                        corr_count += 1
                    cur_info['nilno'] = l[index_l]['nilno']
                elif index_s >= 0 and l[index_s]['flag'] == 'NAM' and l[index_s]['ner'] == 'PER':
                    if cur_info['nilno'] == l[index_s]['nilno']:
                        corr_count += 1
                    cur_info['nilno'] = l[index_s]['nilno']
                else:
                    cur_info['nilno'] = 'NIL10000'

                # find_nerest = examine(index, l)
                # if find_nerest < len(l):
                #     if cur_info['nilno'] == l[find_nerest]['nilno']:
                #         corr_count += 1
                #     cur_info['nilno'] = l[find_nerest]['nilno']
            entity_id = "%05d" % count
            out_file.write('LDC\tTEDL15_TRAINING_' + str(entity_id) + '\t' + cur_info['word'] + '\t' + doc
                               + ':' + str(cur_info['beg']) + '-' + str(cur_info['end']) + '\t' + cur_info['nilno'] + '\t'
                            + cur_info['ner'] + '\t' + cur_info['flag'] + '\t1.0\n')
            print ('LDC\tTEDL15_TRAINING_' + str(entity_id) + '\t' + cur_info['word'] + '\t' + doc
                   + ':' + str(cur_info['beg']) + '-' + str(cur_info['end']) + '\t' + cur_info['nilno'] + '\t'
                   + cur_info['ner'] + '\t' + cur_info['flag'] + '\t1.0')
            count += 1
            # if count == 1796:
            #     print 320
    print total_count
    print corr_count
    print ("accuracy:%.3f" % (float(corr_count) / float(total_count)))

    # print "s"

# def save_nom(file_path):
#     file = codecs.open(file_path, 'rb', encoding='utf-8')
#     save_path = 'model/nom_in_gold.pkl'
#     out_file = codecs.open(save_path, 'wb', encoding='utf-8')
#     info = file.readline().strip()
#     nom_words = []
#     while info != '':
#         info = info.split('\t')
#         word = info[2]
#         flag = info[6]
#         if flag == "NOM":
#             if word not in nom_words:
#                 out_file.write(word + '\n')
#                 # word.encode('utf-8')
#                 nom_words.append(word)
#         info = file.readline().strip()
#     # s = set(nom_words)

if __name__ == "__main__":
    file_path = '/home/dhl/data/EDL/LDC2015E103/output/sys-link-sm.tab'
    out_path = '/home/dhl/data/EDL/LDC2015E103/output/sys-link-sm-nl.tab'
    nomlink(file_path, out_path)
    # save_nom(out_path)
