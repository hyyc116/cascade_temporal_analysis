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

labels = ['1-inf','5-inf','10-inf','20-inf','50-inf','100-inf','500-inf','1000-inf'] 


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

## 根据id的各种属性进行分类
def stats_on_facets(_id,_id_subjects,_id_cn,_id_doctype,_id_year):

    ## 六个顶级领域,一篇论文可能属于多个领域，所以返回一个list
    top_sujects = _id_subjects[_id]

    ## 返回每一个ID的被引次数
    cn = _id_cn[_id]
    ## 被引次数可分为多个 1-inf,5-inf,10-inf,20-inf,50-inf,100-inf,500-inf,1000-inf

    if cn >= 1000:
        cn_clas =  [1,1,1,1,1,1,1,1]
    elif cn >=500:
        cn_clas =  [1,1,1,1,1,1,1,0]
    elif cn >= 100:
        cn_clas =  [1,1,1,1,1,1,0,0]
    elif cn>= 50:
        cn_clas =  [1,1,1,1,1,0,0,0]
    elif cn>= 20:
        cn_clas =  [1,1,1,1,0,0,0,0]
    elif cn>= 10:
        cn_clas =  [1,1,1,0,0,0,0,0]
    elif cn>= 5:
        cn_clas =  [1,1,0,0,0,0,0,0]
    else:
        cn_clas =  [1,0,0,0,0,0,0,0]

    ## 返回每一个id的doctype, 只分析doctype数量前十的论文
    doctype = _id_doctype[_id]

    ## 发表年份
    year  = _id_year[_id]

    return top_sujects,cn_clas,doctype,year


def load_attrs(pathObj):

    logging.info('loading _id_subjects ...')
    _id_subjects = json.loads(open(pathObj.paper_id_topsubj).read())

    logging.info('loading _id_cn ...')
    _id_cn = json.loads(open(pathObj.paper_cit_num_path).read())

    logging.info('loading _id_doctype ...')
    _id_doctype = json.loads(open(pathObj.paper_doctype_path).read())

    doctype_counter = Counter(_id_doctype.values())
    top10_doctypes = sorted(doctype_counter.keys(),key=lambda x:doctype_counter[x],reverse=True)[:10]
    logging.info('top 10 doctypes:{:}'.format(top10_doctypes))

    logging.info('loading _id_pubyear ...')
    _id_pubyear = json.loads(open(pathObj.paper_year_path).read())

    logging.info('Data loaded')

    return _id_subjects,_id_cn,_id_doctype,_id_pubyear,top10_doctypes

