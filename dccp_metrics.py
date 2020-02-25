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

labels = ['1-inf','5-inf','10-inf','20-inf','50-inf','100-inf','500-inf','1000-inf']


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
    year  = int(_id_year[_id])

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


markers = ['o','>','^','s','.','*','D','<']
### 不同的field为一条线，然后分别描述dccp与citation count， dccp与doctype，dccp与时间之间的相互变化关系
def dccp_depits(_id_dccp,start_year,end_year,_id_subjects,_id_cn,_id_doctype,_id_year,top10_doctypes,SCIENTO_IDS):

    ### 领域内不同cc对应的dccps
    field_cc_dccps = defaultdict(lambda:defaultdict(list))
    field_ccbin_eins = defaultdict(lambda:defaultdict(list))

    field_cc_eins = defaultdict(lambda:defaultdict(list))

    ## 领域 时间 dccps
    field_year_dccps = defaultdict(lambda:defaultdict(list))
    field_year_eins = defaultdict(lambda:defaultdict(list))

    ## 领域 doctype dccps
    field_doctype_dccps = defaultdict(lambda:defaultdict(list))
    field_doctype_eins = defaultdict(lambda:defaultdict(list))

    ## 加载shuffle之后的结果
    pathss = PATHS('RND')
    _id_dccp_rnd = json.loads(open(pathss.dccp_path).read())

    logging.info('startting to stat dccp ...')
    for _id in _id_dccp.keys():

        if _id_cn.get(_id,None) is None:
            continue

        ## 获得这一篇论文的基础属性值
        _cn = int(_id_cn[_id])
        _top_sujects,_cn_clas,_doctype,_year = stats_on_facets(_id,_id_subjects,_id_cn,_id_doctype,_id_year)

        ## 过滤时间
        if int(_year)>end_year or int(_year)<start_year:
            continue

        for subj in _top_sujects:

            field_cc_dccps[subj][_cn].append(_id_dccp[_id][0])

            field_cc_eins[subj][_cn].append(_id_dccp[_id][1]/float(_cn))
            for cc_ix,_cc_cl in enumerate(_cn_clas):
                if _cc_cl==1:
                    field_ccbin_eins[subj][cc_ix].append(_id_dccp[_id][1]/float(_cn))

            field_year_dccps[subj][_year].append(_id_dccp[_id][0])
            field_year_eins[subj][_year].append(_id_dccp[_id][1]/float(_cn))

            field_doctype_dccps[subj][_doctype].append(_id_dccp[_id][0])
            field_doctype_eins[subj][_doctype].append(_id_dccp[_id][1]/float(_cn))

        field_doctype_dccps['WOS_ALL'][_doctype].append(_id_dccp[_id][0])
        field_doctype_eins['WOS_ALL'][_doctype].append(_id_dccp[_id][1]/float(_cn))

        field_doctype_dccps['RANDOMIZE'][_doctype].append(_id_dccp_rnd[_id][0])
        field_doctype_eins['RANDOMIZE'][_doctype].append(_id_dccp_rnd[_id][1])

        field_year_dccps['WOS_ALL'][_year].append(_id_dccp[_id][0])
        field_year_eins['WOS_ALL'][_year].append(_id_dccp[_id][1]/float(_cn))

        field_year_dccps['RANDOMIZE'][_year].append(_id_dccp_rnd[_id][0])
        field_year_eins['RANDOMIZE'][_year].append(_id_dccp_rnd[_id][1])

        field_cc_dccps['WOS_ALL'][_cn].append(_id_dccp[_id][0])
        field_cc_eins['WOS_ALL'][_cn].append(_id_dccp[_id][1]/float(_cn))

        field_cc_dccps['RANDOMIZE'][_cn].append(_id_dccp_rnd[_id][0])
        field_cc_eins['RANDOMIZE'][_cn].append(_id_dccp_rnd[_id][1])

        for cc_ix,_cc_cl in enumerate(_cn_clas):
            if _cc_cl==1:
                field_ccbin_eins['WOS_ALL'][cc_ix].append(_id_dccp[_id][1]/float(_cn))
                field_ccbin_eins['RANDOMIZE'][cc_ix].append(_id_dccp_rnd[_id][1])

        if _id in SCIENTO_IDS:

            # field_doctype_dccps['SCIENTOMETRICS'][_doctype].append(_id_dccp[_id][0])
            # field_doctype_eins['SCIENTOMETRICS'][_doctype].append(_id_dccp[_id][1]/float(_cn))

            field_year_dccps['SCIENTOMETRICS'][_year].append(_id_dccp[_id][0])
            field_year_eins['SCIENTOMETRICS'][_year].append(_id_dccp[_id][1]/float(_cn))

            field_cc_dccps['SCIENTOMETRICS'][_cn].append(_id_dccp[_id][0])
            field_cc_eins['SCIENTOMETRICS'][_cn].append(_id_dccp[_id][1]/float(_cn))

            for cc_ix,_cc_cl in enumerate(_cn_clas):
                if _cc_cl==1:
                    field_ccbin_eins['SCIENTOMETRICS'][cc_ix].append(_id_dccp[_id][1]/float(_cn))


    open('data/field_cc_dccps.json','w').write(json.dumps(field_cc_dccps))

    open('data/field_cc_eins.json','w').write(json.dumps(field_cc_eins))
    open('data/field_ccbin_eins.json','w').write(json.dumps(field_ccbin_eins))
    open('data/field_year_dccps.json','w').write(json.dumps(field_year_dccps))
    open('data/field_year_eins.json','w').write(json.dumps(field_year_eins))
    open('data/field_doctype_dccps.json','w').write(json.dumps(field_doctype_dccps))
    open('data/field_doctype_eins.json','w').write(json.dumps(field_doctype_eins))

    logging.info('data saved.')

    # boxplot()

def boxplot():

    MAXMIN,MINMAX = minmax_maxmin()

    field_cc_eins = json.loads(open('data/field_cc_eins.json').read())
    field_CLS_dccps = defaultdict(lambda:defaultdict(list))

    for fi,field in enumerate(sorted(field_cc_eins.keys())):

        ## dccp随着citation count的变化
        xs = []
        ys = []
        for cc in sorted(field_cc_eins[field].keys(),key=lambda x:int(x)):

            if int(cc)<MAXMIN:
                CLS = 0
            elif int(cc)<MINMAX:
                CLS = 1
            else:
                CLS = 2

            dccps  = [float(f) for f in field_cc_eins[field][cc] if float(f)>0]

            field_CLS_dccps[field][CLS].extend(dccps)

    ## file CLs DCCPS box plots
    fig,axes = plt.subplots(2,4,figsize=(26,8))
    for i,subj in enumerate(sorted(field_CLS_dccps.keys())):
        logging.info('field {} ...'.format(subj))
        data = []
        for CLS in sorted(field_CLS_dccps[subj].keys()):
            logging.info('CLS:{}'.format(CLS))
            # logging.info('num of dccps:{}'.format())
            data.append(field_CLS_dccps[subj][CLS])

        print('length of data {}'.format(len(data)))

        ax = axes[i/4,i%4]

        ax.boxplot(data,labels=['lowly cited','medium cited','highly cited'],showfliers=True)

        ax.set_xlabel('Paper Impact Level')
        ax.set_ylabel('$e_{i-norm}$')
        ax.set_yscale('log')
        ax.set_title('{}'.format(subj))

    plt.tight_layout()

    plt.savefig('fig/boxplot_wos_all.png',dpi=300)

    logging.info('fig saved to fig/boxplot_wos_all.png.')



