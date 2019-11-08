#coding:utf-8
'''
不同类型论文cascade的node角色分布

'''
from basic_config import *

from dccp_metrics import load_attrs

## 根据cascade的出度入度对node的角色进行分析
def cascade_role(pathObj):

    cc_path = pathObj.cascade_path
    progress = 0
    owner_count = 0
    pid_role_dict = defaultdict(dict)

    pid_node_role = defaultdict(lambda:defaultdict(list))

    for line in open(cc_path):

        line = line.strip()

        citation_cascade = json.loads(line)

        for pid in citation_cascade.keys():

            progress+=1

            if progress%100000==0:
                logging.info('progress report {:} ...'.format(progress))

            edges = citation_cascade[pid]

            ## 创建graph
            dig  = nx.DiGraph()
            dig.add_edges_from(edges)

            # if citation cascade is not acyclic graph
            if not nx.is_directed_acyclic_graph(dig):
                continue

            ## 根据出度以及入度对结点的角色进行分析
            node_count = 0
            connector_count = 0
            le_count = 0
            ie_count = 0
            for nid,od in dig.out_degree():

                ## 出度为0的是owner
                if od==0:
                    owner_count+=1
                else:
                    node_count+=1
                    ## 如果大于0，表示是endoser的一种
                    ind = dig.in_degree(nid)

                    if ind==0 and od==1:
                        ie_count+=1

                        pid_node_role[pid][nid].append('ie')

                    if od>1:
                        le_count+=1
                        pid_node_role[pid][nid].append('le')


                    if ind>0 and od>0:
                        connector_count+=1
                        pid_node_role[pid][nid].append('c')


            pc = connector_count/float(node_count)
            ple = le_count/float(node_count)
            pie = ie_count/float(node_count)

            pid_role_dict[pid]['pc'] = pc
            pid_role_dict[pid]['ple'] = ple
            pid_role_dict[pid]['pie'] = pie

    open(pathObj._node_role_stat_path,'w').write(json.dumps(pid_role_dict))
    logging.info('data saved to {}.'.format(pathObj._node_role_stat_path))

    open(pathObj._node_role_dict_path,'w').write(json.dumps(pid_node_role))
    logging.info('data saved to {}.'.format(pathObj._node_role_dict_path))


markers = ['o','>','^','s','.','*','D','<']

def moving_average(ys,win=10):

    avgs = []
    for i,y in enumerate(ys):

        start = i-10 if i>=10 else 0

        avgs.append(np.mean(ys[start:i+1]))

    return avgs



