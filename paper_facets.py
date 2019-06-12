#coding:utf-8

'''
    Tasks in this script:

        1. paper facets
        2. id subject general_subject
        3. save cascade seperately

'''
from basic_config import *

## data/_ids_subjects.json中subject归为大类

def _ids_2_top_subject():

    ## 所有id对应的id列表
    logging.info('loading _ids_subjects from data/_ids_subjects.json ....')
    _ids_subjects = json.loads(open('data/_ids_subjects.json').read())

    total_paper_num = len(_ids_subjects.keys())
    logging.info('%d papers with subjects loaded.' % total_paper_num)

    ##加载所有论文的subject对应的最高级的subject
    logging.info('loading mapping relations to top subject ...')
    top_subject = None
    subject_2_top = {}

    for line in open('subjects.txt'):

        line = line.strip()

        if line=='' or line is None:
            continue

        if line.startswith('====='):

            top_subject = line[5:]
        else:
            subject_2_top[line.lower()] = top_subject

            if ',' in line.lower():

                for subj in line.split(','):

                    subject_2_top[subj.lower()] = top_subject
            if '&' in line.lower():

                subject_2_top[line.replace('&','')] = top_subject

    logging.info('%d subjects are loaded ..' % len(subject_2_top.keys()))

    ## 所有论文的顶级subject
    logging.info('paper top subjs ....')
    nums_top_subjs  = []
    _ids_top_subjs = {}
    progress = 0
    error_subjs = []

    topsubj_num = defaultdict(int)
    for _id in _ids_subjects.keys():

        progress+=1

        if progress%1000000==0:

            logging.info('progress %d/%d ...' %(progress,total_paper_num))

        top_subjs = []
        for subj in _ids_subjects[_id]:

            top_subj = subject_2_top.get(subj.strip().lower(),None)

            if top_subj is None:
                error_subjs.append(subj)
                logging.info('error subj %s' % subj)
            else:
                top_subjs.append(top_subj)

                topsubj_num[top_subj]+=1


        top_subjs = list(set(top_subjs))

        nums_top_subjs.append(len(top_subjs))

        _ids_top_subjs[_id] = top_subjs
    open('data/missing_subjects.txt','w').write('\n'.join(list(set(error_subjs))))

    open('data/_ids_top_subjects.json','w').write(json.dumps(_ids_top_subjs))
    logging.info('_ids_top_subjects.json saved')

    logging.info(Counter(nums_top_subjs))

    ## 顶级领域的文章数量
    plt.figure(figsize=(5,6))
    xs = []
    ys = []

    for subject in sorted(topsubj_num.keys()):
        xs.append(subject)
        ys.append(topsubj_num[subject])

    plt.bar(np.arange(len(xs)),ys,width=0.8)

    plt.xticks(np.arange(len(xs)),xs,rotation=60)

    plt.xlabel('filed')

    plt.ylabel('number of papers')

    plt.yscale('log')

    plt.tight_layout()

    plt.savefig('fig/top_subject_num_dis.png',dpi=400)


def _id_2_citation_classification(pathObj):

    ##统计每篇论文被引的次数
    cn_dis = defaultdict(int)
    _id_cn = {}

    progress = 0

    for line in open(pathObj.cascade_path):

        line = line.strip()

        progress+=1

        if progress%10==0:

            logging.info('progress %d .... ' %progress)

        cascades = json.loads(line)

        for _id in cascades.keys():

            edges = cascades[_id]
            cn = 0
            for cpid,pid in edges:

                if pid==_id:
                    cn+=1

            _id_cn[_id] = cn

            cn_dis[pid]+=1

    open('data/_citation_dis.json','w').write(json.dumps(cn_dis))
    logging.info('data saved to data/_citation_dis.json.')
    ##
    plot_citation_dis()

    open('data/_id_cn.json','w').write(json.dumps(_id_cn))
    logging.info('%d papers cn saved to data/_id_cn.json.'% len(_id_cn.keys()))


def plot_citation_dis():

    num_dis = json.loads(open('data/_citation_dis.json').read())

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

    plt.savefig('fig/_citation_dis.png',dpi=400)

def fecth_pubyear_of_com_ids(pathObj):
    com_ids_year = {}
    ## query database wos_summary
    query_op = dbop()
    sql = 'select id,pubyear from wos_core.wos_summary'
    progress=0
    for pid,pubyear in query_op.query_database(sql):
        progress+=1
        if progress%1000000==0:
            logging.info('progress {:} ...'.format(progress))

        com_ids_year[pid] = pubyear

    query_op.close_db()
    logging.info('{:} cited ids have year'.format(len(com_ids_year.keys())))

    saved_path = pathObj.paper_year_path
    open(saved_path,'w').write(json.dumps(com_ids_year))


def fecth_doctype_of_com_ids(pathObj):
    com_ids_doctype = {}
    ## query database wos_summary
    query_op = dbop()
    sql = 'select id,doctype from wos_core.wos_doctypes'
    progress=0
    for pid,doctype in query_op.query_database(sql):
        progress+=1
        if progress%1000000==0:
            logging.info('progress {:} ...'.format(progress))

        com_ids_doctype[pid] = doctype

    query_op.close_db()
    logging.info('{:} cited ids have year'.format(len(com_ids_doctype.keys())))

    saved_path = pathObj.paper_doctype_path
    open(saved_path,'w').write(json.dumps(com_ids_doctype))


def doctype_dis(pathObj):

    _id_doctype = json.loads(open(pathObj.paper_doctype_path))

    doctype_counter = Counter(_id_doctype.values())

    xs = []
    ys = []
    for doctype in sorted(doctype_counter.keys(),key=lambda x:doctype_counter[x],reverse=True)[:10]:
        xs.append(doctype)
        ys.append(doctype_counter[doctype])


    plt.figure(figsize=(4,3.5))

    plt.bar(range(len(xs)),ys)

    plt.xticks(range(len(xs)),xs)

    plt.xlabel('doctype')

    plt.ylabel('number of papers')

    plt.tight_layout()

    plt.savefig('fig/doctype_dis.png',dpi=400)

def pubyear_dis(pathObj):

    _id_pubyear = json.loads(open(pathObj.paper_year_path))

    pubyear_counter = Counter(_id_pubyear.values())

    xs = []
    ys = []
    for pubyear in sorted(pubyear_counter.keys(),key=lambda x:pubyear_counter[x],reverse=True)[:10]:
        xs.append(pubyear)
        ys.append(pubyear_counter[pubyear])


    plt.figure(figsize=(4,3.5))

    plt.bar(range(len(xs)),ys)

    plt.xticks(range(len(xs)),xs)

    plt.xlabel('published year')

    plt.ylabel('number of papers')

    plt.tight_layout()

    plt.savefig('fig/pubyear_dis.png',dpi=400)



if __name__ == '__main__':

    ## 为每个id统计top_subj
    # _ids_2_top_subject()

    field = 'ALL'
    paths = PATHS(field)

    ### 所有论文的引用次数
    # _id_2_citation_classification(paths)

    ### 所有论文的发表年份以及所有论文的type
    # fecth_pubyear_of_com_ids(paths)
    # fecth_doctype_of_com_ids(paths)

    ## 年份以及发表年份的分布

    doctype_dis(paths)
    pubyear_dis(paths)

