def plot_dccps():

    top10_doctypes = ['Article','Review','Proceedings Paper','Letter','Book Review','Editorial Material']


    field_cc_dccps = json.loads(open('data/field_cc_dccps.json').read())
    field_ccbin_eins = json.loads(open('data/field_ccbin_eins.json').read())

    field_year_dccps = json.loads(open('data/field_year_dccps.json').read())
    field_year_eins = json.loads(open('data/field_year_eins.json').read())

    field_doctype_dccps = json.loads(open('data/field_doctype_dccps.json').read())
    field_doctype_eins = json.loads(open('data/field_doctype_eins.json').read())

    logging.info('startting to plotting ....')
    fig,axes = plt.subplots(1,3,figsize=(20,5))
    ## 分不同的领域查看dccp随着citation count, doctype, 时间之间的变化
    for fi,field in enumerate(sorted(field_cc_dccps.keys())):

        ## dccp随着citation count的变化
        ax = axes[0]
        xs = []
        ys = []
        for cc in sorted(field_cc_dccps[field].keys(),key=lambda x:int(x)):


            dccps  = field_cc_dccps[field][cc]


            ## dccp 在这个的比例
            p_of_dccp = np.sum(dccps)/float(len(dccps))

            xs.append(int(cc))
            ys.append(p_of_dccp)

            if int(cc)==10 and field=='WOS_ALL':
                logging.info('P(e>n|C=n) is {}/{} = {} when citation number is 10.'.format(np.sum(dccps),float(len(dccps)),p_of_dccp))


        ax.plot(xs,ys,label='{}'.format(field))
        ax.set_xscale('log')

        ax.set_xlabel('number of citations')
        ax.set_ylabel('$P(e>n|C=n)$')
        ax.set_xlim(1,1000)
        lgd = ax.legend(loc=9,bbox_to_anchor=(0.5, -0.15), ncol=2)



        ## dccp与时间之间的关系
        ax2 = axes[1]
        xs = []
        ys = []
        for year in sorted(field_year_dccps[field].keys(),key=lambda x:int(x)):
            dccps = field_year_dccps[field][year]
            ## dccp 在这个的比例
            p_of_dccp = np.sum(dccps)/float(len(dccps))

            xs.append(int(year))
            ys.append(p_of_dccp)
        ax2.plot(xs,ys,label='{}'.format(field))

        ax2.set_xlabel('Year')
        ax2.set_ylabel('$P(e>n|C=n)$')

        lgd2 = ax2.legend(loc=9,bbox_to_anchor=(0.5, -0.15), ncol=2)


        ## dccp与doctype的关系
        if field=='SCIENTOMETRICS':
            continue

        ax1 = axes[2]
        xs = []
        ys = []
        for doctype in top10_doctypes:

            dccps = field_doctype_dccps[field][doctype]
            ## dccp 在这个的比例
            p_of_dccp = np.sum(dccps)/float(len(dccps))

            xs.append(doctype)
            ys.append(p_of_dccp)

        # ax1.plot(range(len(top10_doctypes)),ys,label='{}'.format(field),marker=markers[fi])

        width = 0.1
        bi = fi-3
        if bi>2:
            bi = bi-1
        bias = bi*width
        ax1.bar(np.arange(len(top10_doctypes))+bias,ys,width=width,label='{}'.format(field))

        ax1.set_xticks(range(len(top10_doctypes)))
        ax1.set_xticklabels(top10_doctypes,rotation=-90)
        ax1.set_xlabel('Doctype')
        ax1.set_ylabel('$P(e>n|C=n)$')


        ax1.legend()

        # ax2.legend()

    plt.tight_layout()
    plt.savefig('fig/dccp_total.png',dpi=300,additional_artists=[lgd,lgd2],
    bbox_inches="tight")
    logging.info('fig saved to fig/dccp_total.png.')


    fig,axes = plt.subplots(1,3,figsize=(18,5))
    ## 分不同的领域查看ein随着citation count, doctype, 时间之间的变化




    ## 统计不同学科的e_i-norm的list
    subj_eins = defaultdict(list)
    for fi,field in enumerate(sorted(field_ccbin_eins.keys())):

        ## dccp随着citation count的变化
        ax = axes[0]
        xs = []
        ys = []
        for cc in sorted(field_ccbin_eins[field].keys(),key=lambda x:int(x)):

            if int(cc)<36:
                CLS = 0
            elif int(cc)<120:
                CLS = 1
            else:
                CLS = 2

            dccps  = field_ccbin_eins[field][cc]

            # field_CLS_dccps[field][CLS].extend(dccps)


            subj_eins[field].extend(dccps)

            ## dccp 在这个的比例
            p_of_dccp = np.mean(dccps)

            xs.append(int(cc))
            ys.append(p_of_dccp)

            if field.startswith('Art') and labels[int(cc)]=='1000-inf':
                logging.info('number of papers in 1000-inf in {} is {}'.format(field,len(dccps)))

        ax.plot(xs,ys,label='{}'.format(field))
        # ax.set_xscale('log')
        ax.set_xticks(xs)
        ax.set_xticklabels(labels)

        ax.set_xlabel('number of citations')
        ax.set_ylabel('$e_{i-norm}$')
        lgd = ax.legend(loc=9,bbox_to_anchor=(0.5, -0.15), ncol=2)





        ## dccp与时间之间的关系
        ax2 = axes[1]
        xs = []
        ys = []
        for year in sorted(field_year_eins[field].keys(),key=lambda x:int(x)):
            dccps = field_year_eins[field][year]
            ## dccp 在这个的比例
            p_of_dccp = np.sum(dccps)/float(len(dccps))

            xs.append(int(year))
            ys.append(p_of_dccp)
        ax2.plot(xs,ys,label='{}'.format(field))

        ax2.set_xlabel('Year')
        ax2.set_ylabel('$e_{i-norm}$')

        lgd2 = ax2.legend(loc=9,bbox_to_anchor=(0.5, -0.15), ncol=2)


        if field == 'SCIENTOMETRICS':
            continue
        ## dccp与doctype的关系
        ax1 = axes[2]
        xs = []
        ys = []
        for doctype in top10_doctypes:
            dccps = field_doctype_eins[field][doctype]
            ## dccp 在这个的比例
            # p_of_dccp = np.mean(dccps)
            p_of_dccp = np.sum(dccps)/float(len(dccps))

            xs.append(doctype)
            ys.append(p_of_dccp)

        # ax1.plot(range(len(top10_doctypes)),ys,label='{}'.format(field),marker=markers[fi])

        width = 0.1
        bi = fi-3
        if bi>2:
            bi = bi-1
        bias = bi*width
        ax1.bar(np.arange(len(top10_doctypes))+bias,ys,width=width,label='{}'.format(field))

        ax1.set_xticks(range(len(top10_doctypes)))
        ax1.set_xticklabels(top10_doctypes,rotation=-90)
        ax1.set_xlabel('Doctype')
        ax1.set_ylabel('$e_{i-norm}$')


        ax1.legend()

        # ax2.legend()

    plt.tight_layout()
    plt.savefig('fig/eins_total.png',dpi=300,additional_artists=[lgd,lgd2],
    bbox_inches="tight")
    logging.info('fig saved to fig/eins_total.png.')


    # logging.info('Done')




    # return


    ## eins的ccdf
    plt.figure(figsize=(5,4))
    for subj in sorted(subj_eins.keys()):


        eins = [f for f in [float('{:.3f}'.format(ein)) for ein in subj_eins[subj]] if f>0]

        logging.info('subj:{},len:{}'.format(subj,len(eins)))


        eins_counter = Counter(eins)
        xs = []
        ys = []

        for x in sorted(eins_counter.keys()):

            xs.append(x)
            ys.append(eins_counter[x])

        xs,ys = cdf(xs,ys)

        plt.plot(xs,ys,label='{}'.format(subj))

    plt.xlabel('$e_{i-norm}$')
    plt.ylabel('$P(X>e_{i-norm})$')
    plt.legend(prop={'size':6})

    plt.xscale('log')

    plt.tight_layout()

    plt.savefig('fig/eins-ccdf.png',dpi=300)
    logging.info('e_i-norm ccdf saved to fig/eins-ccdf.png.')


