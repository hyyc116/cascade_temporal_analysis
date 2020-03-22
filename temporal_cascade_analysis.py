#coding:utf-8

from basic_config import *

from dccp_metrics import load_attrs


## 从各个领域中提取出10000篇高被引的论文
def top_1_percent_papers(pathObj):

    # _id_subjects,_id_cn,_id_doctype,_id_year,top10_doctypes = load_attrs(pathObj)
    logging.info('loading _id_subjects ...')
    _id_subjects = json.loads(open(pathObj.paper_id_topsubj).read())

    logging.info('loading _id_cn ...')
    _id_cn = json.loads(open(pathObj.paper_cit_num_path).read())

    sciento_ids = set([l.strip() for l in open(pathObj._scientometrics_path)])

    ## 从各个领域选取引用次数最高的1%的论文，大部分有6000万 1%也就是60万数据
    _subj_id_cn = defaultdict(lambda:defaultdict(int))
    _subj_num = defaultdict(int)
    logging.info('stating ....')

    for _id in _id_subjects.keys():

        _subjs = _id_subjects[_id]


        if _id_cn.get(_id,None) is None:
            continue

        _cn = int(_id_cn[_id])

        if _cn <=2:
            continue

        for _subj in _subjs:

            _subj_id_cn[_subj][_id] = _cn

            _subj_num[_subj]+=1

        if _id in sciento_ids:

            _subj_id_cn["SCIENTOMETRICS"][_id] = _cn

    logging.info('stating top subject ...')
    ## 并保留各个
    _subj_id_dict = defaultdict(lambda:defaultdict(dict))

    _id_list = []
    for _subj in _subj_id_cn.keys():

        _id_cn = _subj_id_cn[_subj]

        sorted_ids = sorted(_id_cn.keys(),key = lambda x:_id_cn[x],reverse=True)

        num = len(sorted_ids)

        for p in [0.01,0.05,0.5]:
            ## 每一个范围随机选择6个

            selected_ids = np.random.choice(sorted_ids[:int(num*p)],6,replace=False)

            for _id in selected_ids:

                _subj_id_dict[_subj][p][_id] = _id_cn[_id]

                _id_list.append(_id)

    open('data/subject_id_cn_top1.json','w').write(json.dumps(_subj_id_dict))

    logging.info('data saved to data/subject_id_cn_top1.json.')

    _id_list = list(set(_id_list))

    open('data/selected_id_list.txt','w').write('\n'.join(_id_list))
    logging.info('id list saved to data/selected_id_list.txt.')


def get_top_cascade(pathObj):


    id_set = []

    for line in open("data/selected_id_list.txt"):
        line = line.strip()

        id_set.append(line)

    id_set = set(id_set)

    logging.info('Number of ids is {}.'.format(len(id_set)))


    cc_path = pathObj.cascade_path
    progress = 0

    selected_cascades = {}

    for line in open(cc_path):

        line = line.strip()

        citation_cascade = json.loads(line)

        for pid in citation_cascade.keys():

            progress+=1

            if progress%1000000==0:
                logging.info('progress report {:}, selected cascades size {} ...'.format(progress,len(selected_cascades)))

            if pid in id_set:

                selected_cascades[pid] = citation_cascade[pid]

    open('data/selected_high_cascades.json','w').write(json.dumps(selected_cascades))

    logging.info('data saved to data/selected_high_cascades.json')