def dccp_on_facets(pathObj,field,start_year,end_year,interval,doctype_,_id_subjects,_id_cn,_id_doctype,_id_year,top10_doctypes,cn_t,_t='point'):

    logging.info('stating dccp of field {:}, from year {:} to year {:} with interval {:} and doctype {:}'.format(field,start_year,end_year,interval,doctype_))

    ## 加载DCCP的数据
    logging.info('loading dccp data ...')
    _id_dccp=json.loads(open(pathObj.dccp_path).read())

    ## 只需要过滤所有的数据 然后统计分布就行了
    if _t=='point':

        dccps = []
        for _id in _id_dccp.keys():
            ## 获得这一篇论文的基础属性值
            _top_sujects,_cn_clas,_doctype,_year = stats_on_facets(_id,_id_subjects,_id_cn,_id_doctype,_id_year)

            ## field 只有是all或者top field中的一个才可以
            if field!='ALL' and field not in _top_sujects:
                continue

            ## 年份,point的start_year和end_year相同或者保留所有的年份数据
            if int(_year) < start_year or int(_year) > end_year:
                continue

            ## doctype
            if doctype_!='ALL' and doctype_!=_doctype:
                continue

            ## citation range,_cn_class是不同range的标签，如果是1就说明在这个range内
            if _cn_clas[citation_range]==1:
                continue

            ## 剩下的就是剩余的论文的dccp，画出其分布的柱状图，并且标明均值和中位数
            dccps.append(_id_dccp[_id])

        plt.figure(figszie=(4,3))

        plt.hist(dccps,bins=20)

        plt.xlabel('Percentage of DCCP')
        plt.ylabel('percentage')

        if start_year!=end_year:
            year='ALL'
        else:
            year=  start_year
        plt.title('{:}-{:}-{:}-{:}'.format(field,doctype,labels[citation_range],year))

        plt.tight_layout()


        plt.savefig('{:}-{:}-{:}-{:}-dccp-point.png'.format(field,doctype,labels[citation_range],year),dpi=300)

        print('fig saved to {:}-{:}-{:}-{:}-dccp-point.png'.format(field,doctype,labels[citation_range],year))


    # else:



    # # year_doctype_cnclas_dccp = defaultdict(lambda:defaultdict(lambda:defaultdict(int)))
    # year_dccp = defaultdict(list)
    # doctype_dccp = defaultdict(list)
    # cnclas_dccp = defaultdict(list)

    # doctype_year_dccp = defaultdict(lambda:defaultdict(list))
    # cnclas_year_dccp = defaultdict(lambda:defaultdict(list))

    # logging.info('stating dccp ...')
    # progress=0
    # for _id in _id_dccp.keys():
    #     _top_sujects,_cn_clas,_doctype,_year = stats_on_facets(_id,_id_subjects,_id_cn,_id_doctype,_id_year)
    #     dccp = _id_dccp[_id]
    #     ## 领域
    #     if field!='ALL' and field not in _top_sujects:
    #         continue

    #     ## 年份
    #     if int(_year) < start_year or int(_year) > end_year:
    #         continue

    #     ## doctype
    #     if doctype_!='ALL' and doctype_!=_doctype:
    #         continue


    #     progress+=1

    #     if progress%100000==1:
    #         logging.info('progress {:} ...'.format(progress))

    #     for i,_cn in enumerate(_cn_clas):

    #         if _cn==1:
    #             cnclas_dccp[i].append(dccp)
    #             cnclas_year_dccp[i][int(_year)].append(dccp)

    #     doctype_dccp[_doctype].append(dccp)

    #     year_dccp[int(_year)].append(dccp)

    #     doctype_year_dccp[_doctype][int(_year)].append(dccp)


    # logging.info('plotting data ....')
    # fig,axes = plt.subplots(2,2,figsize=(8,7))

    # ax0 = axes[0,0]
    # ## 画出所有的citation num的dccp分布
    # xs = []
    # ys = []
    # for _cn in cnclas_dccp.keys():

    #     dccp = cnclas_dccp[_cn]

    #     percent = np.sum(dccp)/float(len(dccp))

    #     xs.append(_cn)

    #     ys.append(percent)

    # logging.info('xs:{:}'.format(xs))
    # logging.info('ys:{:}'.format(ys))

    # ax0.bar(xs,ys)
    # ax0.set_xticks(xs)
    # ax0.set_xticklabels(labels)

    # ax0.set_xlabel('number of citation range')
    # ax0.set_ylabel('percetage of DCCP')

    # ## 画出doctype的
    # ax1 = axes[0,1]
    # xs = []
    # ys = []
    # for doctype in top10_doctypes:

    #     dccp = doctype_dccp[doctype]

    #     percent = np.sum(dccp)/float(len(dccp))

    #     xs.append(doctype)

    #     ys.append(percent)

    # ax1.bar(range(len(xs)),ys)
    # ax1.set_xticks(range(len(xs)))
    # ax1.set_xticklabels(xs,rotation=-60)

    # ax1.set_xlabel('doctype')
    # ax1.set_ylabel('percetage of DCCP')

    # ## 画出year的关系
    # ax2 = axes[1,0]
    
    # for cnclas in cnclas_year_dccp.keys():
    #     year_dccp = cnclas_year_dccp[cnclas]
    #     xs = []
    #     ys = []
    #     for year in sorted(year_dccp.keys()):
    #         xs.append(year)
    #         dccp = year_dccp[year]

    #         percent = np.sum(dccp)/float(len(dccp))
    #         ys.append(percent)

    #     ax2.plot(xs,ys,label=labels[cnclas])

    # ax2.set_xlabel("year")
    # ax2.set_ylabel('percentage of DCCP')
    # ax2.legend()

    # ## 画出year的关系
    # ax3 = axes[1,1]
    
    # for doctype in top10_doctypes:
    #     year_dccp = doctype_year_dccp[doctype]
    #     xs = []
    #     ys = []
    #     for year in sorted(year_dccp.keys()):
    #         xs.append(year)
    #         dccp = year_dccp[year]

    #         percent = np.sum(dccp)/float(len(dccp))
    #         ys.append(percent)

    #     ax3.plot(xs,ys,label=doctype)

    # ax3.set_xlabel("year")
    # ax3.set_ylabel('percentage of DCCP')
    # ax3.legend()

    # plt.tight_layout()

    # plt.savefig('fig/{:}_{:}_{:}_{:}_dccp.png'.format(field,doctype_,start_year,end_year),dpi=400)

    # logging.info('fig saved to fig/{:}'.format('{:}_{:}_{:}_{:}_dccp.png'.format(field,doctype_,start_year,end_year)))