##画出各个领域的数据分析
def plot_field_year_num(pathObj):

    ## field_year_num
    _id_subjects,_id_cn,_id_doctype,_id_year,top10_doctypes = load_attrs(pathObj)
    top10_doctypes = ['Article','Review','Proceedings Paper','Letter','Book Review','Editorial Material']

    sciento_ids = set([l.strip() for l in open(pathObj._scientometrics_path)])


    ## 各个领域的论文数量随时间的变化
    field_year_num = defaultdict(lambda:defaultdict(int))
    ## 各个领域的文献总量
    field_num = defaultdict(int)
    ## 每篇论文的field数量分布
    fieldnum_dis = defaultdict(int)

    ## 领域内的各文献类型分布
    field_doctype_num = defaultdict(lambda:defaultdict(int))

    ## 各领域论文每年论文的平均被引用次数
    field_year_refnums = defaultdict(lambda:defaultdict(list))


    ## 统计论文的参考文献的数量
    pid_cits_path = pathObj.pid_cits_path

    logging.info("build cascade from {:} .".format(pid_cits_path))

    pid_refnum = defaultdict(int)
    progress = 0
    for line in open(pid_cits_path):

        progress+=1

        if progress%10000000==0:
            logging.info('reading %d citation relations....' % progress)

        line = line.strip()
        pid,citing_id = line.split("\t")

        pid_refnum[citing_id]+=1


    for pid in _id_subjects.keys():

        subjs = _id_subjects[pid]

        fieldnum = len(subjs)

        _year = int(_id_year[pid])

        fieldnum_dis[fieldnum]+=1

        doctype = _id_doctype[pid]


        for subj in subjs:

            field_year_num[subj][_year]+=1

            field_year_refnums[subj][_year].append(pid_refnum[pid])

            field_num[subj]+=1

            field_doctype_num[subj][doctype]+=1

        field_num['WOS_ALL']+=1

        field_year_num['WOS_ALL'][_year]+=1

        field_year_refnums['WOS_ALL'][_year].append(pid_refnum[pid])

        field_doctype_num['WOS_ALL'][doctype]+=1

        if pid in sciento_ids:
            field_year_num['SCIENTOMETRICS'][_year]+=1

            field_year_refnums['SCIENTOMETRICS'][_year].append(pid_refnum[pid])


    ## 画出field_year_refnum

    ## 画出上面的field_year_num,以及两个数据
    logging.info('plotting field year ref num png ...')
    plt.figure(figsize=(5,4))
    for subj in sorted(field_year_refnums.keys()):

        xs = []
        ys = []
        for year in sorted(field_year_refnums[subj].keys()):

            if year >2016:
                continue

            xs.append(year)
            ys.append(np.mean(field_year_refnums[subj][year]))

        plt.plot(xs,ys,label='{}'.format(subj))

    plt.xlabel("year")
    plt.ylabel('number of references')
    # plt.yscale('log')

    plt.legend(prop={'size':5})
    plt.tight_layout()

    plt.savefig('fig/field_year_refnum_dis.png',dpi=400)

    logging.info('fig saved to fig/field_year_refnum_dis.png.')




    ## 画出上面的field_year_num,以及两个数据
    logging.info('plotting field year num png ...')
    plt.figure(figsize=(5,4))
    for subj in sorted(field_year_num.keys()):

        xs = []
        ys = []
        for year in sorted(field_year_num[subj].keys()):

            if year >2016:
                continue

            xs.append(year)
            ys.append(field_year_num[subj][year])

        plt.plot(xs,ys,label='{}'.format(subj))

    plt.xlabel("year")
    plt.ylabel('number of publications')
    plt.yscale('log')

    plt.legend(prop={'size':5})
    plt.tight_layout()

    plt.savefig('fig/field_year_num_dis.png',dpi=400)

    logging.info('fig saved to fig/field_year_num_dis.png.')

    logging.info('start to print field num..')
    total =float(field_num['WOS_ALL'])
    print('Macro-level discipline,Number of publications (%)')
    for subj in sorted(field_num.keys()):

        line = '{},{}({:.2%})'.format(subj,field_num[subj],field_num[subj]/total)

        print(line)


    logging.info('start to print fieldnum dis ..')
    print('number of labels,number of publications')
    _5_p = 0
    for fieldnum in sorted(fieldnum_dis.keys()):

        if fieldnum<5:

            line = '{},{}({:.2%})'.format(fieldnum,fieldnum_dis[fieldnum],fieldnum_dis[fieldnum]/total)

            print line

        else:
            _5_p+=fieldnum


    line = '{},{}({:.2%})'.format(fieldnum,_5_p,_5_p/total)

    print line

    ## 各领域的doctype分布柱状图
    ## 每一个subj一个图

    print()
    logging.info('start to plot ..')
    plt.figure(figsize=(10,6))
    width = 0.1
    for i,subj in enumerate(sorted(field_doctype_num.keys())):

        ys = []
        for j,doctype in enumerate(top10_doctypes):

            num = field_doctype_num[subj][doctype]

            ys.append(num)

        xs = np.arange(len(top10_doctypes))+(i-3)*width

        plt.bar(xs,ys,width=width,label='{}'.format(subj))

    plt.xlabel('doctype')
    plt.xticks(np.arange(len(top10_doctypes)),top10_doctypes)

    plt.ylabel('number of publications')

    plt.yscale('log')

    plt.legend(prop={'size':6})


    plt.tight_layout()


    plt.savefig('fig/field_doctype_num_bar.png',dpi=400)

    logging.info('fig saved to fig/field_doctype_num_bar.png.')