def temporal_dccp(pathObj):

    logging.info('loading data ...')

    selected_cascades = json.loads(open('data/selected_high_cascades.json').read())
    ## 加载时间
    logging.info('loading _id_pubyear ...')
    _id_year = json.loads(open(pathObj.paper_year_path).read())

    pid_year_role = defaultdict(lambda:defaultdict(list))
    pid_year_dccps = defaultdict(lambda:defaultdict(int))
    pid_year_dcs= defaultdict(lambda:defaultdict(int))


    ## 这个
    progress = 0
    for pid in selected_cascades.keys():

        progress+=1
        if progress%100000==0:
            logging.info('progress {} ...'.format(progress))

        ## pid

        _year = int(_id_year[pid])

        edges = selected_cascades[pid]


        ## 创建graph
        dig  = nx.DiGraph()
        dig.add_edges_from(edges)

        citation_count = len(dig.nodes())-1


        # if citation cascade is not acyclic graph
        # if not nx.is_directed_acyclic_graph(dig):
        #     continue

        ## 出度进行计算
        for nid,od in dig.out_degree():

            if nid == pid:
                continue

            citing_year = int(_id_year[nid])

            ## 每年的被引用次数
            pid_year_dcs[pid][citing_year]+=1
            ## 出度-1之和就是dccp的数量
            pid_year_dccps[pid][citing_year]+=(od-1)

            if od>0:
                if od>1:
                    pid_year_role[pid][citing_year].append('le')

                ind = dig.in_degree(nid)


                if od==1 and ind==0:
                    pid_year_role[pid][citing_year].append('ie')

                ind = dig.in_degree(nid)

                if ind>0:
                    pid_year_role[pid][citing_year].append('c')


    open('data/selected_pid_year_role.json','w').write(json.dumps(pid_year_role))

    logging.info('data saved to data/selected_pid_year_role.json.')

    open('data/selected_pid_year_dccps.json','w').write(json.dumps(pid_year_dccps))

    open('data/selected_pid_year_dcs.json','w').write(json.dumps(pid_year_dcs))


## 每一个subject选取10篇，看出和year以及获得的citation数量之间的关系
def plot_temporal_dccp(pathObj):

    selected_pid_year_role = json.loads(open('data/selected_pid_year_role.json').read())

    selected_pid_year_dccps = json.loads(open('data/selected_pid_year_dccps.json').read())
    selected_pid_year_dcs = json.loads(open('data/selected_pid_year_dcs.json').read())

    #首先把所有的进行一起刻画

    lines = ['pid,index,year_index,year,p_cit_num,t_cit_num,le,ie']
    for pid in selected_pid_year_role.keys():

        total_cit_num = 0

        year_role = selected_pid_year_role[pid]

        first_year = None
        for ix,year in enumerate(sorted(year_role.keys(),key=lambda x:int(x))):
            _year = int(year)

            if ix==0:

                first_year=_year

            year_ix = _year-first_year

            roles = year_role[year]

            cit_num = len(roles)

            total_cit_num+=cit_num

            le_num = len([r for r in roles if r=='le'])

            ie_num = len([r for r in roles if r=='ie'])

            c_num = len([r for r in roles if r=='c'])

            num_of_dccps = selected_pid_year_dccps[pid][year]
            num_of_dcs = selected_pid_year_dcs[pid][year]

            line = '{},{},{},{},{},{},{},{},{},{},{}'.format(pid,ix,year_ix,_year,cit_num,total_cit_num,le_num,ie_num,num_of_dccps,num_of_dcs,c_num)

            lines.append(line)

    open('data/temporal_data.csv','w').write('\n'.join(lines))

    logging.info('data saved to data/temporal_data.csv.')



