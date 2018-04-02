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
    xmin,xmax = group_papers(pid_cit_num,'pdf/paper_groups.jpg')

    logging.info('save highly cited papers ...')
    ## get highly cited papers
    highly_cited_papers = {}
    for pid in pid_citations.keys():
        if len(pid_citations[pid])>=xmax:
            cpid_list = []
            for cpid in pid_citations[pid]:
                cpid_list.append([cpid,com_IDs_year.get(cpid,-1)])

            highly_cited_papers[pid]=cpid_list

    open('data/highly_cited_papers.json','w').write(json.dumps(highly_cited_papers))


def plot_highly_cited_papers(highly_cited_papers_path):
    highly_cited_papers = json.loads(open(highly_cited_papers_path).read())
    logging.info('Plotting highly cited papers ..')
    high_pids = highly_cited_papers.keys()
    total_num = len(high_pids)


    logging.info('there are {:} highly cited papers loaded.'.format(total_num))
    rows = (total_num/5)+1
    fig,axes = plt.subplots(rows,5,figsize=(25,rows*5))
    highly_cited_papers_ids = []
    for i,pid in enumerate(high_pids[:100]):

        highly_cited_papers_ids.append(pid)

        y0 = com_IDs_year[pid]
        ax = axes[i/5,i%5]
        citation_list = highly_cited_papers[pid]
        year_num =defaultdict(int)
        for cpid,year in citation_list:
            year_num[year]+=1

        xs = []
        ys = []
        for year in sorted(year_num.keys()):
            xs.append(year-y0)
            ys.append(year_num[year])

        ax.plot(xs,ys)
        ax.set_title(pid)
        ax.set_xlabel('years after publication')
        ax.set_ylabel('number of citations')

    open('data/highly_cited_papers_ids.txt','w').write('\n'.join(highly_cited_papers_ids))
    plt.savefig('pdf/plots_of_highly_cited_papers.jpg',dpi=200)
    logging.info('figure saved to pdf/plots_of_highly_cited_papers.jpg.')

    

if __name__ == '__main__':
    pid_cits_path = 'data/pid_cits.txt'
    com_IDs_year_path = 'data/com_ids_year.json'
    # citation_distribution(pid_cits_path,com_IDs_year_path)
    highly_cited_papers_path = 'data/highly_cited_papers.json'
    plot_highly_cited_papers(highly_cited_papers_path)










