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

    ## 领域 时间 dccps
    field_year_dccps = defaultdict(lambda:defaultdict(list))
    field_year_eins = defaultdict(lambda:defaultdict(list))

    ## 领域 doctype dccps
    field_doctype_dccps = defaultdict(lambda:defaultdict(list))
    field_doctype_eins = defaultdict(lambda:defaultdict(list))

    logging.info('startting to stat dccp ...')
    for _id in _id_dccp.keys():
        ## 获得这一篇论文的基础属性值
        _cn = int(_id_cn[_id])
        _top_sujects,_cn_clas,_doctype,_year = stats_on_facets(_id,_id_subjects,_id_cn,_id_doctype,_id_year)

        ## 过滤时间
        if int(_year)>end_year:
            continue

        for subj in _top_sujects:

            field_cc_dccps[subj][_cn].append(_id_dccp[_id][0])
            for cc_ix,_cc_cl in enumerate(_cn_clas):
                if _cc_cl==1:
                    field_ccbin_eins[subj][cc_ix].append(_id_dccp[_id][1]/float(_cn))

            field_year_dccps[subj][_year].append(_id_dccp[_id][0])
            field_year_eins[subj][_year].append(_id_dccp[_id][1]/float(_cn))

            field_doctype_dccps[subj][_doctype].append(_id_dccp[_id][0])
            field_doctype_eins[subj][_doctype].append(_id_dccp[_id][1]/float(_cn))

        field_doctype_dccps['WOS_ALL'][_doctype].append(_id_dccp[_id][0])
        field_doctype_eins['WOS_ALL'][_doctype].append(_id_dccp[_id][1]/float(_cn))

        field_year_dccps['WOS_ALL'][_year].append(_id_dccp[_id][0])
        field_year_eins['WOS_ALL'][_year].append(_id_dccp[_id][1]/float(_cn))

        field_cc_dccps['WOS_ALL'][_cn].append(_id_dccp[_id][0])
        for cc_ix,_cc_cl in enumerate(_cn_clas):
            if _cc_cl==1:
                field_ccbin_eins['WOS_ALL'][cc_ix].append(_id_dccp[_id][1]/float(_cn))

        if _id in SCIENTO_IDS:

            field_doctype_dccps['SCIENTOMETRICS'][_doctype].append(_id_dccp[_id][0])
            field_doctype_eins['SCIENTOMETRICS'][_doctype].append(_id_dccp[_id][1]/float(_cn))

            field_year_dccps['SCIENTOMETRICS'][_year].append(_id_dccp[_id][0])
            field_year_eins['SCIENTOMETRICS'][_year].append(_id_dccp[_id][1]/float(_cn))

            field_cc_dccps['SCIENTOMETRICS'][_cn].append(_id_dccp[_id][0])
            for cc_ix,_cc_cl in enumerate(_cn_clas):
                if _cc_cl==1:
                    field_ccbin_eins['SCIENTOMETRICS'][cc_ix].append(_id_dccp[_id][1]/float(_cn))


    open('data/field_cc_dccps.json','w').write(json.dumps(field_cc_dccps))
    open('data/field_ccbin_eins.json','w').write(json.dumps(field_ccbin_eins))
    open('data/field_year_dccps.json','w').write(json.dumps(field_year_dccps))
    open('data/field_year_eins.json','w').write(json.dumps(field_year_eins))
    open('data/field_doctype_dccps.json','w').write(json.dumps(field_doctype_dccps))
    open('data/field_doctype_eins.json','w').write(json.dumps(field_doctype_eins))

    logging.info('data saved.')

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
        for cc in sorted(field_cc_dccps[field].keys()):
            dccps  = field_cc_dccps[field][cc]
            ## dccp 在这个的比例
            p_of_dccp = np.sum(dccps)/float(len(dccps))

            xs.append(cc)
            ys.append(p_of_dccp)

        ax.plot(xs,ys,label='{}'.format(field),marker=markers[fi])
        ax.set_xscale('log')

        ax.set_xlabel('number of citations')
        ax.set_ylabel('$p$')
        ax.set_xlim(1,1000)
        lgd = ax.legend(loc=9,bbox_to_anchor=(0.5, -0.1), ncol=2)

        ## dccp与doctype的关系
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

        width = 0.24
        bi = fi-4
        if bi>=0:
            bi+=1
        bias = bi*width/8
        ax1.bar(np.arange(len(top10_doctypes))+bias,ys,label='{}'.format(field))

        ax1.set_xticks(range(len(top10_doctypes)))
        ax1.set_xticklabels(top10_doctypes,rotation=-90)
        ax1.set_xlabel('Doctype')
        ax1.set_ylabel('$p$')


        ax1.legend()

        ## dccp与时间之间的关系
        ax2 = axes[1]
        xs = []
        ys = []
        for year in sorted(field_year_dccps[field].keys()):
            dccps = field_year_dccps[field][year]
            ## dccp 在这个的比例
            p_of_dccp = np.sum(dccps)/float(len(dccps))

            xs.append(year)
            ys.append(p_of_dccp)
        ax2.plot(xs,ys,label='{}'.format(field),marker=markers[fi])

        ax2.set_xlabel('Year')
        ax2.set_ylabel('$p$')

        # ax2.legend()

    plt.tight_layout()
    plt.savefig('fig/dccp_total.png',dpi=300,additional_artists=[lgd],
    bbox_inches="tight")


    fig,axes = plt.subplots(1,3,figsize=(18,5))
    ## 分不同的领域查看ein随着citation count, doctype, 时间之间的变化
    for fi,field in enumerate(sorted(field_ccbin_eins.keys())):

        ## dccp随着citation count的变化
        ax = axes[0]
        xs = []
        ys = []
        for cc in sorted(field_ccbin_eins[field].keys()):
            dccps  = field_ccbin_eins[field][cc]
            ## dccp 在这个的比例
            p_of_dccp = np.mean(dccps)

            xs.append(cc)
            ys.append(p_of_dccp)

        ax.plot(xs,ys,label='{}'.format(field),marker=markers[fi])
        # ax.set_xscale('log')
        ax.set_xticks(xs)
        ax.set_xticklabels(labels)

        ax.set_xlabel('number of citations')
        ax.set_ylabel('$e_{i-norm}$')
        lgd = ax.legend(loc=9,bbox_to_anchor=(0.5, -0.1), ncol=2)

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

        width = 0.24
        bi = fi-4
        if bi>=0:
            bi+=1
        bias = bi*width/8
        ax1.bar(np.arange(len(top10_doctypes))+bias,ys,label='{}'.format(field))

        ax1.set_xticks(range(len(top10_doctypes)))
        ax1.set_xticklabels(top10_doctypes,rotation=-90)
        ax1.set_xlabel('Doctype')
        ax1.set_ylabel('$e_{i-norm}$')


        ax1.legend()

        ## dccp与时间之间的关系
        ax2 = axes[1]
        xs = []
        ys = []
        for year in sorted(field_year_eins[field].keys()):
            dccps = field_year_eins[field][year]
            ## dccp 在这个的比例
            p_of_dccp = np.sum(dccps)/float(len(dccps))

            xs.append(year)
            ys.append(p_of_dccp)
        ax2.plot(xs,ys,label='{}'.format(field),marker=markers[fi])

        ax2.set_xlabel('Year')
        ax2.set_ylabel('$e_{i-norm}$')

        # ax2.legend()

    plt.tight_layout()
    plt.savefig('fig/eins_total.png',dpi=300,additional_artists=[lgd],
    bbox_inches="tight")

    logging.info('Done')


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