def size_of_subcascade_on_facets():

    pass


def num_of_comp_on_facets():

    pass

### 不同学科、不同引用次数、不同类型的common motif
def common_motif_on_facets(pathObj,field,start_year,end_year,interval,doctype_,_id_subjects,_id_cn,_id_doctype,_id_year,top10_doctypes,_t='point'):
    logging.info('stating common motif of field {:}, from year {:} to year {:} with interval {:} and doctype {:}'.format(field,start_year,end_year,interval,doctype_))

    ## 加载DCCP的数据
    logging.info('loading paper subcascades  ...')
    paper_size_id=json.loads(open(pathObj.paper_subcascades_path).read())

    # year_doctype_cnclas_dccp = defaultdict(lambda:defaultdict(lambda:defaultdict(int)))
    # year_dccp = defaultdict(list)
    doctype_subcasid = defaultdict(list)
    cnclas_subcasid = defaultdict(list)

    doctype_year_subcasid = defaultdict(lambda:defaultdict(list))
    cnclas_year_subcasid = defaultdict(lambda:defaultdict(list))

    logging.info('stating dccp ...')
    progress=0
    for _id in paper_size_id.keys():
        _top_sujects,_cn_clas,_doctype,_year = stats_on_facets(_id,_id_subjects,_id_cn,_id_doctype,_id_year)
        # dccp = _id_dccp[_id]

         ## 领域
        if field!='ALL' and field not in _top_sujects:
            continue

        ## 年份
        if int(_year) < start_year or int(_year) > end_year:
            continue

        ## doctype
        if doctype_!='ALL' and doctype_!=_doctype:
            continue

        progress+=1

        if progress%100000==1:
            logging.info('progress {:} ...'.format(progress))

        all_subcas_ids = []
        for size in paper_size_id[_id].keys():
            subcas_ids = paper_size_id[_id][size]

            all_subcas_ids.extend(subcas_ids)

        all_subcas_ids = list(set([subcas_id for subcas_id in all_subcas_ids if subcas_id!=-999]))

        doctype_subcasid[_doctype].extend(all_subcas_ids)

        for i,_cn_clas in enumerate(_cn_clas):

            if _cn_clas==1:
                cnclas_subcasid[i].extend(all_subcas_ids)

    ### 把一个学科的 不同类型 不同次数的最频繁的10个subcascade画出来
    readme = open('README.md','w')
    lines = ['### Subject:{:}'.format(field)]

    for doctype in top10_doctypes:
        logging.info('doctype:{:}'.format(doctype))
        lines.append('#### doctype:{:}'.format(doctype))
        lines.append('|order|motif|frequency|')
        lines.append('|:----:|:-----:|:----:|')

        id_counter = Counter(doctype_subcasid[doctype])

        for i,_id in enumerate(sorted(id_counter.keys(),key=lambda x:id_counter[x],reverse=True)[:10]):

            lines.append('|{:}|![subcascade](subcascade/fig/subcas_{:}.jpg)|{:}|'.format(i,_id,id_counter[_id]))
    
    readme.write('\n'.join(lines))

    lines = ['### number of citations']
    for cnclas in sorted(cnclas_subcasid.keys()):
        subject_name = labels[cnclas]
        logging.info('subject:{:}'.format(subject_name))
        lines.append('#### subject:{:}'.format(subject_name))
        lines.append('|order|motif|frequency|')
        lines.append('|:----:|:-----:|:----:|')

        id_counter = Counter(cnclas_subcasid[cnclas])

        for i,_id in enumerate(sorted(id_counter.keys(),key=lambda x:id_counter[x],reverse=True)[:10]):

            lines.append('|{:}|![subcascade](subcascade/fig/subcas_{:}.jpg)|{:}|'.format(i,_id,id_counter[_id]))
    
    readme.write('\n'.join(lines))