def plot_temporal_data(pathObj):

    top10subjids = json.loads(open('data/subject_id_cn_top1.json').read())

    id_set = set([line.strip() for line in open('data/selected_id_list.txt')])

    logging.info('size of id set {}'.format(len(id_set)))

    logging.info('number of papers in sciento {}.'.format(sciento_count))

    pid_attrs = defaultdict(list)
    ## 加载数据
    for line in open('data/temporal_data.csv'):

        line = line.strip()

        if line.startswith('pid'):
            continue

        splits = line.split(',')

        pid = splits[0]
        attrs = [float(i) for i in splits[1:]]

        # print pid
        if pid in id_set:

            pid_attrs[pid].append(attrs)


    logging.info('size of pid_attrs is {}'.format(len(pid_attrs)))

    ## 画出几个学科图

    subj_xs_ys = defaultdict(lambda:defaultdict(list))

    ## 每一个subj 画三张图
    for subj in top10subjids.keys():

        for _p in top10subjids[subj][_p]:

            _id_cn = top10subjids[subj][_p]

            logging.info('length {},{},{}'.format(subj,_p,len(_id_cn)))

            ## 每一个学科1张图
            fig,axes = plt.subplots(3,2,figsize=(10,13))

            fig.subplots_adjust(top=0.85)

            for i,_id in _id_cn.keys()[:6]:

                attrs = zip(*pid_attrs[_id])

                year_ixs = attrs[1]

                p_cit_nums = attrs[3]
                t_cit_nums = attrs[4]

                le_nums = attrs[5]
                t_le_nums = [np.sum(le_nums[:ix+1]) for ix in range(len(le_nums))]
                ie_nums = attrs[6]
                t_ie_nums = [np.sum(ie_nums[:ix+1]) for ix in range(len(ie_nums))]

                num_of_dccps = attrs[7]
                t_n_dccps = [np.sum(num_of_dccps[:ix+1]) for ix in range(len(num_of_dccps))]
                num_of_dcs = attrs[8]
                t_n_dcs = [np.sum(num_of_dcs[:ix+1]) for ix in range(len(num_of_dcs))]

                c_nums = attrs[9]

                t_c_nums = [np.sum(c_nums[:ix+1]) for ix in range(len(c_nums))]


                sums = np.array(t_n_dccps)+np.array(t_n_dcs)

                subj_xs_ys[subj][_p].append([_id,year_ixs,t_n_dccps,t_n_dcs,sums])


                ax = axes[i/2,i%2]

                ax.plot(year_ixs,np.array(t_le_nums)/np.array(t_cit_nums),label='p(le)')
                ax.plot(year_ixs,np.array(t_ie_nums)/np.array(t_cit_nums),label='p(ie)')
                ax.plot(year_ixs,np.array(t_c_nums)/np.array(t_cit_nums),label='p(c)')


                ax.set_xlabel('number of years after publication')
                ax.set_ylabel('percentage')

                ax.set_title(_id)

                ax.legend()



                ## 每一篇论文四个子图
                ## 第一个子图随着时间citation数量 le ie的数量变化
                # ax0 = axes[i,0]

                # ax0.plot(year_ixs,p_cit_nums,label='total citation')
                # ax0.plot(year_ixs,ie_nums,label='direct citation')
                # ax0.plot(year_ixs,le_nums,label='indirect citation')

                # ax0.set_xlabel('publication year')
                # ax0.set_ylabel('number of citations per year')

                # ax0.set_title('Number distribution')

                # ax0.legend()

                # ax1 = axes[i,1]

                # # ax1.plot(year_ixs,t_cit_nums,label='citation per year')
                # ax1.plot(year_ixs,np.array(ie_nums)/np.array(p_cit_nums),label='direct citation')
                # ax1.plot(year_ixs,np.array(le_nums)/np.array(p_cit_nums),label='indirect citation')

                # ax1.set_xlabel('publication year')
                # ax1.set_ylabel('number of citations')

                # ax1.set_title('year percentage')


                # ax1.legend()


                # ax1 = axes[i,2]

                # # ax1.plot(year_ixs,t_cit_nums,label='citation per year')
                # ax1.plot(year_ixs,np.array(t_ie_nums)/np.array(t_cit_nums),label='direct citation')
                # ax1.plot(year_ixs,np.array(t_le_nums)/np.array(t_cit_nums),label='indirect citation')

                # ax1.set_xlabel('publication year')
                # ax1.set_ylabel('number of citations')

                # ax1.set_title('total percentage')


                # ax1.legend()



                # ax2 = axes[i,3]
                # ax2.plot(t_cit_nums,np.array(le_nums)/np.array(p_cit_nums),label='indirect citation')
                # ax2.plot(t_cit_nums,np.array(ie_nums)/np.array(p_cit_nums),label='direct citation')

                # ax2.set_xlabel('publication year')
                # ax2.set_ylabel('number of citations per year')

                # ax2.set_title('year percentage')


                # ax2.legend()


                # ax3 = axes[i,4]
                # ax3.plot(t_cit_nums,np.array(t_ie_nums)/np.array(t_cit_nums),label='citation per year')
                # ax3.plot(t_cit_nums,np.array(t_le_nums)/np.array(t_cit_nums),label='direct citation')

                # ax3.set_xlabel('publication year')
                # ax3.set_ylabel('number of citations')

                # ax2.set_title('total percentage')


                # ax3.legend()

            plt.suptitle('{} - {}'.format(subj,_p),y=0.98,fontsize=20)
            # plt.tight_layout()

            plt.savefig('fig/temporal_{}_{}.png'.format(subj[:3],_p))

            logging.info('{} fig saved.'.format(subj))


    for subj in subj_xs_ys:

        ## 每一个学科1张图
        for _p in subj_xs_ys[subj].keys():

            fig,axes = plt.subplots(3,2,figsize=(10,13))

            fig.subplots_adjust(top=0.85)

            for i,(_id,year_ixs,t_n_dccps,t_n_dcs,sums) in enumerate(subj_xs_ys[subj][_p]):

                ax = axes[i/2,i%2]

                ax.plot(year_ixs,t_n_dccps,label='DCCP')
                ax.plot(year_ixs,t_n_dcs,label='DC')
                # ax.plot(year_ixs,sums,label='SUM')

                ax.set_xlabel('number of years after publication')
                ax.set_ylabel('number')

                ax.ticklabel_format(axis='y',style='sci')

                ax.yaxis.major.formatter.set_powerlimits((0,0))

                ax.set_title(_id)

                ax.legend()

            plt.suptitle('{} - {}'.format(subj,_p),y=0.98,fontsize=20)
            # plt.tight_layout()

            plt.savefig('fig/temporal_dccp_{}_{}.png'.format(subj[:3],_p))

            logging.info('{} DCCP TEMPORAL fig saved.'.format(subj))