def stat_subcascades(pathObj):
    _id_subjects,_id_cn,_id_doctype,_id_year,top10_doctypes = load_attrs(pathObj)
    start_year = 1900
    end_year = 2015
    interval = 1
    # logging.info('loading dccp data ...')
    logging.info('loading paper subcascades  ...')
    paper_size_id=json.loads(open(pathObj.paper_subcascades_path).read())

    logging.info('{} paper size dict loaded.'.format(len(paper_size_id)))
    ## 各个field对应的size以及num distribution
    field_size_dict = defaultdict(lambda:defaultdict(int))
    field_num_dict = defaultdict(lambda:defaultdict(int))
    ## field中不同citation count对应的subcascade的频次
    field_cnbin_subcascade = defaultdict(lambda:defaultdict(lambda:defaultdict(int)))
    ## 记录subcascade的DF
    field_subcascade_df = defaultdict(lambda:defaultdict(list))
    ## 每一个field对应的文章数量
    field_ccbin_num = defaultdict(lambda:defaultdict(int))

    progress =0

    for _id in paper_size_id.keys():
        _top_subjects,_cn_clas,_doctype,_year = stats_on_facets(_id,_id_subjects,_id_cn,_id_doctype,_id_year)

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

                all_ids.extend(ids)

            for _cc_ix,_cc_cl in enumerate(_cn_clas):
                if _cc_cl==1:
                    for sub_id in set(all_ids):

                        if sub_id==-999:
                            continue

                        field_cnbin_subcascade[subj][_cc_ix][sub_id]+=1
                        field_subcascade_df[subj][sub_id].append(_cc_ix)
                        field_ccbin_num[subj][_cc_ix]+=1

            field_num_dict[subj][num]+=1
            # field_total_num[subj]+=1

    open('data/field_num_dict_all.json','w').write(json.dumps(field_num_dict))
    open('data/field_size_dict_all.json','w').write(json.dumps(field_size_dict))

    ## ===
    open('data/field_cnbin_subcascade_all.json','w').write(json.dumps(field_cnbin_subcascade))
    open('data/field_subcascade_df_all.json','w').write(json.dumps(field_subcascade_df))
    open('data/field_ccbin_num_all.json','w').write(json.dumps(field_ccbin_num))

    logging.info("subcascade data saved.")