def general_node_role_dis(pathObj):

    kept_doctypes = ['Article','Review','Proceedings Paper','Letter','Book Review','Editorial Material']

    _id_subjects,_id_cn,_id_doctype,_id_year,top10_doctypes =load_attrs(pathObj)

    pid_role_dict = json.loads(open(pathObj._node_role_stat_path).read())

    sciento_ids = set([l.strip() for l in open('scientometrics.txt')])

    ## 不同的role随着citation count的变化
    subj_cn_pcs = defaultdict(lambda:defaultdict(list))
    subj_cn_ples = defaultdict(lambda:defaultdict(list))
    subj_cn_pies = defaultdict(lambda:defaultdict(list))

    ## 不同学科 node role随着时间的变化
    subj_year_pcs = defaultdict(lambda:defaultdict(list))
    subj_year_ples = defaultdict(lambda:defaultdict(list))
    subj_year_pies = defaultdict(lambda:defaultdict(list))

    ## 不同doctype的三个指标分布
    doctype_pcs = defaultdict(list)
    doctype_ples = defaultdict(list)
    doctype_pies = defaultdict(list)

    logging.info('start to stating data ...')

    for pid in pid_role_dict.keys():

        pc = pid_role_dict[pid]['pc']
        ple = pid_role_dict[pid]['ple']
        pie = pid_role_dict[pid]['pie']

        _cn = int(_id_cn[pid])
        _subjs = _id_subjects[pid]
        _year = int(_id_year[pid])
        _doctype = _id_doctype[pid]

        for _subj in _subjs:

            subj_cn_pcs[_subj][_cn].append(pc)
            subj_cn_ples[_subj][_cn].append(ple)
            subj_cn_pies[_subj][_cn].append(pie)

            subj_year_pcs[_subj][_year].append(pc)
            subj_year_ples[_subj][_year].append(ple)
            subj_year_pies[_subj][_year].append(pie)

        subj_cn_pcs['WOS_ALL'][_cn].append(pc)
        subj_cn_ples['WOS_ALL'][_cn].append(ple)
        subj_cn_pies['WOS_ALL'][_cn].append(pie)

        subj_year_pcs['WOS_ALL'][_year].append(pc)
        subj_year_ples['WOS_ALL'][_year].append(ple)
        subj_year_pies['WOS_ALL'][_year].append(pie)

        if pid in sciento_ids:
            subj_cn_pcs['SCIENTOMETRICS'][_cn].append(pc)
            subj_cn_ples['SCIENTOMETRICS'][_cn].append(ple)
            subj_cn_pies['SCIENTOMETRICS'][_cn].append(pie)

            subj_year_pcs['SCIENTOMETRICS'][_year].append(pc)
            subj_year_ples['SCIENTOMETRICS'][_year].append(ple)
            subj_year_pies['SCIENTOMETRICS'][_year].append(pie)

        if _doctype in kept_doctypes:
            doctype_pcs[_doctype].append(pc)
            doctype_ples[_doctype].append(ple)
            doctype_pies[_doctype].append(pie)


    open('data/subj_cn_pcs.json','w').write(json.dumps(subj_cn_pcs))
    open('data/subj_cn_ples.json','w').write(json.dumps(subj_cn_ples))
    open('data/subj_cn_pies.json','w').write(json.dumps(subj_cn_pies))
    open('data/subj_year_pcs.json','w').write(json.dumps(subj_year_pcs))
    open('data/subj_year_ples.json','w').write(json.dumps(subj_year_ples))

    open('data/subj_year_pies.json','w').write(json.dumps(subj_year_pies))

    open('data/doctype_pcs.json','w').write(json.dumps(doctype_pcs))
    open('data/doctype_ples.json','w').write(json.dumps(doctype_ples))
    open('data/doctype_pies.json','w').write(json.dumps(doctype_pies))
    logging.info('data saved')

