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

            top_subject = line[6:]
        else:
            subject_2_top[line.lower()] = top_subject

            if ',' in line.lower():

                for subj in line.split(','):

                    subject_2_top[subj.lower()] = top_subject

    logging.info('%d subjects are loaded ..' % len(subject_2_top.keys()))

    ## 所有论文的顶级subject
    logging.info('paper top subjs ....')
    nums_top_subjs  = []
    _ids_top_subjs = {}
    progress = 0
    for _id in _ids_subjects.keys():

        progress+=1

        if progress%1000000==0:

            logging.info('progress %d/%d ...' %(progress,total_paper_num))

        top_subjs = []
        for subj in _ids_subjects[_id]:

            top_subj = subject_2_top[subj.strip().lower()]

            top_subjs.append(top_subj)

        top_subjs = list(set(top_subjs))

        nums_top_subjs.append(len(top_subjs))

        _ids_top_subjs[_id] = top_subjs

    open('data/_ids_top_subjects.json','w').write(json.dumps(_ids_top_subjs))
    logging.info('_ids_top_subjects.json saved')

    loging.info(Counter(nums_top_subjs))


def _id_2_citation_classification(pathObj):

    ##统计
    citation_num_dis = defaultdict(int)
    _id_cn = {}
    for line in open(pathObj.cascade_path):

        line = line.strip()

        progress+=1

        if progress%10==0:

            logging.info('progress %d .... ' %progress)

        cascades = json.loads(line)

        for _id in cascades.keys():

            edges = cascades
            cn = 0
            for cpid,pid in edges:

                if pid==_id:
                    cn+=1

            _id_cn[_id] = cn

            citation_num_dis[cn]+=1

    open('data/_citation_dis.json','w').write(json.dumps(citation_num_dis))
    logging.info('data saved to data/_citation_dis.json.')
    ##

    open('data/_id_cn.json','w').write(json.dumps(_id_cn))
    logging.info('%d papers cn saved to data/_id_cn.json.'% len(_id_cn.keys()))

if __name__ == '__main__':

    ## 为每个id统计top_subj
    _ids_2_top_subject()

    field = 'ALL'

    paths = PATHS(field)































