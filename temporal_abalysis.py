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

def citation_distribution(pid_cits_path,com_IDs_year_path):
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

    logging.info('load published years ...')
    com_IDs_year = json.loads(open(com_IDs_year_path).read())


    logging.info("Paper grouping ...")
    ## group paper into three groups
    xmin,xmax = group_papers(pid_cit_num,'data/paper_groups.jpg')

    logging.info('save highly cited papers ...')
    ## get highly cited papers
    highly_cited_papers = {}
    for pid in pid_citations.keys():
        if pid>=xmax:
            cpid_list = []
            for cpid in pid_citations[pid]:
                cpid_list.append([cpid,com_IDs_year.get(cpid,-1)])

            highly_cited_papers[pid]=cpid_list

    open('data/highly_cited_papers.json','w').write(json.dumps(highly_cited_papers))

    logging.info('saved to data/highly_cited_papers.json.')


def plot_highly_cited_papers(highly_cited_papers_path):
    pass
    

if __name__ == '__main__':
    pid_cits_path = 'data/pid_cits.txt'
    com_IDs_year_path = 'data/com_ids_year.json'
    citation_distribution(pid_cits_path,com_IDs_year_path)









