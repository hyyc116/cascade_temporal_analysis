#coding:utf-8
from basic_config import *


## 统计几个指标
## number of citations,dccps,dc,depth,anlec,
##

def stat_basic_attr(pathObj):

    cc_path = pathObj.cascade_path

    logging.info('loading citation cascade from {:}.'.format(cc_path))

    _id_cn = json.loads(open(pathObj.paper_cit_num_path).read())

    # num_of_cascades = len(citation_cascade.keys())
    # logging.info('{:} citation cascade are loaded.'.format(num_of_cascades))

    ##进度index
    progress_index = 0
    ## 存在环的pid
    cyclic_pids = []
    ## 放射型扇形cascade的数量
    radical_size_num = defaultdict(int)
    ##对每种类型的subcascade进行编号
    size_subcas_id = defaultdict(dict)
    _id_subcascade = {}
    ## 每篇文章subcas的分布
    pid_size_id = defaultdict(lambda:defaultdict(list))
    ## 文章的citation 数量
    pid_cnum = defaultdict(int)

    # citation_cascade = {}

    pid_attrs = {}

    for line in open(cc_path):

        line = line.strip()

        citation_cascade = json.loads(line)

        for pid in citation_cascade.keys():
            progress_index+=1

            if progress_index%10000==0:
                logging.info('progress report:{:}'.format(progress_index))

            edges = citation_cascade[pid]
            num_of_edges = len(edges)

            # 创建graph
            dig  = nx.DiGraph()
            dig.add_edges_from(edges)

            ##如果有环
            if not nx.is_directed_acyclic_graph(dig):
                cyclic_pids.append(pid)
                continue

            num_of_nodes = len(dig.nodes())
            citation_count = num_of_nodes-1

            ## dccp的数量是
            num_of_dccps = num_of_edges-citation_count

            pid_cnum[pid] = citation_count

            ## DEPTH
            depth=nx.dag_longest_path_length(dig)

            ## 根据出度以及入度对结点的角色进行分析
            node_count = 0
            connector_count = 0
            le_count = 0
            ie_count = 0

            connector_ccs = []
            for nid,od in dig.out_degree():

                ## 出度为0的是owner
                if od==0:
                    # owner_count+=1
                    pass
                else:
                    node_count+=1
                    ## 如果大于0，表示是endoser的一种
                    ind = dig.in_degree(nid)

                    if ind==0 and od==1:
                        ie_count+=1

                        # pid_node_role[pid][nid].append('ie')

                    if od>1:
                        le_count+=1
                        # pid_node_role[pid][nid].append('le')


                    if ind>0 and od>0:
                        connector_count+=1
                        # pid_node_role[pid][nid].append('c')

                        _cn = _id_cn.get(nid,0)

                        connector_ccs.append(_cn)

            if connector_count==0:
                anlec = 0
            else:
                anlec = le_count/float(connector_count)

            cc_of_connc = np.mean(connector_ccs) if len(connector_ccs)>0 else 0

            pid_attrs[pid] = [citation_count,num_of_edges,num_of_dccps,depth,anlec,cc_of_connc]



    open('data/pid_all_attrs.json','w').write(json.dumps(pid_attrs))

    logging.info('all data saved to data/pid_all_attrs.json.')



