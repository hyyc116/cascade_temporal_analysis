#coding:utf-8

'''
    Tasks in this script:

        1. Citation Distribution, and get highly cited papers
        2. endorser distribution over time
        3. Indirect links changes over time
        4. depth changes over time
        5. modularity changes over time

'''
from basic_config import *
from paper_grouping import group_papers

def citation_distribution(pid_cits_path):
    logging.info("build cascade from {:} .".format(pid_cits_path))

    pid_citations = defaultdict(list)
    for line in open(pid_cits_path):
        ## line format: pid \t citing_id
        line = line.strip()
        pid,citing_id = line.split("\t")

        pid_citations[pid].append(citing_id)

    pid_cit_num = []
    for pid in pid_citations.keys():
        pid_cit_num.append(len(pid_citations[pid]))

    open('data/citation_list.txt','w').write(','.join(pid_cit_num))
    logging.info('citation list saved to citation_list.txt.')

    ## group paper into three groups
    xmin,xmax = group_papers(pid_cit_num,'data/paper_groups.jpg')

    logging.info('save highly cited papers ...')
    ## get highly cited papers
    highly_cited_papers = {}
    for pid in pid_citations.keys():
        if pid>=xmax:
            highly_cited_papers[pid] = pid_citations[pid]

    open('data/highly_cited_papers.json','w').write(json.dumps(highly_cited_papers))

    logging.info('saved to data/highly_cited_papers.json.')

    

if __name__ == '__main__':
    pid_cits_path = 'data/pid_cits.txt'
    citation_distribution(pid_cits_path)