def parse_args(pathObj):
    parser = argparse.ArgumentParser(usage='python %(prog)s [options]')

    ## 领域选择
    parser.add_argument('-f','--field',dest='field',default=0,type=int,choices=[0,1,2,3,4,5,6],help='field code dict %s' % str(field_dict))
    ## 数据开始时间
    parser.add_argument('-s','--start_year',dest='start_year',default=1980,type=int,help='start year of papers used in analyzing.')
    ## 数据结束时间
    parser.add_argument('-e','--end_year',dest='end_year',default=2019,type=int,help='end year of papers used in analyzing.')
    ## 数据的时间间隔
    parser.add_argument('-i','--interval',dest='interval',default=1,type=int,help='interval of data.')

    ## citation range
    parser.add_argument('-c','--citation_range',dest='citation_range',default=0,type=int,choices=[0,1,2,3,4,5,6,7],help='interval of data.')

    ## 文章类型
    parser.add_argument('-d','--doctypeid',dest='doctypeid',default='ALL',type=str,choices=['ALL','0','1','2','3','4','5','6','7','8','9'],help='doctype used, ALL means top 10.')

     parser.add_argument('-t','--optype',dest='optype',default='point',type=str,choices=['point','temporal'],help='op type:point or temporal')

    ## 操作类型
    parser.add_argument('-p','--operation',dest='operation',default='dccp',type=str,choices=['dccp','subcas_num','subcas_size','motif'],help='select operations')

    arg = parser.parse_args()

    field = arg.field

    field_name = field_dict[field].replace(' ','_').replace('&','and')

    start_year = arg.start_year

    end_year = arg.end_year

    doctype_id = arg.doctypeid

    interval = arg.interval

    operation = arg.operation

    _id_subjects,_id_cn,_id_doctype,_id_year,top10_doctypes = load_attrs(pathObj)

    citation_range = arg.citation_range

    _t = arg.optype

    print('top 10 doctype: ',top10_doctypes)

    if doctype_id!='ALL':
        doctype= top10_doctypes[int(doctype_id)]
        print('-----doctype:',doctype)
    else:
        doctype='ALL'

    if operation=='dccp':
        dccp_on_facets(pathObj,field_name,start_year,end_year,interval,doctype,_id_subjects,_id_cn,_id_doctype,_id_year,top10_doctypes,citation_range,_t)
    
    elif operation=='motif':
        common_motif_on_facets(pathObj,field_name,start_year,end_year,interval,doctype,_id_subjects,_id_cn,_id_doctype,_id_year,top10_doctypes,citation_range,_t)
    else:
        print 'no such action.'


if __name__ == '__main__':

    field = 'ALL'
    paths = PATHS(field)
    parse_args(paths)
   