def plot_subcascade_data():

    field_size_dict = json.loads(open('data/field_size_dict_all.json').read())
    fig,axes = plt.subplots(2,3,figsize=(12,6))

    for i,subj in enumerate(sorted(field_size_dict.keys())):

        xs = []
        ys = []

        ax = axes[i/3,i%3]

        for size in sorted(field_size_dict[subj].keys(),key=lambda x:int(x)):

            xs.append(int(size))
            ys.append(field_size_dict[subj][size])

        # logging.info('subj {},xs:{},ys:{}'.format(subj,xs,ys))
        ax.plot(xs,ys,'o',fillstyle='none')

        ax.set_xlabel('size of subcascade')
        ax.set_ylabel('number of subcascade')

        ax.set_xscale('log')
        ax.set_yscale('log')

        ax.set_title('{}'.format(subj))

    plt.tight_layout()

    plt.savefig('fig/field_subcas_size_dis.png',dpi=400)
    logging.info('Size distribution saved to fig/field_subcas_size_dis.png.')

    field_num_dict = json.loads(open('data/field_num_dict_all.json').read())
    ## 不同field对应的num distribution
    fig,axes = plt.subplots(2,3,figsize=(12,6))

    for i,subj in enumerate(sorted(field_num_dict.keys())):

        xs = []
        ys = []

        ax = axes[i/3,i%3]
        for num in sorted(field_num_dict[subj].keys(),key=lambda x:int(x)):

            xs.append(int(num))
            ys.append(field_num_dict[subj][num])

        ax.plot(xs,ys,'o',fillstyle='none')
        # logging.info('subj {},xs:{},ys:{}'.format(subj,xs,ys))
        ax.set_xlabel('number of components')
        ax.set_ylabel('number of papers')

        ax.set_xscale('log')
        ax.set_yscale('log')

        ax.set_title('{}'.format(subj))

    plt.tight_layout()

    plt.savefig('fig/field_subcas_num_dis.png',dpi=400)
    logging.info('Size distribution saved to fig/field_subcas_num_dis.png.')

    ## ===
    field_cnbin_subcascade = json.loads(open('data/field_cnbin_subcascade_all.json').read())
    field_subcascade_df = json.loads(open('data/field_subcascade_df_all.json').read())
    field_ccbin_num = json.loads(open('data/field_ccbin_num_all.json').read())

    ## 不同field中不同ccbin对应的common motif,以tf/df进行排序，找出个ccbin对应的独特的motif
    subj_ccbin_motif_dict = defaultdict(lambda:defaultdict(dict))
    for subj in sorted(field_cnbin_subcascade.keys()):
        subcas_df = field_subcascade_df[subj]
        logging.info("subj of subcascade {},length of subcascade {}".format(subj,len(subcas_df)))

        for cc_bin in sorted(field_cnbin_subcascade[subj].keys()):

            subcas_num_dict = field_cnbin_subcascade[subj][cc_bin]

            subcas_num_total = field_ccbin_num[subj][cc_bin]

            motif_dict = defaultdict(dict)

            for sub_id in subcas_num_dict.keys():

                df = len(set(subcas_df[sub_id]))

                tf = subcas_num_dict[sub_id]

                norm_tf = tf/float(subcas_num_total)

                tfidf = norm_tf*(np.log(len(labels)/df))

                motif_dict[sub_id]['tf'] = tf
                motif_dict[sub_id]['norm_tf'] = norm_tf
                motif_dict[sub_id]['tfidf'] = tfidf

            ## 对于改bin下的top motif进行输出
            subj_ccbin_motif_dict[subj][cc_bin]= motif_dict

    ## 分别对每一个subject下不同的ccbin的motif进行计算
    lines = []
    for subj in sorted(subj_ccbin_motif_dict.keys()):
        line = '#### Subject:{}'.format(subj)
        header = "|"+'|'.join(['0']*25)+"|"
        pos = "|"+'|'.join([':--------:']*25)+"|"
        lines.append(line)
        lines.append(header)
        lines.append(pos)
        ccbin_motif_dict = subj_ccbin_motif_dict[subj]
        cc_lines = []
        for ccbin in sorted(ccbin_motif_dict.keys()):
            motif_dict = ccbin_motif_dict[ccbin]
            # print motif_dict
            cc_line = ['{}||'.format(labels[int(ccbin)])]
            cc_line.append('subcascade|tf|tfidf')
            for ix,motif in enumerate(sorted(motif_dict.keys(),key = lambda x:motif_dict[x]['tfidf'],reverse=True)[:10]):
                tf = motif_dict[motif]['tf']
                tfidf = motif_dict[motif]['tfidf']
                line = '![subcascade](subcascade/fig/subcas_{:}.jpg)|{}|{}'.format(motif,tf,tfidf)
                # print line
                cc_line.append(line)


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

    open("README.md",'w').write('\n'.join(lines)+'\n')
    logging.info('saved to README.md')



if __name__ == '__main__':

    field = 'ALL'
    paths = PATHS(field)
    # parse_args(paths)
    # run_all(paths)
    # dccp_of_paper(paths)
    # stat_dccp(paths)
    plot_dccps()

    # stat_subcascades(paths)
    # plot_subcascade_data()
    # logging.info('Done')



