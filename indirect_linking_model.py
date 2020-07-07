#coding:utf-8
'''

间接链接模型，生成真正的cascade


'''
from basic_config import *


def get_high_year_citnum():

    logging.info('loading _id_pubyear ...')
    selected_cascades = json.loads(open('data/selected_high_cascades.json').read())

    logging.info('loading pid year citnum ...')
    pid_year_citnum = json.loads(open('data/pid_year_citnum.json').read())

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
    if maxY+1<2018:
        mY=2018


    year_total = {}
    total = 0
    for y in range(minY,mY):
        total+= year_citnum.get(str(y),0)
        year_total[int(y)]=total
    return year_total


def random_selecting_linking_edges():
    ## 各个学科里面分别从50% 5% 1%随机选取了6篇论文
    logging.info('loading _id_pubyear ...')
    selected_cascades = json.loads(open('data/selected_high_cascades.json').read())

    pid_year_total = json.loads(open('data/selected_high_pid_year_total.json').read())

    ## 加载时间
    logging.info('loading _id_pubyear ...')
    _id_year = json.loads(open('data/pubyear_ALL.json').read())

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


    ##对每一个cascade的构建过程按照链入顺序重新安排
    new_pid_year_citing_cited = defaultdict(lambda:defaultdict(lambda:defaultdict(list)))
    for pid in pid_year_citing_cited.keys():

        year_citing_cited = pid_year_citing_cited[pid]

        for year in sorted(year_citing_cited.keys(),key=lambda x:int(x)):

            for citing_pid in year_citing_cited[year].keys():

                cited_pids = [p for p in  year_citing_cited[year][citing_pid] if p!=pid]

                if len(cited_pids)==0:
                    new_pid_year_citing_cited[pid][year][citing_pid].append(pid)

                else:
                    ## 根据前一年的被引论文的总次数进行概率计算
                    for indirect_pid in cit_by_impact(cited_pids,pid_year_total,year):

                        new_pid_year_citing_cited[pid][year][citing_pid].append(indirect_pid)

    ## 将新的保存
    open('data/new_randomized_cascade.json','w').write(json.dumps(new_pid_year_citing_cited))
    logging.info('new cascade saved to data/new_randomized_cascade.json')


def cit_by_impact(cited_pids,pid_year_total,year):

    props = [preyear_cit(pid_year_total,pid,year) for pid in cited_pids]

    print(props)

    props = np.array(props)/float(np.sum(props))

    N = np.random.randint(1,len(props)+1)

    selected_pids = np.random.choice(cited_pids,size=N,replace=False,p=props)

    return pids

def preyear_cit(pid_year_total,pid,year):

    if pid_year_total.get(pid,None) is None:
        return 0

    # if pid_year_total[pid].get(str(int(year)-1),None)

    return pid_year_total[pid].get(str(int(year)-1),0)






if __name__ == '__main__':
    # get_high_year_citnum()
    random_selecting_linking_edges()