def plot_node_dis():
    kept_doctypes = ['Article','Review','Proceedings Paper','Letter','Book Review','Editorial Material']

    subj_cn_pcs = json.loads(open('data/subj_cn_pcs.json').read())

    logging.info('start to plot subj cn ps ...')
    ## 画图 subj cn pc
    fig,axes = plt.subplots(1,3,figsize=(15,4))
    ax = axes[0]
    for i,subj in enumerate(sorted(subj_cn_pcs.keys())):
        _cn_pcs = subj_cn_pcs[subj]

        xs = []
        ys = []
        for _cn in sorted(_cn_pcs.keys(),key=lambda x:int(x)):
            xs.append(int(_cn))
            ys.append(np.mean(_cn_pcs[_cn]))

        # zs = moving_average(ys,50)
        zs = [np.mean(ys[:i+1]) for i in range(len(ys))]

        ax.plot(xs,zs,label='{}'.format(subj))

    ax.legend(prop={'size':6})
    ax.set_xlabel('number of citations')
    ax.set_ylabel('$P(c)$')
    ax.set_xscale('log')


    subj_cn_ples = json.loads(open('data/subj_cn_ples.json').read())

    ax = axes[1]
    ## subj cn ple
    for i,subj in enumerate(sorted(subj_cn_ples.keys())):
        _cn_ples = subj_cn_ples[subj]

        xs = []
        ys = []
        for _cn in sorted(_cn_ples.keys(),key=lambda x:int(x)):
            xs.append(int(_cn))
            ys.append(np.mean(_cn_ples[_cn]))

        # zs = [i for i in zip(*lowess(ys,np.log(xs),frac=0.05,it=1,is_sorted =True))[1]]

        zs = moving_average(ys,50)


        ax.plot(xs,zs,label='{}'.format(subj))

    ax.legend(prop={'size':6})
    ax.set_xlabel('number of citations')
    ax.set_ylabel('$p(le)$')
    ax.set_xscale('log')


    subj_cn_pies = json.loads(open('data/subj_cn_pies.json').read())


    ax = axes[2]
    # subj cn pie
    for i,subj in enumerate(sorted(subj_cn_pies.keys())):
        _cn_pies = subj_cn_pies[subj]

        xs = []
        ys = []
        for _cn in sorted(_cn_pies.keys(),key=lambda x:int(x)):
            xs.append(int(_cn))
            ys.append(np.mean(_cn_pies[_cn]))

        # zs = [i for i in zip(*lowess(ys,np.log(xs),frac=0.01,it=1,is_sorted =True))[1]]

        zs = moving_average(ys,50)


        ax.plot(xs,zs,label='{}'.format(subj))

    ax.legend(prop={'size':6})
    ax.set_xscale('log')

    ax.set_xlabel('number of citations')
    ax.set_ylabel('$p(ie)$')
    plt.tight_layout()
    plt.savefig('fig/general_subj_cc_ps.png',dpi=300)
    logging.info('fig saved to fig/general_subj_cc_ps.png ...')



    subj_year_pcs = json.loads(open('data/subj_year_pcs.json').read())
    subj_year_ples = json.loads(open('data/subj_year_ples.json').read())

    subj_year_pies = json.loads(open('data/subj_year_pies.json').read())


    logging.info('start to plot subj year ps ...')
    fig,axes = plt.subplots(2,4,figsize=(20,8))
    ## 分为八个字图，每个三条线随着时间的变化
    for i,subj in enumerate(sorted(subj_year_pcs.keys())):

        ax = axes[i/4,i%4]

        _year_pcs = subj_year_pcs[subj]
        _year_ples = subj_year_ples[subj]
        _year_pies = subj_year_pies[subj]

        xs = []
        pcs = []
        ples = []
        pies = []
        for _year in sorted(_year_pcs.keys(),key=lambda x:int(x)):
            xs.append(int(_year))
            pcs.append(np.mean(_year_pcs[_year]))
            ples.append(np.mean(_year_ples[_year]))
            pies.append(np.mean(_year_pies[_year]))

        ax.plot(xs,pcs,label='p(c)')
        ax.plot(xs,ples,label='p(le)')
        ax.plot(xs,pies,label='p(ie)')

        ax.legend()
        ax.set_xlabel('publication year')
        ax.set_ylabel('$p$')
        ax.set_title('{}'.format(subj))

    plt.tight_layout()
    plt.savefig('fig/general_subj_year_ps.png',dpi=300)
    logging.info('fig saved to fig/general_subj_year_ps.png ...')

    doctype_pcs = json.loads(open('data/doctype_pcs.json').read())
    doctype_ples = json.loads(open('data/doctype_ples.json').read())
    doctype_pies = json.loads(open('data/doctype_pies.json').read())

    logging.info('start to plot doctype ps ...')
    ## 分为三个子图
    fig,ax = plt.subplots(1,1, figsize=(5,4))

    width = 0.3

    xs = []
    ys = []
    for i,doctype in enumerate(kept_doctypes):
        pcs = doctype_pcs[doctype]
        xs.append(i)
        ys.append(np.mean(pcs))

    ax.bar(np.arange(len(xs))-width,ys,width=width,label='{}'.format('p(c)'))

    xs = []
    ys = []
    for i,doctype in enumerate(kept_doctypes):
        ples = doctype_ples[doctype]
        xs.append(i)
        ys.append(np.mean(ples))

    ax.bar(np.arange(len(xs)),ys,width=width,label='{}'.format('p(le)'))


    xs = []
    ys = []
    for i,doctype in enumerate(kept_doctypes):
        pies = doctype_pies[doctype]
        xs.append(i)
        ys.append(np.mean(pies))

    ax.bar(np.arange(len(xs))+width,ys,width=width,label='{}'.format('p(ie)'))

    ax.set_xticks(xs)
    ax.set_xticklabels(kept_doctypes,rotation=-90)
    ax.set_xlabel('doctype')
    ax.set_ylabel('$percentage$')
    ax.legend()

    plt.tight_layout()

    plt.savefig('fig/general_doctype_ps.png',dpi=300)
    logging.info('fig saved to fig/general_doctype_ps.png ...')