def plot_cascade_attr(pathObj):

    logging.info('loading _id_subjects ...')
    _id_subjects = json.loads(open(pathObj.paper_id_topsubj).read())

    logging.info('loading pid all pid_attrs ...')
    pid_attrs = json.loads(open('data/pid_all_attrs.json').read())

    logging.info('loading _id_pubyear ...')
    _id_pubyear = json.loads(open(pathObj.paper_year_path).read())

    sciento_ids = set([l.strip() for l in open(pathObj._scientometrics_path)])


    logging.info('starting to stat ..')
    subj_depth_dis = defaultdict(lambda:defaultdict(int))
    subj_anlec_dis = defaultdict(lambda:defaultdict(int))
    subj_cc_concc = defaultdict(lambda:defaultdict(list))
    progress = 0

    # logging.inf
    total = len(pid_attrs.keys())
    logging.info('total {} ...'.format(total))

    for pid in pid_attrs.keys():

        _year = _id_pubyear.get(pid,9999)

        if int(_year)>2016:
            continue

        citation_count,num_of_edges,num_of_dccps,depth,anlec,cc_of_connc = pid_attrs[pid]

        subjs = _id_subjects[pid]

        if len(subjs)>0:
            progress+=1

        if progress%10000:
            logging.info('progress {}/{} ..'.format(progress,total))

        for subj in subjs:
            subj_depth_dis[subj][depth]+=1

            subj_anlec_dis[subj][float('{:.4f}'.format(anlec))]+=1

            subj_cc_concc[subj][citation_count].append(cc_of_connc)

        subj_depth_dis['WOS_ALL'][depth]+=1

        subj_anlec_dis['WOS_ALL'][float('{:.4f}'.format(anlec))]+=1

        subj_cc_concc['WOS_ALL'][citation_count].append(cc_of_connc)

        if pid in sciento_ids:

            subj_depth_dis['SCIENTOMETRICS'][depth]+=1

            subj_anlec_dis['SCIENTOMETRICS'][float('{:.4f}'.format(anlec))]+=1

            subj_cc_concc['SCIENTOMETRICS'][citation_count].append(cc_of_connc)


    ## 画出depth的图
    logging.info('plotting depth...')

    plt.figure(figsize=(5,4))
    for subj in sorted(subj_depth_dis.keys()):

        xs = []
        ys = []

        for depth in sorted(subj_depth_dis[subj].keys()):

            xs.append(depth)
            ys.append(subj_depth_dis[subj][depth])

        ys = [np.sum(ys[i:])/float(np.sum(ys)) for i in range(len(ys))]

        plt.plot(xs,ys,label=subj)


    plt.legend()

    plt.xlabel('depth')

    plt.ylabel('probability')

    plt.title('CCDF')

    plt.tight_layout()

    plt.savefig('fig/cascade_depth_dis.png',dpi=400)

    ##画出anlec的论文

    logging.info('plotting anlec ..')

    plt.figure(figsize=(5,4))
    for subj in sorted(subj_anlec_dis.keys()):

        xs = []
        ys = []

        for anlec in sorted(subj_anlec_dis[subj].keys()):

            xs.append(anlec)
            ys.append(subj_anlec_dis[subj][anlec])

        ys = [np.sum(ys[i:])/float(np.sum(ys)) for i in range(len(ys))]

        plt.plot(xs,ys,label=subj)


    plt.legend()

    plt.xlabel('ANLEC')

    plt.ylabel('probability')

    plt.title('CCDF')

    plt.tight_layout()

    plt.savefig('fig/cascade_anlec_dis.png',dpi=400)


    ## 置信区间 需要每一个领域画一张图
    fig,axes = plt.subplots(4,2,figsize=(10,16))
    for i,subj in enumerate(sorted(subj_cc_concc.keys())):

        ax = axes[i/2,i%2]
        cc_connc = subj_cc_concc[subj]
        xs = []
        ys = []
        up_ys = []
        low_ys = []
        for cc in sorted(cc_connc):

            conns = cc_connc[cc]

            mean = np.mean(conns)
            std = np.std(conns)

            width = 1.96*(std/np.sqrt(len(conns)))

            xs.append(cc)
            ys.append(mean)

            up_ys.append(mean+width)
            low_ys.append(mean-width)


        ax.plot(xs,ys,c='r')

        ax.fill_bettwen(xs,up_ys,low_ys,alpha=0.6)

        ax.title(subj)
        ax.set_xlabel('number of citations')
        ax.set_ylabel('average citation count of connectors')

        ax.set_xscale('log')

    plt.tight_layout()

    plt.savefig('fig/cc_avgconcc.png',dpi=400)





if __name__ == '__main__':
    field = 'ALL'
    paths = PATHS(field)
    # stat_basic_attr(paths)

    plot_cascade_attr(paths)






















