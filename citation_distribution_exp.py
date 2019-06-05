#coding:utf-8
'''
1. 首先将所有的论文、各个子领域的论文的引用次数进行存储
2. 将各个文件的引用次数分布分高中低
3. 画图， 将三种高中低的识别方式的文章比例、分界列出进行比较

'''

from basic_config import *

### 读取所有的论文及各类别的引用次数分布
def read_subject_cns():

	logging.info('loding data/_id_cn.json ....')
	_id_cn = json.loads(open('data/_id_cn.json').read())

	logging.info('loading data/_ids_top_subjects.json ...')

	_id_top_subj = json.loads(open('data/_id_cn.json').read())

	subj_cns = defautdict(list)

	for _id in _id_cn.keys():

		subj_cns['ALL'] = _id_cn[_id]

		for subj in _id_top_subj[_id]:

			subj_cns[subj].append(_id_cn[_id])

	## 存储
	open('data/subj_cns.json','w').write(json.dumps(subj_cns))
	logging.info('data saved to data/subj_cns.json.')

def group_papers():

	subj_cns = json.loads(open('data/subj_cns.json').read())
	## 所有论文的citation count识别
	for subj in subj_cns.keys():

		pass


def compare_methods():

	pass