## 统计性描述
def  stat_citation_dis(pathObj):
    _id_subjects,_id_cn,_id_doctype,_id_year,top10_doctypes = load_attrs(pathObj)
    top10_doctypes = ['Article','Review','Proceedings Paper','Letter','Book Review','Editorial Material']
    _id_dccp=json.loads(open(pathObj.dccp_path).read())
    sciento_ids = set([l.strip() for l in open('scientometrics.txt')])


    field_cn_dis = defaultdict(lambda:defaultdict(int))
    field_year_num = defaultdict(lambda:defaultdict(int))
    # field_num = defaultdict(int)
    # doctype_num = defaultdict(int)

    field_doctype_num = defaultdict(lambda:defaultdict(int))

    logging.info('stating id cn ....')
    for _id in _id_dccp.keys():
        _cn = int(_id_cn[_id])
        _year = int(_id_year[_id])
        _doctype = _id_doctype[_id]

        _top_subjects = _id_subjects[_id]

        for subj in _top_subjects:

            field_cn_dis[subj][_cn]+=1

            field_year_num[subj][_year]+=1

            # field_num[subj]+=1

            if _doctype in top10_doctypes:
                # doctype_num[_doctype]+=1
                field_doctype_num[subj][_doctype]+=1

            field_doctype_num[subj]['ALL']+=1


        field_cn_dis['WOS_ALL'][_cn]+=1
        field_year_num['WOS_ALL'][_year]+=1

        field_doctype_num['WOS_ALL']['ALL']+=1
        if _doctype in top10_doctypes:
            # doctype_num[_doctype]+=1
            field_doctype_num['WOS_ALL'][_doctype]+=1

        if _id in sciento_ids:
            field_cn_dis['SCIENTOMETRICS'][_cn]+=1
            field_year_num['SCIENTOMETRICS'][_year]+=1
            field_doctype_num['SCIENTOMETRICS']['ALL']+=1
            field_doctype_num['SCIENTOMETRICS'][_doctype]+=1

    ## 画出citation distribution
    plt.figure(figsize=(6,4))
    for i,subj in enumerate(sorted(field_cn_dis.keys())):

        cn_dis = field_cn_dis[subj]

        xs = []
        ys = []

        for _cn in sorted(cn_dis.keys(),key=lambda x:int(x)):

            xs.append(int(_cn))
            ys.append(cn_dis[_cn])

        xs,ys = cdf(xs,ys)

        plt.plot(xs,ys,label=subj)


    plt.xlabel('number of citations')
    plt.ylabel('probability')

    plt.xscale('log')
    plt.yscale('log')

    plt.title('CCDF')

    plt.legend()

    plt.tight_layout()

    plt.savefig('fig/field_cit_dis.png',dpi=400)
    logging.info('fig saved to fig/field_cit_dis.png')

    ## 画出year distribution
    plt.figure(figsize=(6,4))
    for i,subj in enumerate(sorted(field_year_num.keys())):

        year_num = field_year_num[subj]

        xs = []
        ys = []

        for _year in sorted(year_num.keys(),key=lambda x:int(x)):

            if int(_year)>2016:
                continue

            xs.append(int(_year))
            ys.append(year_num[_year])

        # xs,ys = cdf(xs,ys)

        plt.plot(xs,ys,label=subj)


    plt.xlabel('year')
    plt.ylabel('number of publications')

    plt.legend(prop={'size': 5},loc=2)

    # plt.xscale('log')
    plt.yscale('log')
    plt.tight_layout()
    plt.savefig('fig/field_year_num_dis.png',dpi=400)
    logging.info('fig saved to fig/field_year_num_dis.png')

    ## 各个学科的文章综述以及各类型文章的数量

    all_doctypes = ['ALL']
    all_doctypes.extend(top10_doctypes)
    logging.info('Subject doctype Num Dis')
    lines = ['field,{}'.format(','.join(all_doctypes))]
    for subj in sorted(field_doctype_num.keys()):

        line = [subj]
        for doctype in sorted(all_doctypes):

            num = field_doctype_num[subj].get(doctype,0)

            line.append(str(num))

        lines.append(','.join(line))

    open('data/field_doctype_num.csv','w').write('\n'.join(lines))
    logging.info('data saved to data/field_doctype_num.csv')



def stat_dccp(pathObj):

    _id_subjects,_id_cn,_id_doctype,_id_year,top10_doctypes = load_attrs(pathObj)

    top10_doctypes = ['Article','Review','Proceedings Paper','Letter','Book Review','Editorial Material']

    start_year = 1980
    end_year = 2016
    interval = 1
    logging.info('loading dccp data ...')
    _id_dccp=json.loads(open(pathObj.dccp_path).read())
    sciento_ids = set([l.strip() for l in open('scientometrics.txt')])
    # logging.info('loading paper subcascades  ...')
    # paper_size_id=json.loads(open(pathObj.paper_subcascades_path).read())
    dccp_depits(_id_dccp,start_year,end_year,_id_subjects,_id_cn,_id_doctype,_id_year,top10_doctypes,sciento_ids)
    logging.info('plotting')

def year_bin(year):
    return int((year-1900)/10)

# year_bins = ['1910','1920','1930','1940','1950','1960','19','1980','2000','2016']
def year_label(i):
    end = 1900+(i+1)*10

    if end>2016:
        end = 2016
    return '{:}-{:}'.format(1900+i*10,end)

def stat_subcascades(pathObj):
    _id_subjects,_id_cn,_id_doctype,_id_year,top10_doctypes = load_attrs(pathObj)
    start_year = 1900
    end_year = 2015
    interval = 1
    # logging.info('loading dccp data ...')
    logging.info('loading paper subcascades  ...')
    paper_size_id=json.loads(open(pathObj.paper_subcascades_path).read())

    ## scientometrics
    sciento_ids = set([l.strip() for l in open(pathObj._scientometrics_path)])

    logging.info('{} paper size dict loaded.'.format(len(paper_size_id)))
    ## 各个field对应的size以及num distribution
    field_size_dict = defaultdict(lambda:defaultdict(int))
    field_num_dict = defaultdict(lambda:defaultdict(int))
    field_doctype_size_dict = defaultdict(lambda:defaultdict(lambda:defaultdict(int)))
    field_year_size_dict = defaultdict(lambda:defaultdict(lambda:defaultdict(int)))
    field_yearb_size_dict = defaultdict(lambda:defaultdict(lambda:defaultdict(int)))


    field_cc_size_int = defaultdict(lambda:defaultdict(lambda:defaultdict(int)))
    field_cc_nums = defaultdict(lambda:defaultdict(list))


    field_doctype_num_dict = defaultdict(lambda:defaultdict(lambda:defaultdict(int)))
    field_year_num_dict = defaultdict(lambda:defaultdict(lambda:defaultdict(int)))

    ## field中不同citation count对应的subcascade的频次
    field_cnbin_subcascade = defaultdict(lambda:defaultdict(lambda:defaultdict(int)))

    ## doctype对应不同citation count的subcascade的频次
    doctype_cnbin_subcascade = defaultdict(lambda:defaultdict(lambda:defaultdict(int)))

    ## 每个领域对应时间的变化
    field_yearbin_subcascade = defaultdict(lambda:defaultdict(lambda:defaultdict(int)))

    ## 记录subcascade的DF
    # field_subcascade_df = defaultdict(lambda:defaultdict(list))
    ## 每一个field对应的文章数量
    # field_ccbin_num = defaultdict(lambda:defaultdict(int))


    progress =0

    for _id in paper_size_id.keys():
        _top_subjects,_cn_clas,_doctype,_year = stats_on_facets(_id,_id_subjects,_id_cn,_id_doctype,_id_year)

        cc = _id_cn[_id]

        _year_bin = year_bin(_year)
        _year_b = year_bin(_year)
        progress+=1

        if progress%1000000==0:
            logging.info('progress {}'.format(progress))

        size_id = paper_size_id[_id]
        ## 对每一篇论文所属的field进行统计
        for subj in _top_subjects:


            ## size
            num = 0
            all_ids = []
            for size in size_id.keys():
                ids = size_id[size]
                num+=len(ids)
                field_size_dict[subj][size]+=len(ids)

                field_year_size_dict[subj][_year_b][size]+=len(ids)

                field_yearb_size_dict[subj][_year][size]+=len(ids)

                field_doctype_size_dict[subj][_doctype][size]+=len(ids)

                field_cc_size_int[subj][cc][size]+=len(ids)

                all_ids.extend(ids)

            field_cc_nums[subj][cc].append(num)

            for _cc_ix,_cc_cl in enumerate(_cn_clas):
                if _cc_cl==1:
                    for sub_id in set(all_ids):

                        if sub_id==-999:
                            continue

                        field_cnbin_subcascade[subj][_cc_ix][sub_id]+=1

                        doctype_cnbin_subcascade[_doctype][_cc_ix][sub_id]+=1

                        field_yearbin_subcascade[subj][_year_bin][sub_id]+=1
                        # field_subcascade_df[subj][sub_id].append(_cc_ix)
                        # field_ccbin_num[subj][_cc_ix]+=1

            field_num_dict[subj][num]+=1

            field_year_num_dict[subj][_year_b][num]+=1
            field_doctype_num_dict[subj][_doctype][num]+=1
            # field_total_num[subj]+=1

        ## ALL
        subj = 'WOS_ALL'
        num = 0
        all_ids = []
        for size in size_id.keys():
            ids = size_id[size]
            num+=len(ids)
            field_size_dict[subj][size]+=len(ids)
            field_year_size_dict[subj][_year_b][size]+=len(ids)
            field_yearb_size_dict[subj][_year][size]+=len(ids)

            field_doctype_size_dict[subj][_doctype][size]+=len(ids)
            field_cc_size_int[subj][cc][size]+=len(ids)


            all_ids.extend(ids)

        field_cc_nums[subj][cc].append(num)


        for _cc_ix,_cc_cl in enumerate(_cn_clas):
            if _cc_cl==1:
                for sub_id in set(all_ids):

                    if sub_id==-999:
                        continue

                    field_cnbin_subcascade[subj][_cc_ix][sub_id]+=1
                    doctype_cnbin_subcascade[_doctype][_cc_ix][sub_id]+=1
                    field_yearbin_subcascade[subj][_year_bin][sub_id]+=1
                    # field_subcascade_df[subj][sub_id].append(_cc_ix)
                    # field_ccbin_num[subj][_cc_ix]+=1

        field_num_dict[subj][num]+=1
        field_year_num_dict[subj][_year_b][num]+=1
        field_doctype_num_dict[subj][_doctype][num]+=1
        ## SCIENTOMETRICS
        if _id in sciento_ids:
            subj = 'SCIENTOMETRICS'
            num = 0

            all_ids = []
            for size in size_id.keys():
                ids = size_id[size]
                num+=len(ids)
                field_size_dict[subj][size]+=len(ids)
                field_year_size_dict[subj][_year_b][size]+=len(ids)
                field_yearb_size_dict[subj][_year][size]+=len(ids)

                field_cc_size_int[subj][cc][size]+=len(ids)



                all_ids.extend(ids)

            field_cc_nums[subj][cc].append(num)


            for _cc_ix,_cc_cl in enumerate(_cn_clas):
                if _cc_cl==1:
                    for sub_id in set(all_ids):

                        if sub_id==-999:
                            continue

                        field_cnbin_subcascade[subj][_cc_ix][sub_id]+=1
                        doctype_cnbin_subcascade[_doctype][_cc_ix][sub_id]+=1
                        field_yearbin_subcascade[subj][_year_bin][sub_id]+=1
                        # field_subcascade_df[subj][sub_id].append(_cc_ix)
                        # field_ccbin_num[subj][_cc_ix]+=1

            field_num_dict[subj][num]+=1
            field_year_num_dict[subj][_year_b][num]+=1


    open('data/field_num_dict_all.json','w').write(json.dumps(field_num_dict))
    open('data/field_size_dict_all.json','w').write(json.dumps(field_size_dict))

    open('data/field_year_size_dict_all.json','w').write(json.dumps(field_year_size_dict))
    open('data/field_yearb_size_dict_all.json','w').write(json.dumps(field_yearb_size_dict))


    open('data/field_cc_size_dict_all.json','w').write(json.dumps(field_cc_size_int))

    open('data/field_cc_nums.json','w').write(json.dumps(field_cc_nums))

    open('data/field_doctype_size_dict_all.json','w').write(json.dumps(field_doctype_size_dict))

    open('data/field_year_num_dict_all.json','w').write(json.dumps(field_year_num_dict))
    open('data/field_doctype_num_dict_all.json','w').write(json.dumps(field_doctype_num_dict))

    ## ===
    open('data/field_cnbin_subcascade_all.json','w').write(json.dumps(field_cnbin_subcascade))
    open('data/field_yearbin_subcascade_all.json','w').write(json.dumps(field_yearbin_subcascade))
    open('data/doctype_cnbin_subcascade_all.json','w').write(json.dumps(doctype_cnbin_subcascade))
    # open('data/field_subcascade_df_all.json','w').write(json.dumps(field_subcascade_df))
    # open('data/field_ccbin_num_all.json','w').write(json.dumps(field_ccbin_num))

    logging.info("subcascade data saved.")