def parallel_linking_data(pathObj):

    kept_doctypes = ['Article','Review','Proceedings Paper','Letter','Book Review','Editorial Material']

    _id_subjects,_id_cn,_id_doctype,_id_year,top10_doctypes =load_attrs(pathObj)

    pid_role_dict = json.loads(open(pathObj._node_role_dict_path).read())

    role_subj1_subj2 = defaultdict(lambda:defaultdict(lambda:defaultdict(int)))

    role_dt1_dt2 = defaultdict(lambda:defaultdict(lambda:defaultdict(int)))
    # ple_subj1_subj2 = defaultdict(lambda:defaultdict(int))
    # pie_subj1_subj2 = defaultdict(lambda:defaultdict(int))

    _year_role_subj1_subj2 = defaultdict(lambda:defaultdict(lambda:defaultdict(lambda:defaultdict(int))))


    progress = 0

    ## 统计每个subject对另一个subject的作用
    for pid in pid_role_dict.keys():

        progress+=1

        if progress%1000000==1:
            logging.info('progress {} ...'.format(progress))

        nid_roles = pid_role_dict[pid]
        subj2s = _id_subjects.get(pid,None)

        if subj2s is None:
            continue

        dt2 = _id_doctype[pid]

        for nid in nid_roles.keys():
            roles = pid_role_dict[pid][nid]
            subj1s = _id_subjects.get(nid,None)

            if subj1s is None:
                continue

            dt1 = _id_doctype[nid]
            year = int(_id_year[nid])

            for role in roles:
                for subj1 in subj1s:
                    for subj2 in subj2s:
                        role_subj1_subj2[role][subj1][subj2]+=1

                        _year_role_subj1_subj2[year][role][subj1][subj2]+=1

                role_dt1_dt2[role][dt1][dt2]+=1


    open('data/role_dt1_dt2.json','w').write(json.dumps(role_dt1_dt2))
    logging.info('data saved to data/role_dt1_dt2.json.')

    open('data/role_subj1_subj2.json','w').write(json.dumps(role_subj1_subj2))
    logging.info('data saved to data/role_subj1_subj2.json.')

    open('data/year_role_subj1_subj2.json','w').write(json.dumps(_year_role_subj1_subj2))
    logging.info('data saved to data/year_role_subj1_subj2.json.')



def gen_data(dict):

    data_lines = {}
    for role in role_subj1_subj2.keys():

        lines = []
        for subj1 in role_subj1_subj2[role].keys():

            subj2 = role_subj1_subj2[role][subj1]

            num = role_subj1_subj2[role][subj1][subj2]

            line= "[{},{},{},{}]".format(subj1,subj2,num,num)

            lines.append(line)

        data_lines[role] = lines


def year_bin(year):
    return int((year-1900)/10)

# year_bins = ['1910','1920','1930','1940','1950','1960','19','1980','2000','2016']
def year_label(i):
    return '{:}-{:}'.format(1900+i*10,1900+(i+1)*10)




def gen_temporal_role_data(pathObj):
    ## 对于不同的role的subject进行分析
    logging.info('generating data ....')
    year_role_subj1_subj2 = json.loads(open('data/year_role_subj1_subj2.json').read())

    type_yearbin_data = defaultdict(lambda:defaultdict(dict))

    _yearbins = []
    for _year in year_role_subj1_subj2.keys():


        _yearbin = year_bin(int(_year))

        _yearbins.append(_yearbin)

        for role in year_role_subj1_subj2[_year]:

            subj1_subj2 = year_role_subj1_subj2[_year][role]

            type_yearbin_data[role][_yearbin].update(subj1_subj2)


    _yearbins = list(sorted(list(set(_yearbins))))

    _yearlabels = [year_label(yb) for yb in _yearbins]

    year_label_js = 'var year_labels=['+','.join(_yearlabels)+'];'

    role_subj1_subj2 = json.loads(open('data/role_subj1_subj2.json').read())

    colors = ["#3366CC","#DC3912","#FF9900","#109618","#990099","#0099C6"]
    subj_colors = []
    for i,subj in enumerate(role_subj1_subj2['c'].keys()):
        subj_colors.append("'{}':'{}'".format(subj,colors[i]))
    subj_color_js = 'var subj_color = {'+','.join(subj_colors)+"};"
    logging.info('generating JS....')

    ## 不同类型的数据生成js,每一种类型的每一年生成数据
    jses= []

    jses.append(subj_color_js)

    jses.append(year_label_js)

    for role in type_yearbin_data.keys():

        role_js = 'var {}_temp_data=['.format(role)

        data = []
        for _yearbin in sorted(type_yearbin_data[role].keys()):

            data.append(gen_link_data(type_yearbin_data[role][_yearbin]))

        role_js +=','.join(data)+'];'

        jses.append(role_js)


    open('js/temp_data.js','w').write('\n'.join(jses))

    logging.info('Data saved to js/temp_data.js.')



