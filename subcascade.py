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
    total_num = np.sum(num_dis.values())
    logging.info('total num of radical papers is {:}.'.format(total_num))

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


### 文章sub-cascade数量的分布
### 需要注意的是可能有直接相连的引证文献会去掉
def plot_num_of_comps(pathObj):

    logging.info('loading paper size id json ..')
    pid_size_id = json.loads(open(pathObj.paper_subcascades_path).read())

    total_pids = len(pid_size_id.keys())

    logging.info('loading paper citation num json ..')
    pid_cnum = json.loads(open(pathObj.paper_cit_num).read())

    cnum_maxsize = defaultdict(list)
    cnum_nums = defaultdict(list)
    cnum_0_nums = defaultdict(list)
    cnum_non_0_nums = defaultdict(list)
    cnum_0_percent = defaultdict(list)

    ## 不同的cnum中每种size在文献中出现的0/1list
    cnum_size_appears = defaultdict(lambda:defaultdict(int))
    cnum_dis = defaultdict(int)

    progress = 0
    for pid in pid_size_id.keys():

        progress+=1

        if progress%10000==0:
            logging.info('progress {:}/{:} ...'.format(progress,total_pids))

        cnum = pid_cnum[pid]
        num_of_nodes_in_none_0_comps = 0
        non_0_num_of_comps = 0
        ## 每一个size都有对应的一个list, list的长度的和就是一共多少的非0的component
        cnum_dis[cnum]+=1
        max_size  = 0

        for size in pid_size_id[pid].keys():

            size = int(size)

            cnum_size_appears[cnum][size]+=1

            ids = pid_size_id[pid][str(size)]

            num_of_nodes_in_none_0_comps +=len(ids)*size

            non_0_num_of_comps+=len(ids)

            if size > max_size:
                max_size = size


        _0_num_of_comps = cnum - num_of_nodes_in_none_0_comps

        num_of_comps = _0_num_of_comps+non_0_num_of_comps

        cnum_maxsize[cnum].append(max_size)
        cnum_nums[cnum].append(num_of_comps)
        cnum_0_nums[cnum].append(_0_num_of_comps)
        cnum_non_0_nums[cnum].append(non_0_num_of_comps)
        cnum_0_percent[cnum].append(_0_num_of_comps/float(cnum))


    cnum_xs = []
    maxsize_stats = []
    nums_stats = []
    _0_nums_stats = []
    non_0_nums_stats = []
    _0_percent_stats = []

    ### 对不同的slice进行可视化
    NS=[10,20,50,100,200,500]
    slice_datas = defaultdict(list)
    for cnum in sorted(cnum_nums.keys()):

        cnum_xs.append(cnum)

        maxsize_list = cnum_maxsize[cnum]
        maxsize_stats.append([np.max(maxsize_list),np.mean(maxsize_list),np.median(maxsize_list),np.min(maxsize_list)])

        nums_list = cnum_nums[cnum]
        nums_stats.append([np.max(nums_list),np.mean(nums_list),np.median(nums_list),np.min(nums_list)])

        _0_nums_list = cnum_0_nums[cnum]
        _0_nums_stats.append([np.max(_0_nums_list)+1,np.mean(_0_nums_list)+1,np.median(_0_nums_list)+1,np.min(_0_nums_list)+1])

        _0_percent_list = cnum_0_percent[cnum]
        _0_percent_stats.append([np.max(_0_percent_list),np.mean(_0_percent_list),np.median(_0_percent_list),np.min(_0_percent_list)])


        non_0_nums_list = cnum_non_0_nums[cnum]
        non_0_nums_stats.append([np.max(non_0_nums_list),np.mean(non_0_nums_list),np.median(non_0_nums_list),np.min(non_0_nums_list)])


        if cnum in NS:
        	slice_datas[cnum] = [maxsize_list,nums_list,_0_nums_list,non_0_nums_list]


    ## slice的distribution
    slice_size_data = defaultdict(list)
    for size in sorted(slice_datas.keys()):

    	data = slice_datas[size]

    	xs,ys = hist_2_bar(data[0])

    	fig_data = {}
    	fig_data['x'] = xs
    	fig_data['y'] = ys
    	fig_data['title'] = 'Maximum Size Distribution\n when N='+str(size)
    	fig_data['xlabel'] = 'Maximum size of sub-cascade'
    	fig_data['ylabel'] = 'number of papers'

    	slice_size_data[size].append(fig_data)

    	xs,ys = hist_2_bar(data[1])

    	fig_data = {}
    	fig_data['x'] = xs
    	fig_data['y'] = ys
    	fig_data['title'] = 'Number of sub-cascade Distribution\n when N='+str(size)
    	fig_data['xlabel'] = 'Number of sub-cascade'
    	fig_data['ylabel'] = 'number of papers'

    	slice_size_data[size].append(fig_data)


    	xs,ys = hist_2_bar(data[2])

    	fig_data = {}
    	fig_data['x'] = xs
    	fig_data['y'] = ys
    	fig_data['title'] = 'Number of Sub-cascade Distribution (size=1)\n when N='+str(size)
    	fig_data['xlabel'] = 'Number of sub-cascade'
    	fig_data['ylabel'] = 'number of papers'

    	slice_size_data[size].append(fig_data)

    	xs,ys = hist_2_bar(data[3])

    	fig_data = {}
    	fig_data['x'] = xs
    	fig_data['y'] = ys
    	fig_data['title'] = 'Number of Sub-cascade Distribution (size>1)\n when N='+str(size)
    	fig_data['xlabel'] = 'Number of sub-cascade'
    	fig_data['ylabel'] = 'number of papers'

    	slice_size_data[size].append(fig_data)

    open(pathObj._fd_slice_distribution_path,'w').write(json.dumps(slice_size_data))
    logging.info('data of slice distribution saved to {:}.'.format(pathObj._fd_slice_distribution_path))

    ### 根据数据进行画图
    fig,axes = plt.subplots(len(NS),4,figsize=(28,len(NS)*5))

    for i,size in enumerate(NS):

    	for j,fig_data in enumerate(slice_size_data[size]):

    		ax = axes[i,j]

    		plot_bar_from_data(fig_data,ax)

    plt.tight_layout()

    plt.savefig(pathObj._f_slice_distribution_path,dpi=300)
    logging.info('data of slice distribution saved to {:}.'.format(pathObj._f_slice_distribution_path))

    ### maximum size of comps
    maxes,means,medians,mins = zip(*maxsize_stats)
    fig_data = {}
    fig_data['x'] = cnum_xs
    fig_data['ys'] = [maxes,means,medians,mins,cnum_xs]
    fig_data['title'] = 'maximum size of sub-cascades distribution'
    fig_data['xlabel'] = 'number of citations'
    fig_data['ylabel'] = 'maximum size of sub-cascades'
    fig_data['markers'] = ['-o','->','-s','-^','--']
    fig_data['labels'] =['maximum','mean','median','minimum','$y=x$']
    fig_data['xscale'] = 'log'
    fig_data['yscale'] = 'log'

    open(pathObj._fd_maxsize_of_comps_path,'w').write(json.dumps(fig_data))
    logging.info('data of maximum size saved to {:}.'.format(pathObj._fd_maxsize_of_comps_path))
    plt.figure(figsize=(7,5))
    plot_multi_lines_from_data(fig_data)
    plt.savefig(pathObj._f_maxsize_of_comps_path,dpi=300)
    logging.info('figure of maximum size saved to {:}.'.format(pathObj._f_maxsize_of_comps_path))

    # num of comps
    datas = []
    fig,axes = plt.subplots(3,1,figsize=(7,15))

    ax0 = axes[0]
    ## data of nums of all subcascades
    maxes,means,medians,mins = zip(*nums_stats)
    fig_data = {}
    fig_data['x'] = cnum_xs
    fig_data['ys'] = [maxes,means,medians,mins,cnum_xs]
    fig_data['title'] = 'number of ALL sub-cascades distribution'
    fig_data['xlabel'] = 'number of citations'
    fig_data['ylabel'] = 'number of all sub-cascades'
    fig_data['markers'] = ['-o','->','-s','-^','--']
    fig_data['labels'] =['maximum','mean','median','minimum','$y=x$']
    fig_data['xscale'] = 'log'
    fig_data['yscale'] = 'log'

    datas.append(fig_data)
    plot_multi_lines_from_data(fig_data,ax0)

    ax1 = axes[1]
    ## data of nums of all subcascades
    maxes,means,medians,mins = zip(*non_0_nums_stats)
    fig_data = {}
    fig_data['x'] = cnum_xs
    fig_data['ys'] = [maxes,means,medians,mins,cnum_xs]
    fig_data['title'] = 'number of NON-0 sub-cascades distribution'
    fig_data['xlabel'] = 'number of citations'
    fig_data['ylabel'] = 'number of non 0 sub-cascades'
    fig_data['markers'] = ['-o','->','-s','-^','--']
    fig_data['labels'] =['maximum','mean','median','minimum','$y=x$']
    fig_data['xscale'] = 'log'
    fig_data['yscale'] = 'log'

    datas.append(fig_data)
    plot_multi_lines_from_data(fig_data,ax1)


    ax2 = axes[2]
    ## data of nums of all subcascades
    maxes,means,medians,mins = zip(*_0_nums_stats)
    fig_data = {}
    fig_data['x'] = cnum_xs
    fig_data['ys'] = [maxes,means,medians,mins,cnum_xs]
    fig_data['title'] = 'number of 0 sub-cascades distribution'
    fig_data['xlabel'] = 'number of citations'
    fig_data['ylabel'] = 'number of 0 sub-cascades'
    fig_data['markers'] = ['-o','->','-s','-^','--']
    fig_data['labels'] =['maximum','mean','median','minimum','$y=x']
    fig_data['xscale'] = 'log'
    fig_data['yscale'] = 'log'

    datas.append(fig_data)
    plot_multi_lines_from_data(fig_data,ax2)

    open(pathObj._fd_num_of_comps_path,'w').write(json.dumps(datas))
    logging.info('data of number of sub-cascades saved to {:}.'.format(pathObj._fd_num_of_comps_path))
    
    plt.tight_layout()
    plt.savefig(pathObj._f_num_of_comps_path,dpi=300)

    logging.info('figure of number of sub-cascades saved to {:}.'.format(pathObj._f_num_of_comps_path))

    ### percentage of nodes directly connected to owner
    maxes,means,medians,mins = zip(*_0_percent_stats)
    fig_data = {}
    fig_data['x'] = cnum_xs
    fig_data['ys'] = [maxes,means,medians,mins]
    fig_data['title'] = 'Distribution of percentage \n of nodes directly connected to the owner'
    fig_data['xlabel'] = 'number of citations'
    fig_data['ylabel'] = 'percentage of nodes'
    fig_data['markers'] = ['-o','->','-s','-^']
    fig_data['labels'] =['maximum','mean','median','minimum']
    fig_data['xscale'] = 'log'
    # fig_data['yscale'] = 'log'

    open(pathObj._fd_0_percent_path,'w').write(json.dumps(fig_data))
    logging.info('data of percentage of directed connected nodes saved to {:}.'.format(pathObj._fd_0_percent_path))
    plt.figure(figsize=(7,5))
    plot_multi_lines_from_data(fig_data)
    plt.savefig(pathObj._f_0_percent_path,dpi=300)
    logging.info('figure of percentage of directed connected nodes saved to {:}.'.format(pathObj._f_0_percent_path))

    ### 不同sub-cascade的size的分布

    last_num = 0
    last_total = 0
    cnum_alis = {}
    new_cnum_dis = defaultdict(list)
    for cnum in sorted(cnum_dis.keys()):

        num_of_papers = cnum_dis[cnum]

        if num_of_papers < 10 and last_total <50:

            cnum_alis[cnum] = last_num

            last_total += num_of_papers

            new_cnum_dis[last_num].append(num_of_papers)

        else:
            cnum_alis[cnum] = cnum
            last_num  = cnum
            last_total = num_of_papers

            new_cnum_dis[cnum].append(num_of_papers)


    size_cnum_num = defaultdict(lambda:defaultdict(list))
    size_cnum_total = defaultdict(lambda:defaultdict(list))
    for cnum in sorted(cnum_size_appears.keys()):
        
        num_of_papers = cnum_dis[cnum]
        a_cnum = cnum_alis[cnum]

        for size in sorted(range(2,7)):

            anum = cnum_size_appears[cnum].get(size,0)

            size_cnum_num[size][a_cnum].append(anum)

            size_cnum_total[size][a_cnum].append(num_of_papers)

    size_percents = defaultdict(list)
    for size in size_cnum_num.keys():
        cnum_xs = []
        for cnum in size_cnum_num[size].keys():

            cnum_xs.append(cnum)

            num = np.sum(size_cnum_num[size][cnum])
            total = np.sum(size_cnum_total[size][cnum])

            size_percents[size].append(num/float(total))

    fig_data = {}
    fig_data['x'] = cnum_xs
    fig_data['ys'] = [size_percents[2],size_percents[3],size_percents[4],size_percents[5],size_percents[6]]
    fig_data['title'] = 'Distribution of percentage of sub-cascade\n with N nodes'
    fig_data['xlabel'] = 'number of citations'
    fig_data['ylabel'] = 'percentage of papers'
    fig_data['markers'] = ['-o','->','-s','-^','-*']
    fig_data['labels'] =['$N=2$','$N=3$','$N=4$','$N=5$','$N=6$']
    fig_data['xscale'] = 'log'

    open(pathObj._fd_size_percent_path,'w').write(json.dumps(fig_data))
    logging.info('data of size percentage saved to {:}.'.format(pathObj._fd_size_percent_path))
    plt.figure(figsize=(7,5))
    plot_multi_lines_from_data(fig_data)
    plt.savefig(pathObj._f_size_percent_path,dpi=300)
    logging.info('figure of size percentage saved to {:}.'.format(pathObj._f_size_percent_path))

    xs = []
    ys = []
    for cnum in sorted(cnum_dis):

    	num = cnum_dis[cnum]

    	xs.append(cnum)
    	ys.append(num)

    xs2 = []
    ys2 = []
    for cnum in sorted(new_cnum_dis):

    	num = new_cnum_dis[cnum]

    	xs2.append(cnum)
    	ys2.append(np.sum(num))

    fig_data = {}
    fig_data['xs'] = [xs,xs2]
    fig_data['ys'] = [ys,ys2]
    fig_data['title'] = 'citation distribution'
    fig_data['xlabel'] = 'number of citations'
    fig_data['ylabel'] = 'number of papers'
    fig_data['markers'] = ['-o','-^']
    fig_data['labels'] =['normal','normed']
    fig_data['xscale'] = 'log'
    fig_data['yscale'] = 'log'

    open(pathObj._fd_citation_distribution_path,'w').write(json.dumps(fig_data))
    logging.info('data of citation distribution saved to {:}.'.format(pathObj._fd_citation_distribution_path))
    plt.figure(figsize=(7,5))
    plot_multi_lines_from_two_data(fig_data)
    plt.savefig(pathObj._f_citation_distribution_path,dpi=300)
    logging.info('figure of citation distribution saved to {:}.'.format(pathObj._f_citation_distribution_path))

    




## 对citation count的不同的切面做分布
def slice_distribution(pathObj,Ns):



    pass

if __name__ == '__main__':
    
    data = int(sys.argv[1])
    op = sys.argv[2]

    if int(sys.argv[1])==0:


        pathObj = PATHS('physics')

        if op=='find_subcas':

            find_sub_cascades(pathObj)

        elif op=='radical_num_dis':

            plot_radical_dis(pathObj)

        elif op=='num_of_comps':

            plot_num_of_comps(pathObj)


    else:

        pathObj = PATHS('computer science')

        if op=='find_subcas':

            find_sub_cascades(pathObj)

        elif op=='radical_num_dis':

            plot_radical_dis(pathObj)

        elif op=='num_of_comps':

            plot_num_of_comps(pathObj)
















