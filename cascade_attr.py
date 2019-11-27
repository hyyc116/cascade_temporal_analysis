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
                    owner_count+=1
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


            anlec = le_count/float(connector_count)

            cc_of_connc = np.mean(connector_ccs) if len(connector_ccs)>0 else 0

            pid_attrs[pid] = [citation_count,num_of_edges,num_of_dccps,depth,anlec,cc_of_connc]



    open('data/pid_all_attrs.json','w').write(json.dumps(pid_attrs))

    logging.info('all data saved to data/pid_all_attrs.json.')

if __name__ == '__main__':
    field = 'ALL'
    paths = PATHS(field)
    stat_basic_attr(paths)






















