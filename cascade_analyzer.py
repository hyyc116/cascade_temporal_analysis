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




if __name__ == '__main__':

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

