#coding:utf-8
from basic_config import *

'''
    
    1. 计算所有学科的每一篇论文 本领域引用与全领域引用的比例
    2. 不同领域的RR的分布
    3. 分高中低 的箱式图
    4. 随着citation count的变化的变化曲线
    5. 随时间的变化曲线


'''

def stat_relative_ratio():
    # 加载基本数据
    pid_topsubjs,pid_pubyear,pid_cn = load_basic_data(['topsubj','year','cn'])


    ref_citations = defaultdict(list)
    progress=0
    for line in open('../WOS_data_processing/data/pid_refs.txt'):
        line = line.strip()
        pid_refs = json.loads(line)
        logging.info(f'progress {progress} ..')
        for pid in pid_refs.keys():

            topsubjs = pid_topsubjs[pid]

            if int(pid_pubyear[pid])>2016 or int(pid_pubyear[pid])<1900:
                continue

            for ref in pid_refs[pid]:

                ref_citations[ref].append(topsubjs)


    logging.info('processing done, start to cal relative ratio')

    pid_rr = {}

    for ref in ref_citations.keys():

        topsubjs = set(pid_topsubjs[ref])

        focal_num = len([1 for subjs in ref_citations[ref] if len(topsubjs&set(subjs))>=0])

        relative_ratio = focal_num/float(len(ref_citations))

        pid_rr[ref] = relative_ratio


    open('data/pid_relative_ratio.json','w').write(json.dumps(pid_rr))

    logging.info('data saved to data/pid_relative_ratio.json.')


def load_basic_data(attrs=['year','subj','topsubj','teamsize','doctype','cn'],isStat=False):

    logging.info('======== LOADING BASIC DATA =============')
    logging.info('======== ================== =============')

    results = {}

    if 'year' in attrs:

        logging.info('loading paper pubyear ...')
        pid_pubyear = json.loads(open('../WOS_data_processing/data/pid_pubyear.json').read())
        logging.info('{} papers has year label.'.format(len(pid_pubyear.keys())))

        results['year']=pid_pubyear

    if 'subj' in attrs:
        logging.info('loading paper subjects ...')
        pid_subjects = json.loads(open('../WOS_data_processing/data/pid_subjects.json').read())
        logging.info('{} papers has subject label.'.format(len(pid_subjects.keys())))

        results['subj'] = pid_subjects

    if 'topsubj' in attrs:
        logging.info('loading paper top subjects ...')
        pid_topsubjs = json.loads(open('../WOS_data_processing/data/pid_topsubjs.json').read())
        logging.info('{} papers has top subject label.'.format(len(pid_topsubjs.keys())))
        
        results['topsubj']=pid_topsubjs


    if 'teamsize' in attrs:

        logging.info('loading paper teamsize ...')
        pid_teamsize = json.loads(open('../WOS_data_processing/data/pid_teamsize.json').read())
        logging.info('{} papers has teamsize label.'.format(len(pid_teamsize.keys())))

        results['teamsize'] = pid_teamsize

    if 'doctype'  in attrs:

        logging.info('loading paper doctype ...')
        pid_doctype = json.loads(open('../WOS_data_processing/data/pid_doctype.json').read())
        logging.info('{} papers has doctype label.'.format(len(pid_doctype.keys())))

        results['doctype'] = pid_doctype

    
    if 'c5' in attrs:

        logging.info('loading paper citation c5 ...')
        pid_cn = json.loads(open('../WOS_data_processing/data/pid_c5.json').read())
        logging.info('{} papers has c5 label.'.format(len(pid_cn.keys())))

        results['c5']=pid_cn

    if 'c10' in attrs:

        logging.info('loading paper citation c10 ...')
        pid_cn = json.loads(open('../WOS_data_processing/data/pid_c10.json').read())
        logging.info('{} papers has c10 label.'.format(len(pid_cn.keys())))

        results['c10']=pid_cn

    if 'cn' in attrs:

        logging.info('loading paper citation count ...')
        pid_cn = json.loads(open('../WOS_data_processing/data/pid_cn.json').read())
        logging.info('{} papers has citation count label.'.format(len(pid_cn.keys())))

        results['cn']=pid_cn

    if isStat:
        interset = set(pid_pubyear.keys())&set(pid_teamsize.keys())&set(pid_topsubjs.keys())&set(pid_topsubjs.keys())
        logging.info('{} papers has both four attrs.'.format(len(interset)))

    logging.info('======== LOADING BASIC DATA DONE =============')
    logging.info('======== ======================= =============')


    if len(attrs)>=1:
        
        return [results[attr] for attr in attrs]

    else:
        return None



if __name__ == '__main__':
    stat_relative_ratio()