## gen link
def gen_link_data(left_right):

    lines = []
    for left in left_right.keys():

        for right in left_right[left].keys():

            num = left_right[left][right]

            line = "['{}','{}',{},{}]".format(left,right,num,num)

            lines.append(line)


    return '['+','.join(lines)+']'


def gen_doc_data(left_right):

    kept_doctypes = ['Article','Review','Proceedings Paper','Letter','Book Review','Editorial Material']

    lines = []
    for left in left_right.keys():

        if left not in kept_doctypes:
            continue

        for right in left_right[left].keys():

            if right not in kept_doctypes:
                continue

            num = left_right[left][right]

            line = "['{}','{}',{},{}]".format(left,right,num,num)

            lines.append(line)


    return '['+','.join(lines)+'];'

def plot_role_data():

    role_subj1_subj2 = json.loads(open('data/role_subj1_subj2.json').read())
    role_dt1_dt2 = json.loads(open('data/role_dt1_dt2.json').read())


    ## 对于不同的role的subject进行分析
    colors = ["#3366CC","#DC3912","#FF9900","#109618","#990099","#0099C6"]

    kept_doctypes = ['Article','Review','Proceedings Paper','Letter','Book Review','Editorial Material']

    subj_colors = []

    for i,subj in enumerate(role_subj1_subj2['c'].keys()):

        subj_colors.append("'{}':'{}'".format(subj,colors[i]))

    subj_color_js = 'var subj_color = {'+','.join(subj_colors)+"};"


    doc_colors = []

    for i,doc in enumerate(kept_doctypes):

        doc_colors.append("'{}':'{}'".format(doc,colors[i]))

    doc_color_js = 'var doc_color = {'+','.join(doc_colors)+"};"




    js_scirpts = []

    js_scirpts.append(subj_color_js)
    js_scirpts.append(doc_color_js)


    ## 三种不同的角色生成三种不同的图


    c_js = 'var c_subj_data ='+gen_link_data(role_subj1_subj2['c'])+';'
    le_js = 'var le_subj_data ='+gen_link_data(role_subj1_subj2['le'])+';'
    ie_js = 'var ie_subj_data ='+gen_link_data(role_subj1_subj2['ie'])+';'

    js_scirpts.append(c_js)
    js_scirpts.append(le_js)
    js_scirpts.append(ie_js)


    c_js = 'var c_doc_data ='+gen_doc_data(role_dt1_dt2['c'])
    le_js = 'var le_doc_data ='+gen_doc_data(role_dt1_dt2['le'])
    ie_js = 'var ie_doc_data ='+gen_doc_data(role_dt1_dt2['ie'])

    js_scirpts.append(c_js)
    js_scirpts.append(le_js)
    js_scirpts.append(ie_js)

    open('js/data.js','w').write('\n'.join(js_scirpts))

    logging.info('data saved to js/data.js')



if __name__ == '__main__':
    field = 'ALL'
    paths = PATHS(field)
    # cascade_role(paths)

    # general_node_role_dis(paths)
    plot_node_dis()

    ## 平行链接数据
    # parallel_linking_data(paths)

    # plot_role_data()

    # gen_temporal_role_data(paths)