## 级联矩阵
def plot_cascade_matrix(pathObj):

    logging.info('loading _id_cn ...')
    _id_cn = json.loads(open(pathObj.paper_cit_num_path).read())

    logging.info('loading _id_pubyear ...')
    _id_year = json.loads(open(pathObj.paper_year_path).read())

    ##高被引的cascade
    logging.info('loading data...')

    selected_cascades = json.loads(open('data/selected_high_cascades.json').read())

    ## 对于一个cascade

    pid = selected_cascades.keys()[999]

    logging.info('number of citations:{}'.format(_id_cn[pid]))

    edges = selected_cascades[pid]

    dig = nx.DiGraph()
    dig.add_edges_from(edges)

    node_id = {}
    node_num = {}
    for i,node in enumerate(sorted(dig.nodes(),key= lambda x:int(_id_year.get(x,1900)))):

        node_num[node]=int(_id_cn.get(node,0))
        node_id[node]=i

    num_of_node = len(node_id)
    data = np.zeros((num_of_node,num_of_node))

    for citing,cited in edges:

        pos1,pos2 = node_id[citing],node_id[cited]

        value = int(_id_cn[cited])

        data[pos2][pos1] = value

    ## 画出热力图
    import seaborn as sns

    fig,ax = plt.subplots(figsize=(6,5))

    sns.heatmap(data,ax = ax)

    plt.tight_layout()

    plt.savefig('fig/cascade_mat.png',dpi=400)
    logging.info('fig saved to fig/cascade_mat.png')





if __name__ == '__main__':
    field = 'ALL'
    paths = PATHS(field)

    top_1_percent_papers(paths)

    get_top_cascade(paths)

    temporal_dccp(paths)


    plot_temporal_dccp(paths)

    plot_temporal_data(paths)

    # plot_cascade_matrix(paths)













