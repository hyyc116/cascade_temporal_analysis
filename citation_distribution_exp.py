#coding:utf-8
'''
1. 首先将所有的论文、各个子领域的论文的引用次数进行存储
2. 将各个文件的引用次数分布分高中低
3. 画图， 将三种高中低的识别方式的文章比例、分界列出进行比较

'''

from basic_config import *
from paper_grouping import *

### 读取所有的论文及各类别的引用次数分布
def read_subject_cns():

	logging.info('loding data/_id_cn.json ....')
	_id_cn = json.loads(open('data/_id_cn.json').read())

	logging.info('loading data/_ids_top_subjects.json ...')

	_id_top_subj = json.loads(open('data/_ids_top_subjects.json').read())

	subj_cns = defaultdict(list)

	for _id in _id_cn.keys():

		subj_cns['ALL'].append(_id_cn[_id])

		for subj in _id_top_subj[_id]:

			subj_cns[subj].append(_id_cn[_id])

	## 存储
	open('data/subj_cns.json','w').write(json.dumps(subj_cns))
	logging.info('data saved to data/subj_cns.json.')

def group_subject_papers():

	subj_cns = json.loads(open('data/subj_cns.json').read())
	## 所有论文的citation count识别
	for i,subj in enumerate(subj_cns.keys()):

		cns = subj_cns[subj]
		logging.info('{:}th subject is {:}'.format(i,subj))
		group_papers(cns,'fig/citation_distribution_{:}.png'.format(i))


def compare_methods():

	pass


if __name__ == '__main__':
	read_subject_cns()
	group_subject_papers()









