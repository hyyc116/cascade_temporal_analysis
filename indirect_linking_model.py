#coding:utf-8
'''

间接链接模型，生成真正的cascade


'''
from basic_config import *

def get_top_cascade():


    logging.info('loading _id_cn ...')
    _id_cn = json.loads(open('../WOS_data_processing/data/pid_cn.json').read())

    id_set = []

    for _id in _id_cn.keys():

        if int(_id_cn[_id])>1000:
            id_set.append(_id)

    id_set = set(id_set)

    logging.info('Number of ids is {}.'.format(len(id_set)))

    cc_path = 'data/cascade_ALL.txt'
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


def get_high_year_citnum():

    logging.info('loading _id_pubyear ...')
    selected_cascades = json.loads(open('data/selected_high_cascades.json').read())

    logging.info('loading pid year citnum ...')
    pid_year_citnum = json.loads(open('../WOS_data_processing/data/pid_year_citnum.json').read())

    selected_pid_year_total = {}

    id_list = []

    for pid in selected_cascades.keys():

        id_list.append(pid)

        for citing_pid,cited_pid in selected_cascades[pid]:
            id_list.append(citing_pid)
            id_list.append(cited_pid)

    id_list = list(set(id_list))

    for pid in id_list:

        if pid_year_citnum.get(pid,None) is None:
            continue
            
        year_total = paper_year_total_citnum(pid_year_citnum[pid])

        selected_pid_year_total[pid] = year_total


    open("data/selected_high_pid_year_total.json",'w').write(json.dumps(selected_pid_year_total))
    logging.info('data saved to data/selected_high_pid_year_total.json.')


def paper_year_total_citnum(year_citnum):

    years = [int(year) for year in year_citnum.keys()]

    minY = np.min(years)
    maxY = np.max(years)

    mY = maxY
    if maxY+1<2019:
        mY=2018


    year_total = {}
    total = 0
    for y in range(minY,mY):
        total+= year_citnum.get(str(y),0)
        year_total[int(y)]=total
    return year_total


def old_edges():
    ## 各个学科里面分别从50% 5% 1%随机选取了6篇论文
    logging.info('loading selected high impact cascade ..')
    selected_cascades = json.loads(open('data/selected_high_cascades.json').read())

    logging.info('{} papers are selected..'.format(len(selected_cascades.keys())))

    pid_year_total = json.loads(open('data/selected_high_pid_year_total.json').read())

    ## 加载时间
    logging.info('loading _id_pubyear ...')
    _id_year = json.loads(open('../WOS_data_processing/data/pid_pubyear.json').read())


    logging.info('start to stat cascade....')

    pid_year_citing_cited = defaultdict(lambda:defaultdict(lambda:defaultdict(list)))

    ## 将按照时间重新处理
    for pid in selected_cascades.keys():

        edges = selected_cascades[pid]

        pubyear = _id_year[pid]

        for citing_pid,cited_pid in edges:
            citing_year = _id_year[citing_pid]

            pid_year_citing_cited[pid][citing_year][citing_pid].append(cited_pid)

    open('data/old_cascade.json','w').write(json.dumps(pid_year_citing_cited))
    logging.info('old cascade saved to data/old_cascade.json')


def random_new_cascade():

    logging.info("loading high cascade ...")
    pid_year_citing_cited = json.loads(open('data/old_cascade.json').read())

    pid_year_total = json.loads(open('data/selected_high_pid_year_total.json').read())

    logging.info('{} papers loaded.'.format(len(pid_year_citing_cited.keys())))

    numT = len(pid_year_citing_cited.keys())

    new_f = open('data/new_randomized_cascade.json','w')

    ##对每一个cascade的构建过程按照链入顺序重新安排
    progress = 0
    new_pid_year_citing_cited = defaultdict(lambda:defaultdict(lambda:defaultdict(list)))
    for pid in pid_year_citing_cited.keys():

        progress+=1

        if progress%10==0:
            logging.info('progress {}/{}..'.format(progress,numT))

        year_citing_cited = pid_year_citing_cited[pid]

        for year in sorted(year_citing_cited.keys(),key=lambda x:int(x)):

            for citing_pid in year_citing_cited[year].keys():

                cited_pids = year_citing_cited[year][citing_pid]
                
                ## 根据前一年的被引论文的总次数进行概率计算,每一年随机50次

                props = [preyear_cit(pid_year_total,cited_id,year) for cited_id in cited_pids]

                props = np.array(props)/float(np.sum(props))

                for _ in range(20):

                    selected_pids = np.random.choice(cited_pids,size=len(props),replace=False,p=props)

                    new_pid_year_citing_cited[pid][year][citing_pid].append(selected_pids.tolist())

        if len(new_pid_year_citing_cited)>=100:
            new_f.write(json.dumps(new_pid_year_citing_cited)+'\n')
            new_pid_year_citing_cited = defaultdict(lambda:defaultdict(lambda:defaultdict(list)))

    ## 将新的保存
    new_f.write(json.dumps(new_pid_year_citing_cited)+'\n')
    logging.info('new cascade saved to data/new_randomized_cascade.json')


def preyear_cit(pid_year_total,pid,year):

    if pid_year_total.get(pid,None) is None:
        return 0.01

    # if pid_year_total[pid].get(str(int(year)-1),None)

    return pid_year_total[pid].get(str(int(year)-1),0.01)

def plot_changing_along_time():

    pid_cn = json.loads(open('../WOS_data_processing/data/pid_cn.json').read())

    new_cascade = json.loads(open('data/new_randomized_cascade.json').readline())

    logging.info('reading line 1, {} simulated cascades loaded.'.format(len(new_cascade.keys())))

    for i,pid in enumerate(new_cascade.keys()):

        cn  = pid_cn[pid]

        if cn>5000:
            continue

        plt.figure(figsize=(5,4))

        xs = []
        ys = []
        for year in sorted(new_cascade[pid].keys(),key=lambda x:int(x)):

            direct = 0
            total = 0

            ps = []
            for citing_pid in new_cascade[pid][year].keys():

                total+=1
                connectors_list = new_cascade[pid][year][citing_pid]
                # if len(connectors)==1 and pid==connectors[0]:
                #     direct+=1

                # if pid in connectors:
                #     direct+=1

                # print(connectors_list)

                cnects = []

                for connectors in connectors_list:

                    if len(isDirect(connectors,pid))==0:

                        cnects.append(0)
                    else:
                        cnects.append(1)

                undirect_prop = np.sum(cnects)/float(len(cnects))

                ps.append(undirect_prop)


            percent = np.mean(ps)

            xs.append(int(year))
            ys.append(percent)


        plt.title('{}:{}'.format(pid,cn))

        plt.plot(xs,ys)

        plt.xlabel('year')
        plt.ylabel('percentage of direct citations')

        plt.tight_layout()

        plt.savefig('fig/cascade_{}.png'.format(i),dpi=200)
        logging.info('fig saved to fig/cascade_{}.png'.format(i))



def isDirect(cits,pid):


    connectors = []
    for cit in cits:

        if pid == cit:
            break

        connectors.append(cit)

    # print(cits,pid,connectors)


    return connectors
    


if __name__ == '__main__':
    # get_top_cascade()
    # get_high_year_citnum()
    # random_selecting_linking_edges()
    # random_new_cascade()
    plot_changing_along_time()














