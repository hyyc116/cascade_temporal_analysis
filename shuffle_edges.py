#coding:utf-8
'''
对所有的edge进行shuffle,然后看效果


'''

from basic_config import *

from numpy.random import shuffle
### pid_year edges
def shuffle_edges(pathObj):

    logging.info("loading paper year path ...")
    paper_year = json.loads(open(pathObj.paper_year_path).read())

    _ids_subjects = json.loads(open('data/_ids_subjects.json').read())

    logging.info('_id_subjects.json loaded ....')

    ## 根据年份将target list shuffle. 

    pid_cits_path = pathObj.pid_cits_path
    logging.info("build cascade from {:} .".format(pid_cits_path))

    progress = 0

    year_edges = defaultdict(lambda:defaultdict(list))

    for line in open(pid_cits_path):

        progress+=1

        if progress%10000000==0:
            logging.info('reading %d citation relations....' % progress)

        line = line.strip()
        pid,citing_id = line.split("\t")

        ## 如果不是wos的论文
        subjs = _ids_subjects.get(pid,[])

        if len(subjs)==0:
            continue

        targ_year = paper_year.get(pid,None)

        if targ_year is None:
            continue

        ## 这里随机选择一个subj
        subj = np.random.choice(subjs,size=1)[0]

        year_edges[targ_year][subj].append([pid,citing_id])


    logging.info('edges loaded, starting to shuffle.')

    f = open('data/shuffled_edges.txt','w')

    for year in year_edges.keys():

        for subj in year_edges[year].keys():

            edges = year_edges[year][subj]

            targ,source = zip(*edges)

            num = len(edges)

            logging.info('Year {},Subj {}, Num of edges {}.'.format(year,subj,len(edges)))

            ## 直接对
            num_index = range(num)
            shuffle(num_index)

            targ_i = [targ[ix] for ix in num_index]
            ## 新的edges
            edges = zip(targ_i,source)

            logging.info('shuffled lines {}'.format(len(edges)))

        
            f.write('\n'.join(['\t'.join(e) for e in edges])+"\n")


    f.close()
    logging.info("shuffled done!")

if __name__ == '__main__':
    
    field = 'ALL'
    paths = PATHS(field)

    shuffle_edges(paths)



