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

    logging.info('start to plot subj cn ps ...')
    ## 画图 subj cn pc
    fig,axes = plt.subplots(1,3,figsize=(15,4))
    ax = axes[0]
    for i,subj in enumerate(sorted(subj_cn_pcs.keys())):
        _cn_pcs = subj_cn_pcs[subj]

        xs = []
        ys = []
        for _cn in sorted(_cn_pcs.keys()):
            xs.append(_cn)
            ys.append(np.mean(_cn_pcs[_cn]))

        ax.plot(xs,ys,label='{}'.format(subj),marker = markers[i])

    ax.legend()
    ax.set_xlabel('number of citations')
    ax.set_ylabel('$P(c)$')
    ax.set_xscale('log')

    ax = axes[1]
    ## subj cn ple
    for i,subj in enumerate(sorted(subj_cn_ples.keys())):
        _cn_ples = subj_cn_ples[subj]

        xs = []
        ys = []
        for _cn in sorted(_cn_ples.keys()):
            xs.append(_cn)
            ys.append(np.mean(_cn_ples[_cn]))

        ax.plot(xs,ys,label='{}'.format(subj),marker = markers[i])

    ax.legend()
    ax.set_xlabel('number of citations')
    ax.set_ylabel('$p(le)$')
    ax.set_xscale('log')


    ax = axes[2]
    # subj cn pie
    for i,subj in enumerate(sorted(subj_cn_pies.keys())):
        _cn_pies = subj_cn_pies[subj]

        xs = []
        ys = []
        for _cn in sorted(_cn_pies.keys()):
            xs.append(_cn)
            ys.append(np.mean(_cn_pies[_cn]))

        ax.plot(xs,ys,label='{}'.format(subj),marker = markers[i])

    ax.legend()
    ax.set_xscale('log')

    ax.set_xlabel('number of citations')
    ax.set_ylabel('$p(ie)$')
    plt.tight_layout()
    plt.savefig('fig/general_subj_cc_ps.png',dpi=300)
    logging.info('fig saved to fig/general_subj_cc_ps.png ...')



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
        for _year in sorted(_year_pcs.keys()):
            xs.append(_year)
            pcs.append(np.mean(_year_pcs[_year]))
            ples.append(np.mean(_year_ples[_year]))
            pies.append(np.mean(_year_pies[_year]))

        ax.plot(xs,pcs,label='p(c)',marker = markers[0])
        ax.plot(xs,ples,label='p(le)',marker = markers[1])
        ax.plot(xs,pies,label='p(ie)',marker = markers[1])

        ax.legend()
        ax.set_xlabel('publication year')
        ax.set_ylabel('$p$')

    plt.tight_layout()
    plt.savefig('fig/general_subj_year_ps.png',dpi=300)
    logging.info('fig saved to fig/general_subj_year_ps.png ...')

    logging.info('start to plot doctype ps ...')
    ## 分为三个子图
    fig,axes = plt.subplots(1,3, figsize=(15,4))

    ax = axes[0]
    xs = []
    ys = []
    for i,doctype in enumerate(kept_doctypes):
        pcs = doctype_pcs[doctype]
        xs.append(i)
        ys.append(np.mean(pcs))

    ax.bar(xs,ys)
    ax.set_xticks(xs)
    ax.set_xticklabels(kept_doctypes)
    ax.set_xlabel('doctype')
    ax.set_ylabel('$p(c)$')

    ax = axes[1]
    xs = []
    ys = []
    for i,doctype in enumerate(kept_doctypes):
        ples = doctype_ples[doctype]
        xs.append(i)
        ys.append(np.mean(ples))

    ax.bar(xs,ys)
    ax.set_xticks(xs)
    ax.set_xticklabels(kept_doctypes)
    ax.set_xlabel('doctype')
    ax.set_ylabel('$p(le)$')

    ax = axes[2]
    xs = []
    ys = []
    for i,doctype in enumerate(kept_doctypes):
        pies = doctype_pies[doctype]
        xs.append(i)
        ys.append(np.mean(pies))

    ax.bar(xs,ys)
    ax.set_xticks(xs)
    ax.set_xticklabels(kept_doctypes)
    ax.set_xlabel('doctype')
    ax.set_ylabel('$p(ie)$')

    plt.tight_layout()

    plt.savefig('fig/general_doctype_ps.png',dpi=300)
    logging.info('fig saved to fig/general_doctype_ps.png ...')



if __name__ == '__main__':
    field = 'ALL'
    paths = PATHS(field)
    # cascade_role(paths)

    general_node_role_dis(paths)






