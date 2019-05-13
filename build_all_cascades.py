#coding:utf-8

'''
    Tasks in this script:

        1. build cascade by using all papers
        2. id subject general_subject
        3. save cascade seperately

'''
## task 1

from basic_config import *


def fetch_citing_relations(pathObj):

    field =pathObj.field
    logging.info('fetch citing relations ...')

    query_op = dbop()
    sql = 'select id,ref_id from wos_references'
    progress=0
    sub_progress = 0
    pid_cits = []
    saved_path = pathObj.pid_cits_path
    os.remove(saved_path) if os.path.exists(saved_path) else None
    pfile = open(saved_path,'w+')
    for pid,ref_id in query_op.query_database(sql):
        progress+=1
        if progress%10000000==0:
            logging.info('total progress {:} ...'.format(progress))
            pfile.write('\n'.join(pid_cits)+'\n')
            pid_cits = []

        pid_cits.append('{:}\t{:}'.format(ref_id,pid))

    query_op.close_db()
    pfile.write('\n'.join(pid_cits)+'\n')
    logging.info('{:} citing relations are saved to {:}'.format(progress,saved_path))

def build_cascade_from_pid_cits(pathObj):

    pid_cits_path = pathObj.pid_cits_path

    logging.info("build cascade from {:} .".format(pid_cits_path))

    _ids_subjects = json.loads(open('data/_ids_subjects.json').read())

    logging.info('_id_subjects.json loaded ....')

    pid_citations = defaultdict(list)
    progress = 0
    for line in open(pid_cits_path):

        progress+=1

        if progress%10000000==0:
            logging.info('reading citation relations....')

        line = line.strip()
        pid,citing_id = line.split("\t")

        ## 如果不是wos的论文
        if len(_ids_subjects.get(pid,[]))==0:
            continue

        pid_citations[pid].append(citing_id)

    pids = pid_citations.keys()

    pid_dis = defaultdict(int)

    length = len(pids)
    logging.info('{:} papers has citations, start to build cascade ...'.format(length))
    progress = 0
    saved_path = pathObj.cascade_path
    os.remove(saved_path) if os.path.exists(saved_path) else None

    outfile = open(saved_path,'w+')
    citation_cascade = defaultdict(list)
    total_num = 0
    for pid in pids:
        progress+=1

        if progress%100000==0:
            total_num += len(citation_cascade.keys())
            outfile.write(json.dumps(citation_cascade)+'\n')
            logging.info('Building progress {:}/{:}, {:} citation cascades saved to {:}...'.format(progress,length,total_num,saved_path))
            citation_cascade = defaultdict(list)

        citing_list = set(pid_citations.get(pid,[]))

        pid_dis[len(citing_list)]+=1

        if len(citing_list)==0:
            continue

        for cit in citing_list:

            if pid == cit:
                continue

            citation_cascade[pid].append([cit,pid])

            ## if cit has no citation
            cit_citation_list = set(pid_citations.get(cit,[]))

            if len(cit_citation_list)==0:
                continue

            for inter_pid in (citing_list & cit_citation_list):
                citation_cascade[pid].append([inter_pid,cit])

    outfile.write(json.dumps(citation_cascade)+"\n")
    logging.info("{:} citation cascade has been build, and saved to {:}".format(total_num,saved_path))

    open('data/pid_dis.json','w').write(json.dumps(pid_dis))

    ## 画引用次数分布
    plot_citation_dis()
    logging.info('citation distribtuion plot saved...')

def fecth_subjects():
    # com_IDs = set([line.strip() for line in open(com_IDs_path)])
    # logging.info('fetch published year of {:} combine ids'.format(len(com_IDs)))


    logging.info('%d unique subjects loaded ...' % len(subjects))

    _ids_subjects = defaultdict(list)
    ## query database wos_summary
    query_op = dbop()
    num_with_subject = 0
    sql = 'select id,subject from wos_subjects'
    progress=0
    for pid,subject in query_op.query_database(sql):
        progress+=1
        if progress%1000000==0:
            logging.info('progress {:}, {:} papers within subjects ...'.format(progress,num_with_subject))

        # if subject.strip().lower() in subjects:
        #     num_with_subject+=1
        _ids_subjects[pid].append(subject)

    query_op.close_db()
    logging.info('{:}  papers have subject'.format(len(_ids_subjects.keys())))
    open('data/_ids_subjects.json','w').write(json.dumps(_ids_subjects))

    # for pid in _ids_subjects:

    #     in_subjects = False
    #     for subject in _ids_subjects[pid]:

    #         if subject in subjects:
    #             in_subjects=True

    #     if in_subjects:
    #         num_with_subject+=1

    # print '{:} papers with subject in subjects.'.format(num_with_subject)

    # return com_ids_subjects

## 根据subject的论文保留cascade
def split_cascades_within_subjects(pathObj):
    # subjects = set([line.strip().lower() for line in open('subjects.txt') if not line.startswith('=====') and line.strip()!=''])
    _ids_subjects = json.loads(open('data/_ids_subjects.json').read())

    citation_cascades = {}
    outfile = open(pathObj.cascade_bak_path,'w+')
    progress=0
    total = 0
    for line in open(pathObj.cascade_path):

        line = line.strip()

        progress+=1

        if progress%10==0:
            total+= len(citation_cascades.keys())
            logging.info('{:} lines procesed, {:} cascades reserved.'.format(progress,total))
            outfile.write(json.dumps(citation_cascades)+'\n')
            citation_cascades = {}

        cascades = json.loads(line)

        for pid in cascades.keys():

            if len(_ids_subjects.get(pid,[]))>0:

                citation_cascades[pid] = cascades[pid]


    total+= len(citation_cascades.keys())
    logging.info('{:} lines procesed, {:} cascades reserved.'.format(progress,total))
    outfile.write(json.dumps(citation_cascades)+'\n')

def split_cascade_into_subject():
    _ids_subjects = json.loads(open('data/_ids_subjects.json').read())



def plot_citation_dis():

    num_dis = json.loads(open('data/pid_dis.json').read())

    xs = []
    ys = []

    for num in sorted(num_dis.keys()):

        xs.append(num)
        ys.append(num_dis[num])

    plt.figure(figsize=(5,4))

    plt.plot(xs,ys,'o',fillstyle='none')

    plt.xlabel('number of citations')
    plt.ylabel('number of publications')

    plt.xscale('log')
    plt.yscale('log')

    plt.tight_layout()

    plt.savefig('fig/citation_dis.png',dpi=400)


if __name__ == '__main__':
    ## task 1
    # if int(sys.argv[1])==0:
    #     field = 'physics'
    # else:
    field = 'ALL'

    paths = PATHS(field)

    ## task 4
    # fetch_citing_relations(paths)

    ## task 5
    build_cascade_from_pid_cits(paths)

    # task 6
    # fecth_subjects()

    # plot_citation_dis()

    # split_cascades_within_subjects(paths)

    # task 7
    # fecth_subjects_of_com_ids(paths)