def cdf(xs,ys):
    total = np.sum(ys)
    cdf_xs = []
    cdf_ys = []
    for i,x in enumerate(xs):

        cd = np.sum(ys[i:])

        cdf = cd/float(total)

        cdf_xs.append(x)
        cdf_ys.append(cdf)

    return cdf_xs,cdf_ys

def plot_subcascade_data():
    top10_doctypes = ['Article','Review','Proceedings Paper','Letter','Book Review','Editorial Material']

    field_size_dict = json.loads(open('data/field_size_dict_all.json').read())
    fig,axes = plt.subplots(1,2,figsize=(13,4))
    ax = axes[0]
    for i,subj in enumerate(sorted(field_size_dict.keys())):

        xs = []
        ys = []

        # ax = axes[i/3,i%3]

        for size in sorted(field_size_dict[subj].keys(),key=lambda x:int(x)):

            xs.append(int(size))
            ys.append(field_size_dict[subj][size])

        xs,ys = cdf(xs,ys)
        # logging.info('subj {},xs:{},ys:{}'.format(subj,xs,ys))
        ax.plot(xs,ys,label='{}'.format(subj))

        ax.set_xlabel('size of subcascades')
        ax.set_ylabel('number of subcascades')

        ax.set_xscale('log')
        ax.set_yscale('log')

        # ax.set_title('{}'.format(subj))

    ax.legend(prop={'size':6})

        # lgd = ax.legend(loc=9,bbox_to_anchor=(-0.2, 0.5), ncol=1)

    # plt.tight_layout()

    # plt.savefig('fig/field_subcas_size_dis.png',dpi=400,additional_artists=[lgd],
    # bbox_inches="tight")
    # logging.info('Size distribution saved to fig/field_subcas_size_dis.png.')

    field_num_dict = json.loads(open('data/field_num_dict_all.json').read())
    ## 不同field对应的num distribution
    # fig,axes = plt.subplots(1,3,figsize=(12,3))
    ax = axes[1]
    for i,subj in enumerate(sorted(field_num_dict.keys())):

        xs = []
        ys = []

        # ax = axes[i/3,i%3]
        for num in sorted(field_num_dict[subj].keys(),key=lambda x:int(x)):

            xs.append(int(num))
            ys.append(field_num_dict[subj][num])

        # ax.plot(xs,ys,'o',fillstyle='none')
        xs,ys = cdf(xs,ys)
        ax.plot(xs,ys,label='{}'.format(subj))
        # logging.info('subj {},xs:{},ys:{}'.format(subj,xs,ys))
        ax.set_xlabel('number of components')
        ax.set_ylabel('number of papers')

        ax.set_xscale('log')
        ax.set_yscale('log')


        # ax.set_title('{}'.format(subj))
        # lgd = ax.legend(loc=9,bbox_to_anchor=(1.3, 0.8), ncol=1)
    ax.legend(prop={'size':6})


    plt.tight_layout()

    plt.savefig('fig/field_subcas_num_dis.png',dpi=400)
    logging.info('Size distribution saved to fig/field_subcas_num_dis.png.')


    field_year_size_dict = json.loads(open('data/field_year_size_dict_all.json').read())
    field_doctype_size_dict = json.loads(open('data/field_doctype_size_dict_all.json').read())

    field_year_num_dict = json.loads(open('data/field_year_num_dict_all.json').read())
    field_doctype_num_dict = json.loads(open('data/field_doctype_num_dict_all.json').read())




    ## 每一个subject两张图，分别对size和num随着doctype以及时间的变化进行描述
    fig,axes = plt.subplots(3,2,figsize=(10,12))
    for i,subj in enumerate(sorted(field_year_size_dict.keys())):


        year_size_dict = field_year_size_dict[subj]

        # if subj=='SCIENTOMETRICS':

        selected_years = [year for year in sorted(year_size_dict.keys(),key=lambda x:int(x)) if int(year)%2!=0]

        print subj,selected_years

        #     continue

        # ax = axes[i,0]
        ## 每一年的distribution
        for j,year in enumerate(selected_years):

            ax =axes[int(j/2),int(j%2)]

            year_l = year_label(int(year))


            xs = []
            ys = []
            for size in sorted(year_size_dict[year].keys(),key=lambda x:int(x)):

                xs.append(int(size))
                ys.append(year_size_dict[year][size])

            xs,ys = cdf(xs,ys)

            ax.plot(xs,ys,label=subj)

            ax.set_xlabel('size of subcascade')
            ax.set_ylabel('percentage')
            ax.set_xscale('log')
            ax.set_yscale('log')
            ax.set_title('{}'.format(year_l))

        # ax.text(0,0,'{}'.format(subj))

            ax.legend(prop={'size':6})

    plt.tight_layout()

    plt.savefig('fig/year_size_dis.png',dpi=400)
    logging.info('saved to fig/year_size_dis.png.')


    fig,axes = plt.subplots(3,2,figsize=(10,12))
    for i,subj in enumerate(sorted(field_year_num_dict.keys())):

        year_num_dict = field_year_num_dict[subj]

        selected_years = [year for year in sorted(year_num_dict.keys(),key=lambda x:int(x)) if int(year)%2!=0]

        # ax = axes[i,1]
        ## 每一年的distribution
        for j,year in enumerate(selected_years):

            ax =axes[j/2,j%2]

            year_l = year_label(int(year))
            xs = []
            ys = []
            for size in sorted(year_num_dict[year].keys(),key=lambda x:int(x)):

                xs.append(int(size))
                ys.append(year_num_dict[year][size])

            xs,ys = cdf(xs,ys)

            ax.plot(xs,ys,label=subj)

            ax.set_xlabel('number of components')
            ax.set_ylabel('percentage')
            ax.set_xscale('log')
            ax.set_yscale('log')
            ax.set_title('{}'.format(year_l))
            ax.legend(prop={'size':6})

            # ax.legend(prop={'size':6})

    plt.tight_layout()

    plt.savefig('fig/year_num_dis.png',dpi=400)
    logging.info('saved to fig/year_num_dis.png.')


    # fig,axes = plt.subplots(2,4,figsize=(20,8))

    field_yearb_size_dict = json.loads(open('data/field_yearb_size_dict_all.json').read())

    fieldnum_xsys = {}

    plt.figure(figsize=(5,4))
    for i,subj in enumerate(sorted(field_yearb_size_dict.keys())):

        year_num_dict = field_yearb_size_dict[subj]

        ## 每一年的distribution
        # ax =axes[i/4,i%4]
        xs = []
        ys = []
        num_ys = []
        for j,year in enumerate(sorted(year_num_dict.keys(),key=lambda x:int(x))):

            xs.append(int(year))
            y = []
            num = 0
            for size in sorted(year_num_dict[year].keys(),key=lambda x:int(x)):

                y.extend([int(size)]*year_num_dict[year][size])

                num+=year_num_dict[year][size]

            num_ys.append(num)

            ys.append(np.mean(y))

        fieldnum_xsys[subj]=[xs,ys]

        ys = [np.mean(ys[:i+1]) for i in range(len(ys))]

        # print('moving average')

        plt.plot(xs,ys,label=subj)

    plt.xlabel('year')
    plt.ylabel('size of components')
    plt.legend(prop={'size':6})

    plt.tight_layout()

    plt.savefig('fig/field_year_size_dis.png',dpi=400)
    logging.info('saved to fig/field_year_size_dis.png.')


    plt.figure(figsize=(5,4))

    for field in sorted(fieldnum_xsys.keys()):

        xs,ys = fieldnum_xsys[field]

        ys = [np.mean(ys[:i+1]) for i in range(len(ys))]

        plt.plot(xs,ys,label='{}'.format(field))

    plt.xlabel('year')
    plt.ylabel('number of components')
    plt.legend(prop={'size':6})

    plt.tight_layout()

    plt.savefig('fig/field_year_num_cas_dis.png',dpi=400)
    logging.info('saved to fig/field_year_num_cas_dis.png.')



    ## field cc size int
    field_cc_size_int = json.loads(open('data/field_cc_size_dict_all.json').read())

    field_cc_nums = json.loads(open('data/field_cc_nums.json').read())

    field_CLS_size = defaultdict(lambda:defaultdict(list))

    field_cc_size = defaultdict(lambda:defaultdict(list))


    field_CLS_num = defaultdict(lambda:defaultdict(list))
    field_cc_num = defaultdict(lambda:defaultdict(list))
    ##
    MAXMIN,MINMAX = minmax_maxmin()

    for field in sorted(field_cc_size_int.keys()):

        for cc in sorted(field_cc_size_int[field].keys(),key = lambda x:int(x)):

            # cc = int(cc)

            if int(cc)<MAXMIN:
                CLS = 0
            elif int(cc)<MINMAX:
                CLS = 1
            else:
                CLS = 2

            y = []
            # nums = []
            for size in field_cc_size_int[field][cc].keys():

                y.extend([int(size)]*field_cc_size_int[field][cc][size])

                # nums.append(field_cc_size_int[field][cc][size])

            nums = field_cc_nums[field][cc]

            field_CLS_num[field][CLS].append(np.mean(nums))
            field_cc_num[field][int(cc)].append(np.mean(nums))


            field_CLS_size[field][CLS].extend(y)
            field_cc_size[field][int(cc)].extend(y)

    lines = ['Displines=Citation impact=Max=Avg=Median=Gini']

    for field in sorted(field_CLS_size.keys()):

        for CLS in sorted(field_CLS_size[field].keys()):

            data = field_CLS_size[field][CLS]

            if CLS ==0:
                TAG = 'L'
            elif CLS ==1:
                TAG = 'M'
            else:
                TAG = 'H'

            max_ = np.max(data)
            mean = np.mean(data)
            median = np.median(data)
            gini_score = gini(np.array([float(d) for d in data]))

            line = '{}={}={}={}={}={}'.format(field,TAG,max_,mean,median,gini_score)

            lines.append(line)

    open('data/field_CLS_table.csv','w').write('\n'.join(lines))
    logging.info('data saved to data/field_CLS_table.csv.')


    ## hua

    fig,axes = plt.subplots(2,4,figsize=(26,8))
    for i,subj in enumerate(sorted(field_CLS_size.keys())):
        logging.info('field {} ...'.format(subj))
        data = []
        for CLS in sorted(field_CLS_size[subj].keys()):
            logging.info('CLS:{}'.format(CLS))
            # logging.info('num of dccps:{}'.format())
            data.append(field_CLS_size[subj][CLS])

        print('length of data {}'.format(len(data)))

        ax = axes[i/4,i%4]

        ax.boxplot(data,labels=['lowly cited','medium cited','highly cited'],showfliers=True)

        ax.set_xlabel('Paper Impact Level')
        ax.set_ylabel('size of components')
        ax.set_yscale('log')
        ax.set_title('{}'.format(subj))

    plt.tight_layout()

    plt.savefig('fig/boxplot_size_wos_all.png',dpi=300)

    logging.info('fig saved to fig/boxplot_size_wos_all.png.')

    fig,axes = plt.subplots(2,4,figsize=(26,8))
    for i,subj in enumerate(sorted(field_CLS_num.keys())):
        logging.info('field {} ...'.format(subj))
        data = []
        for CLS in sorted(field_CLS_num[subj].keys()):
            logging.info('CLS:{}'.format(CLS))
            # logging.info('num of dccps:{}'.format())
            data.append(field_CLS_num[subj][CLS])

        print('length of data {}'.format(len(data)))

        ax = axes[i/4,i%4]

        ax.boxplot(data,labels=['lowly cited','medium cited','highly cited'],showfliers=True)

        ax.set_xlabel('Paper Impact Level')
        ax.set_ylabel('number of components')
        ax.set_yscale('log')
        ax.set_title('{}'.format(subj))

    plt.tight_layout()

    plt.savefig('fig/boxplot_num_wos_all.png',dpi=300)

    logging.info('fig saved to fig/boxplot_num_wos_all.png.')

    # fig,axes = plt.subplots(2,4,figsize=(20,8))
    plt.figure(figsize=(5,4))
    for i,subj in enumerate(sorted(field_cc_size.keys())):
        logging.info('field {} ...'.format(subj))
        # data = []
        xs = []
        ys = []
        for cc in sorted(field_cc_size[subj].keys()):
            # logging.info('cc:{}'.format(cc))
            # logging.info('num of dccps:{}'.format())
            # data.append(field_cc_size[subj][cc])

            xs.append(cc)
            ys.append(np.mean(field_cc_size[subj][cc]))

        ys = [ np.mean(ys[:i+1]) for i in range(len(ys))]

        # print('length of data {}'.format(len(data)))

        # ax = axes[i/4,i%4]
        plt.plot(xs,ys,label='{}'.format(subj))

        # ax.boxplot(data,labels=['lowly-cited','medium-cited','highly-cited'],showfliers=True)

    plt.xlabel('number of citations')
    plt.ylabel('size of components')
    plt.yscale('log')
    plt.xscale('log')

    plt.legend(prop={'size':6})


    plt.tight_layout()

    plt.savefig('fig/field_cc_size.png',dpi=300)

    logging.info('fig saved to fig/field_cc_size.png.')


    plt.figure(figsize=(5,4))
    for i,subj in enumerate(sorted(field_cc_num.keys())):
        logging.info('field {} ...'.format(subj))
        # data = []
        xs = []
        ys = []
        for cc in sorted(field_cc_num[subj].keys()):
            # logging.info('cc:{}'.format(cc))
            # logging.info('num of dccps:{}'.format())
            # data.append(field_cc_num[subj][cc])

            xs.append(cc)
            ys.append(np.mean(field_cc_num[subj][cc]))

        ys = [ np.mean(ys[:i+1]) for i in range(len(ys))]

        # print('length of data {}'.format(len(data)))

        # ax = axes[i/4,i%4]
        plt.plot(xs,ys,label='{}'.format(subj))

        # ax.boxplot(data,labels=['lowly-cited','medium-cited','highly-cited'],showfliers=True)

    plt.xlabel('number of citations')
    plt.ylabel('number of components')
    plt.yscale('log')
    plt.xscale('log')

    # plt.legend(prop={'size':6})
    lgd = plt.legend(loc=9,bbox_to_anchor=(0.5, -0.15), ncol=2)



    plt.tight_layout()

    plt.savefig('fig/field_cc_num_cas.png',dpi=300,additional_artists=[lgd])

    logging.info('fig saved to fig/field_cc_num_cas.png.')



    fig,axes = plt.subplots(3,2,figsize=(10,12))
    for i,subj in enumerate(sorted(field_doctype_size_dict.keys())):

        doctype_size_dict = field_doctype_size_dict[subj]

        ## 每一年的distribution
        for j,doctype in enumerate(sorted(top10_doctypes)):

            ax =axes[int(j/2),int(j%2)]


            xs = []
            ys = []
            for size in sorted(doctype_size_dict[doctype].keys(),key=lambda x:int(x)):

                xs.append(int(size))
                ys.append(doctype_size_dict[doctype][size])

            xs,ys = cdf(xs,ys)

            ax.plot(xs,ys,label=subj)

            ax.set_xlabel('size of subcascade')
            ax.set_ylabel('percentage')
            ax.set_xscale('log')
            ax.set_yscale('log')
            ax.set_title('{}'.format(doctype))
            ax.legend(prop={'size':6})

    plt.tight_layout()

    plt.savefig('fig/doctype_size_dis.png',dpi=400)
    logging.info('saved to fig/doctype_size_dis.png.')


    fig,axes = plt.subplots(3,2,figsize=(10,12))
    for i,subj in enumerate(sorted(field_doctype_num_dict.keys())):
        ## 每一年的distribution
        doctype_num_dict = field_doctype_num_dict[subj]
        for j,doctype in enumerate(sorted(top10_doctypes)):
            ax =axes[int(j/2),int(j%2)]

            xs = []
            ys = []
            for size in sorted(doctype_num_dict[doctype].keys(),key=lambda x:int(x)):

                xs.append(int(size))
                ys.append(doctype_num_dict[doctype][size])

            xs,ys = cdf(xs,ys)

            ax.plot(xs,ys,label=subj)

            ax.set_xlabel('number of components')
            ax.set_ylabel('percentage')
            ax.set_xscale('log')
            ax.set_yscale('log')
            ax.set_title('{}'.format(doctype))
            ax.legend(prop={'size':6})

    plt.tight_layout()

    plt.savefig('fig/doctype_num_dis.png',dpi=400)
    logging.info('saved to fig/doctype_num_dis.png.')

    # return

