#coding:utf-8

from basic_config import *

from dccp_metrics import load_attrs


## 从各个领域中提取出10000篇高被引的论文
def top_1_percent_papers(pathObj):

    # _id_subjects,_id_cn,_id_doctype,_id_year,top10_doctypes = load_attrs(pathObj)
    logging.info('loading _id_subjects ...')
    _id_subjects = json.loads(open(pathObj.paper_id_topsubj).read())

    logging.info('loading _id_cn ...')
    _id_cn = json.loads(open(pathObj.paper_cit_num_path).read())

    ## 从各个领域选取引用次数最高的1%的论文，大部分有6000万 1%也就是60万数据
    _subj_id_cn = defaultdict(lambda:defaultdict(int))
    _subj_num = defaultdict(int)
    logging.info('stating ....')

    for _id in _id_subjects.keys():

        _subjs = _id_subjects[_id]


        if _id_cn.get(_id,None) is None:
            continue

        _cn = int(_id_cn[_id])

        for _subj in _subjs:

            _subj_id_cn[_subj][_id] = _cn

            _subj_num[_subj]+=1

    logging.info('stating top subject ...')
    ## 并保留各个
    _subj_id_dict = defaultdict(lambda:defaultdict(int))
    for _subj in _subj_id_cn.keys():

        num = int(_subj_num[_subj]/10)

        _id_cn = _subj_id_cn[_subj]

        for _id in sorted(_id_cn.keys(),key = lambda x:_id_cn[x],reverse=True)[:num]:

            # pass
            _subj_id_dict[_subj][_id] = _id_cn[_id]


    open('data/subject_id_cn_top1.json','w').write(json.dumps(_subj_id_dict))

    logging.info('data saved to data/subject_id_cn_top1.json.')


def get_top_cascade(pathObj):

    top10subjids = json.loads(open('data/subject_id_cn_top1.json').read())

    id_set = []

    for subj in top10subjids:

        _id_cn = top10subjids[subj]

        num = len(_id_cn)
        logging.info('subject {} has {} papers.'.format(subj,num))

        for _id in sorted(_id_cn.keys(),key = lambda x:_id_cn[x],reverse=True)[:num/10]:

            id_set.append(_id)

    id_set = set(id_set)

    logging.info('Number of ids is {}.'.format(len(id_set)))


    cc_path = pathObj.cascade_path
    progress = 0

    selected_cascades = {}

    for line in open(cc_path):

        line = line.strip()

        citation_cascade = json.loads(line)

        for pid in citation_cascade.keys():

            progress+=1

            if progress%1000000==0:
                logging.info('progress report {:}, selected cascades size {} ...'.format(progress,len(selected_cascades)))

            if pid in id_set:

                selected_cascades[pid] = citation_cascade[pid]

    open('data/selected_high_cascades.json','w').write(selected_cascades)

    logging.info('data saved to data/selected_high_cascades.json')



if __name__ == '__main__':
    field = 'ALL'
    paths = PATHS(field)

    # top_1_percent_papers(paths)

    get_top_cascade(paths)













