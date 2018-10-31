#coding:utf-8
'''
抽取sub-cascade及统计分析
'''
from basic_config import *

def iso_cc(size_subcas_id,_id_subcascade,graph):
    
    num_of_subcases = len(_id_subcascade.keys())

    size = len(graph.nodes())
    subcas_id  = size_subcas_id.get(size,{})
    is_iso = False
    for sub_cascade in subcas_id.keys():
        if nx.is_isomorphic(graph,sub_cascade):
            is_iso=True
            _id = subcas_id[sub_cascade]
            break

    if not is_iso:
        _id = num_of_subcases
        size_subcas_id[size][graph] = _id
        _id_subcascade[_id] = list(graph.edges())
    
    return size_subcas_id,_id_subcascade,_id

## 将与根节点的链接的边去掉,相当于出度小于2的点都去掉了
def find_sub_cascades(pathObj):

    cc_path = pathObj.cascade_path

    logging.info('loading citation cascade from {:}.'.format(cc_path))
    citation_cascade = {}

    for line in open(cc_path):

        line = line.strip()

        citation_cascade.update(json.loads(line))

    num_of_cascades = len(citation_cascade.keys())
    logging.info('{:} citation cascade are loaded.'.format(num_of_cascades))

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

    for pid in citation_cascade.keys():
        progress_index+=1

        if progress_index%1000==0:
            logging.info('progress report:{:}/{:}'.format(progress_index,num_of_cascades))

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

        pid_cnum[pid] = citation_count

        ## 如果没有环
        remaining_edges=[]
        for edge in edges:
            source = edge[0]
            target = edge[1]
            
            if target!=pid:
                remaining_edges.append(edge)
        
        ## 去掉与owner直接相连的边之后的边的数量
        remaining_edges_size = len(remaining_edges)
        # remaining_statistics[citation_count].append(remaining_edges_size/size_of_cascade)

        #如果剩余边的数量是0，无子图，原图形状为扇形
        if remaining_edges_size==0:
            ## 放射型cascade的分布计算
            radical_size_num[citation_count]+=1
            continue

        # 根据剩余边创建图
        dig  = nx.DiGraph()
        dig.add_edges_from(remaining_edges)
        #根据创建的有向图，获得其所有弱连接的子图
        for subgraph in nx.weakly_connected_component_subgraphs(dig):
            # 获得图像子图的边的数量
            node_size = len(subgraph.nodes())

            ## 对subgraphs进行判断
            _id = -999
            if node_size<6:
                size_subcas_id,_id_subcascade,_id = iso_cc(size_subcas_id,_id_subcascade,subgraph)
            
            ## 这个里面会将直接相连的节点省略
            pid_size_id[pid][node_size].append(_id)



    ##保存radical num 的分布
    open(pathObj.radical_num_dis_path,'w').write(json.dumps(radical_size_num))
    logging.info('radical subcascades saved to {:}.'.format(pathObj.radical_num_dis_path))

    ## 保存所有的sub-cascade的id以及对应的cascades的edges
    open(pathObj.all_subcasdes_path,'w').write(json.dumps(_id_subcascade))
    logging.info('{:} sub-cascades motif are detected, and aved to {:}.'.format(len(_id_subcascade.keys()),pathObj.all_subcasdes_path))

    ## 每篇文章的sub-cascade的分布 paper_subcascades_path
    open(pathObj.paper_subcascades_path,'w').write(json.dumps(pid_size_id))
    logging.info('paper sub-cascades distribution saved to {:}.'.format(pathObj.paper_subcascades_path))

    ## 每篇文章的引文数量
    open(pathObj.paper_cit_num,'w').write(json.dumps(pid_cnum))
    logging.info('{:} papers has 1 more citations and saved to {:}.'.format(len(pid_cnum.keys()),pathObj.paper_cit_num))


### radical cascade的分布, 没有间接链接的文章的
def plot_radical_dis(pathObj):

    logging.info('plot citation distribution of radical cascade ...')
    radical_num_dis_path = pathObj.radical_num_dis_path

    num_dis = json.loads(open(radical_num_dis_path).read())

    xs = []
    ys = []

    for num in sorted([int(num) for num in num_dis.keys()]):
        xs.append(num)
        ys.append(num_dis[str(num)])

    ## 每一个图都保存fig data
    fig_data = {}
    fig_data['x'] = xs
    fig_data['y'] = ys
    fig_data['title'] = 'citation distribution of radical cascades'
    fig_data['xlabel'] = 'number of citations'
    fig_data['ylabel'] = 'number of cascades'
    fig_data['marker'] = '-o'
    fig_data['xscale'] = 'log'
    fig_data['yscale'] = 'log'

    open(pathObj._fd_radical_num_dis_path,'w').write(json.dumps(fig_data))

    logging.info('data of citation distribution of radical distribution saved to {:}.'.format(pathObj._fd_radical_num_dis_path))


    plt.figure(figsize=(7,5))

    plot_line_from_data(fig_data)

    plt.savefig(pathObj._f_radical_num_dis_path,dpi=400)

    logging.info('figure of citation distribution of radical distribution saved to {:}.'.format(pathObj._f_radical_num_dis_path))



if __name__ == '__main__':
    
    data = int(sys.argv[1])
    op = sys.argv[2]

    if int(sys.argv[1])==0:


        pathObj = PATHS('physics')

        if op=='find_subcas':

            find_sub_cascades(pathObj)

        elif op=='radical_num_dis':

            plot_radical_dis(pathObj)


    else:

        pathObj = PATHS('computer science')

        if op=='find_subcas':

            find_sub_cascades(pathObj)

        elif op=='radical_num_dis':

            plot_radical_dis(pathObj)


