def output_motif_table():
    ## ===
    field_cnbin_subcascade = json.loads(open('data/field_cnbin_subcascade_all.json').read())

    field_yearbin_subcascade = json.loads(open('data/field_yearbin_subcascade_all.json').read())

    doctype_cnbin_subcascade = json.loads(open('data/doctype_cnbin_subcascade_all.json').read())

    # field_subcascade_df = json.loads(open('data/field_subcascade_df_all.json').read())
    field_ccbin_num = json.loads(open('data/field_ccbin_num_all.json').read())

    ## 不同field中不同ccbin对应的common motif,以tf/df进行排序，找出个ccbin对应的独特的motif
    subj_ccbin_motif_dict = defaultdict(lambda:defaultdict(dict))
    for subj in sorted(field_cnbin_subcascade.keys()):
        # subcas_df = field_subcascade_df[subj]
        # logging.info("subj of subcascade {},length of subcascade {}".format(subj,len(subcas_df)))

        for cc_bin in sorted(field_cnbin_subcascade[subj].keys()):

            subcas_num_dict = field_cnbin_subcascade[subj][cc_bin]

            # subcas_num_total = field_ccbin_num[subj][cc_bin]

            motif_dict = defaultdict(dict)

            for sub_id in subcas_num_dict.keys():

                # df = len(set(subcas_df[sub_id]))

                tf = subcas_num_dict[sub_id]

                # norm_tf = tf/float(subcas_num_total)

                # tfidf = norm_tf*(np.log(len(labels)/df))

                motif_dict[sub_id]['tf'] = tf
                # motif_dict[sub_id]['norm_tf'] = norm_tf
                # motif_dict[sub_id]['tfidf'] = tfidf

            ## 对于改bin下的top motif进行输出
            subj_ccbin_motif_dict[subj][cc_bin]= motif_dict

    ## 分别对每一个subject下不同的ccbin的motif进行计算
    lines = ['## Subject vs. Citation Count\n']
    for subj in sorted(subj_ccbin_motif_dict.keys()):
        line = '#### Subject:{}'.format(subj)
        header = "|"+'|'.join(['0']*17)+"|"
        pos = "|"+'|'.join([':--------:']*17)+"|"
        lines.append(line)
        lines.append(header)
        lines.append(pos)
        ccbin_motif_dict = subj_ccbin_motif_dict[subj]
        cc_lines = []
        for ccbin in sorted(ccbin_motif_dict.keys()):
            motif_dict = ccbin_motif_dict[ccbin]
            # print motif_dict
            cc_line = ['{}|'.format(labels[int(ccbin)])]
            cc_line.append('subcascade|tf')

            _10_line = []
            for ix,motif in enumerate(sorted(motif_dict.keys(),key = lambda x:motif_dict[x]['tf'],reverse=True)[:10]):
                tf = motif_dict[motif]['tf']
                # tfidf = motif_dict[motif]['tfidf']
                line = '![subcascade](subcascade/fig/subcas_{:}.jpg)|{}'.format(motif,tf)
                # print line
                _10_line.append(line)

            if len(_10_line)!=10:

                _10_line.extend(['|']*(10-len(_10_line)))

            cc_line.extend(_10_line)
            cc_lines.append(cc_line)

        # print cc_lines[0]

        for ix,line in enumerate(zip(*cc_lines)):
            # print line

            if line[0].startswith('!'):
                ix = ix-1
            else:
                ix = 0

            line= "|{}|".format(ix)+'|'.join(line)+"|"
            print line
            lines.append(line)

    f = open("README.md",'w')

    f.write('\n'.join(lines)+'\n')

    ### doctype bin
    ## 不同field中不同ccbin对应的common motif,以tf/df进行排序，找出个ccbin对应的独特的motif
    doctype_ccbin_motif_dict = defaultdict(lambda:defaultdict(dict))
    for subj in sorted(doctype_cnbin_subcascade.keys()):
        # subcas_df = field_subcascade_df[subj]
        # logging.info("subj of subcascade {},length of subcascade {}".format(subj,len(subcas_df)))

        for cc_bin in sorted(doctype_cnbin_subcascade[subj].keys()):

            subcas_num_dict = doctype_cnbin_subcascade[subj][cc_bin]

            # subcas_num_total = field_ccbin_num[subj][cc_bin]

            motif_dict = defaultdict(dict)

            for sub_id in subcas_num_dict.keys():

                # df = len(set(subcas_df[sub_id]))

                tf = subcas_num_dict[sub_id]

                # norm_tf = tf/float(subcas_num_total)

                # tfidf = norm_tf*(np.log(len(labels)/df))

                motif_dict[sub_id]['tf'] = tf
                # motif_dict[sub_id]['norm_tf'] = norm_tf
                # motif_dict[sub_id]['tfidf'] = tfidf

            ## 对于改bin下的top motif进行输出
            doctype_ccbin_motif_dict[subj][cc_bin]= motif_dict

    ## 分别对每一个subject下不同的ccbin的motif进行计算
    lines = ['## Doctype vs. Citation Count\n']
    top10_doctypes = ['Article','Review','Proceedings Paper','Letter','Book Review','Editorial Material']
    for subj in sorted(top10_doctypes):
        line = '#### Doctype:{}'.format(subj)
        header = "|"+'|'.join(['0']*17)+"|"
        pos = "|"+'|'.join([':--------:']*17)+"|"
        lines.append(line)
        lines.append(header)
        lines.append(pos)
        ccbin_motif_dict = doctype_ccbin_motif_dict[subj]
        cc_lines = []
        for ccbin in sorted(ccbin_motif_dict.keys()):
            motif_dict = ccbin_motif_dict[ccbin]
            # print motif_dict
            cc_line = ['{}|'.format(labels[int(ccbin)])]
            cc_line.append('subcascade|tf')

            _10_line = []
            for ix,motif in enumerate(sorted(motif_dict.keys(),key = lambda x:motif_dict[x]['tf'],reverse=True)[:10]):
                tf = motif_dict[motif]['tf']
                # tfidf = motif_dict[motif]['tfidf']
                line = '![subcascade](subcascade/fig/subcas_{:}.jpg)|{}'.format(motif,tf)
                # print line
                # cc_line.append(line)
                _10_line.append(line)

            if len(_10_line)!=10:
                _10_line.extend(['|']*(10-len(_10_line)))

            cc_line.extend(_10_line)
            cc_lines.append(cc_line)

        # print cc_lines[0]

        for ix,line in enumerate(zip(*cc_lines)):
            # print line

            if line[0].startswith('!'):
                ix = ix-1
            else:
                ix = 0

            line= "|{}|".format(ix)+'|'.join(line)+"|"
            print line
            lines.append(line)

    f.write('\n'.join(lines)+'\n')


    ## subject yearbin
    ## 不同field中不同ccbin对应的common motif,以tf/df进行排序，找出个ccbin对应的独特的motif
    subj_yearbin_motif_dict = defaultdict(lambda:defaultdict(dict))
    for subj in sorted(field_yearbin_subcascade.keys()):
        # subcas_df = field_subcascade_df[subj]
        # logging.info("subj of subcascade {},length of subcascade {}".format(subj,len(subcas_df)))

        for year_bin in sorted(field_yearbin_subcascade[subj].keys()):

            subcas_num_dict = field_yearbin_subcascade[subj][year_bin]

            # subcas_num_total = field_ccbin_num[subj][cc_bin]

            motif_dict = defaultdict(dict)

            for sub_id in subcas_num_dict.keys():

                # df = len(set(subcas_df[sub_id]))

                tf = subcas_num_dict[sub_id]

                # norm_tf = tf/float(subcas_num_total)

                # tfidf = norm_tf*(np.log(len(labels)/df))

                motif_dict[sub_id]['tf'] = tf
                # motif_dict[sub_id]['norm_tf'] = norm_tf
                # motif_dict[sub_id]['tfidf'] = tfidf

            ## 对于改bin下的top motif进行输出
            subj_yearbin_motif_dict[subj][year_bin]= motif_dict

    ## 分别对每一个subject下不同的ccbin的motif进行计算
    lines = ['## Subject vs. Year\n']
    for subj in sorted(subj_yearbin_motif_dict.keys()):
        line = '#### Subject:{}'.format(subj)
        header = "|"+'|'.join(['0']*25)+"|"
        pos = "|"+'|'.join([':--------:']*25)+"|"
        lines.append(line)
        lines.append(header)
        lines.append(pos)
        yearbin_motif_dict = subj_yearbin_motif_dict[subj]
        cc_lines = []
        for yearbin in sorted(yearbin_motif_dict.keys(),key=lambda x:int(x)):
            motif_dict = yearbin_motif_dict[yearbin]
            # print motif_dict
            cc_line = ['{}|'.format(year_label(int(yearbin)))]
            cc_line.append('subcascade|tf')

            _10_line = []
            for ix,motif in enumerate(sorted(motif_dict.keys(),key = lambda x:motif_dict[x]['tf'],reverse=True)[:10]):
                tf = motif_dict[motif]['tf']
                # tfidf = motif_dict[motif]['tfidf']
                line = '![subcascade](subcascade/fig/subcas_{:}.jpg)|{}'.format(motif,tf)
                # print line
                _10_line.append(line)

            if len(_10_line)!=10:

                _10_line.extend(['|']*(10-len(_10_line)))

            cc_line.extend(_10_line)
            cc_lines.append(cc_line)

        # print cc_lines[0]

        for ix,line in enumerate(zip(*cc_lines)):
            # print line

            if line[0].startswith('!'):
                ix = ix-1
            else:
                ix = 0

            line= "|{}|".format(ix)+'|'.join(line)+"|"
            print line
            lines.append(line)

    # f = open("README.md",'w')

    f.write('\n'.join(lines)+'\n')

    logging.info('saved to README.md')



def minmax_maxmin():

    id_num = json.loads(open('data/paper_cit_num_ALL.json').read())

    total = len(id_num)
    logging.info('number of papers {}.'.format(total))

    citnums = sorted(id_num.values(),reverse=True)

    maxmin_index = int(total/2)

    minmax_index = int(total*0.05)

    maxmin = citnums[maxmin_index]
    minmax = citnums[minmax_index]

    logging.info('maxmin:{}, minmax:{}'.format(maxmin,minmax))

    return maxmin,minmax




if __name__ == '__main__':

    field = 'ALL'
    paths = PATHS(field)
    # parse_args(paths)
    # run_all(paths)
    # dccp_of_paper(paths)
    stat_dccp(paths)
    # boxplot()
    # plot_dccps()

    # stat_subcascades(paths)
    # plot_subcascade_data()
    # output_motif_table()

    # logging.info('Done')

    # stat_citation_dis(paths)


    # plot_field_year_num(paths)

