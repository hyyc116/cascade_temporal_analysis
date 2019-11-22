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

    ## 从各个领域选取引用次数最高的1%的论文，大部分有6000万 1%也就是60万数据
    _subj_id_cn = defaultdict(lambda:defaultdict(int))
    _subj_num = defaultdict(int)
    logging.info('stating ....')

    for _id in _id_subjects.keys():

        _subjs = _id_subjects[_id]


        if _id_cn.get(_id,None) is None:
            continue

        _cn = int(_id_cn[_id])

        for _subj in _subjs:

            _subj_id_cn[_subj][_id] = _cn

            _subj_num[_subj]+=1

    logging.info('stating top subject ...')
    ## 并保留各个
    _subj_id_dict = defaultdict(lambda:defaultdict(int))
    for _subj in _subj_id_cn.keys():

        num = int(_subj_num[_subj]/10)

        _id_cn = _subj_id_cn[_subj]

        for _id in sorted(_id_cn.keys(),key = lambda x:_id_cn[x],reverse=True)[:num]:

            # pass
            _subj_id_dict[_subj][_id] = _id_cn[_id]


    open('data/subject_id_cn_top1.json','w').write(json.dumps(_subj_id_dict))

    logging.info('data saved to data/subject_id_cn_top1.json.')


def get_top_cascade(pathObj):

    top10subjids = json.loads(open('data/subject_id_cn_top1.json').read())

    id_set = []

    for subj in top10subjids:

        _id_cn = top10subjids[subj]

        num = len(_id_cn)
        logging.info('subject {} has {} papers.'.format(subj,num))

        for _id in sorted(_id_cn.keys(),key = lambda x:_id_cn[x],reverse=True)[:num/10]:

            id_set.append(_id)

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

        # if citation cascade is not acyclic graph
        # if not nx.is_directed_acyclic_graph(dig):
        #     continue

        ## 出度进行计算
        for nid,od in dig.out_degree():

            citing_year = int(_id_year[nid])

            if od!=0:
                if od>1:
                    pid_year_role[pid][citing_year].append('le')

                if od==1:
                    pid_year_role[pid][citing_year].append('ie')


    open('data/selected_pid_year_role.json','w').write(json.dumps(pid_year_role))

    logging.info('data saved to data/selected_pid_year_role.json.')


## 每一个subject选取10篇，看出和year以及获得的citation数量之间的关系
def plot_temporal_dccp(pathObj):

    selected_pid_year_role = json.loads(open('data/selected_pid_year_role.json').read())

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

            line = '{},{},{},{},{},{},{},{}'.format(pid,ix,year_ix,_year,cit_num,total_cit_num,le_num,ie_num)

            lines.append(line)

    open('data/temporal_data.csv','w').write('\n'.join(lines))

    logging.info('data saved to data/temporal_data.csv.')



def plot_temporal_data():

    top10subjids = json.loads(open('data/subject_id_cn_top1.json').read())

    id_set = []

    subj_ids = defaultdict(list)
    for subj in top10subjids:

        _id_cn = top10subjids[subj]

        num = len(_id_cn)
        logging.info('subject {} has {} papers.'.format(subj,num))

        for _id in sorted(_id_cn.keys(),key = lambda x:_id_cn[x],reverse=True)[:5]:

            id_set.append(_id)

            subj_ids[subj].append(_id)

    id_set = set(id_set)

    logging.info('size of id set {}'.format(len(id_set)))


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

    for subj in subj_ids:

        ## 每一个学科1张图
        fig,axes = plt.subplots(1,5,figsize=(25,5))

        fig.subplots_adjust(top=0.8)

        for i,_id in enumerate(subj_ids[subj]):

            attrs = zip(*pid_attrs[_id])

            # logging.info('{}'.format(len(attrs)))

            year_ixs = attrs[1]

            p_cit_nums = attrs[3]
            t_cit_nums = attrs[4]

            le_nums = attrs[5]
            t_le_nums = [np.sum(le_nums[:ix+1]) for ix in range(len(le_nums))]
            ie_nums = attrs[6]
            t_ie_nums = [np.sum(ie_nums[:ix+1]) for ix in range(len(ie_nums))]

            ax = axes[i]

            ax.plot(year_ixs,t_cit_nums,label='total')
            ax.plot(year_ixs,t_le_nums,label='le')
            ax.plot(year_ixs,t_ie_nums,label='ie')

            ax.set_xlabel('year index')
            ax.set_ylabel('number')

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

        plt.suptitle(subj,y=0.95,fontsize=12)
        plt.tight_layout()

        plt.savefig('fig/temporal_{}.png'.format(subj[:3]))

        logging.info('{} fig saved.'.format(subj))

if __name__ == '__main__':
    field = 'ALL'
    paths = PATHS(field)

    # top_1_percent_papers(paths)

    # get_top_cascade(paths)

    # temporal_dccp(paths)


    # plot_temporal_dccp(paths)

    plot_temporal_data()













