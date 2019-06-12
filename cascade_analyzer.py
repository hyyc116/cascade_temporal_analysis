#coding:utf-8

'''
    Tasks in this script:

        1. analyze the result from our facets

'''
## task 1

from basic_config import *


import argparse

field_dict = {
    0:'ALL',
    1:'Arts & Humanities',
    2:'Clinical, Pre-Clinical & Health',
    3:'Engineering & Technology',
    4:'Life Sciences',
    5:'Physical Sciences',
    6:'Social Sciences'
}

doctype_dict = {

}

## 所有论文的dccp
def dccp_of_paper(pathObj):

    _id_dccp = {}

    logging.info('start to stat dccp of all papers ....')
    progress = 0
    for line in open(pathObj.cascade_path):
        cascades = json.loads(line)

        logging.info('{:} line processed ...'.format(progress))
        progress+=1

        for pid in cascades.keys():

            edges = cascades[pid]

            direct_cit_num = 0
            for e_cpid,e_pid in edges:
                if e_pid == pid:
                    direct_cit_num+=1

            if direct_cit_num==len(edges):

                has_dccp=0
            else:
                has_dccp=1

            _id_dccp[pid] = has_dccp

    open(pathObj.dccp_path,'w').write(json.dumps(_id_dccp))
    logging.info('id dccp json saved to {:} .'.format(pathObj.dccp_path))



def parse_args():
    parser = argparse.ArgumentParser(usage='python %(prog)s [options] \n  exp. python -m ST-NA-ALL -f impact')

    ## 领域选择
    parser.add_argument('-f','--field',dest='field',default='ALL',type=str,choices=[0,1,2,3,4,5,6],help='field code dict %s' % str(field_dict))
    ## 数据开始时间
    parser.add_argument('-s','--start_year',dest='start_year',type=int,help='start year of papers used in analyzing.')
    ## 数据结束时间
    parser.add_argument('-e','--end_year',dest='end_year',type=int,help='end year of papers used in analyzing.')
    ## 文章类型
    parser.add_argument('-t','--doctype',dest='doctype',type=int,default=30,help='set doctype, default is 30.')

    ## 是否从数据文件生成，或者直接生成成图
    parser.add_argument('-D','--from_data',action='store_true',dest='from_data',default=False,help='wether generate from data directly,default is True')


    arg = parser.parse_args()


if __name__ == '__main__':

    field = 'ALL'
    paths = PATHS(field)
    dccp_of_paper(paths)



