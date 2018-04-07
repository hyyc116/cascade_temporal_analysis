#coding:utf-8

'''
    Tasks in this script:

        1. Citation Distribution, and get highly cited papers
        2. get citation cascade of highly cited papers
        3. endorser distribution over time
        4. Indirect links changes over time
        5. depth changes over time
        6. modularity changes over time
        7. subjects changes over time

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

    open('data/highly_cited_papers_cits.json','w').write(json.dumps(highly_cited_papers))


## plot highly cited papers, and saved highly cited paper ids
def plot_highly_cited_papers(highly_cited_papers_cits_path,com_IDs_year_path):
    logging.info('load com IDs year ...')
    com_IDs_year = json.loads(open(com_IDs_year_path).read())
    
    logging.info('load published years ...')
    highly_cited_papers = json.loads(open(highly_cited_papers_cits_path).read())

    total_num = len(highly_cited_papers.keys())
    logging.info('there are {:} highly cited papers loaded.'.format(total_num))

    logging.info('Plotting highly cited papers ..')
    selected_highly_cited_papers = {}
    high_pids = highly_cited_papers.keys()
    for pid in high_pids:
        if int(com_IDs_year.get(pid,-1))==-1:
            continue
        citation_list = highly_cited_papers[pid]
        isused = True
        years = []
        year_num = defaultdict(int)
        for cpid,year in citation_list:
            year = int(year)

            if year==-1:
                isused=False
                break

            years.append(year)
            year_num[year]+=1

        if isused and year_num[np.max(years)]<20:
            selected_highly_cited_papers[pid] = citation_list

    logging.info('there are {:} highly cited papers loaded.'.format(len(selected_highly_cited_papers.keys())))

    total_num = len(selected_highly_cited_papers.keys())
    high_pids = sorted(selected_highly_cited_papers.keys(),key=lambda x:len(selected_highly_cited_papers[x]),reverse=True)
    highly_cited_papers_ids = defaultdict(int)
    for i,pid in enumerate(high_pids[:total_num]):

        index = i%100

        if i%100==0:

            if i!=0:
                plt.tight_layout()
                plt.savefig('pdf/cds/plots_of_highly_cited_papers_{:}.jpg'.format(i),dpi=200)

            if total_num-i>100:
                rows=20
            else:
                rows = ((total_num-i)/5) if (total_num-i)%5==0 else ((total_num-i)/5)+1

            fig,axes = plt.subplots(rows,5,figsize=(25,rows*5))

        y0 = int(com_IDs_year[pid])
        highly_cited_papers_ids[pid] = y0
        print index,index/5
        ax = axes[index/5,index%5]
        citation_list = highly_cited_papers[pid]
        year_num =defaultdict(int)
        for cpid,year in citation_list:
            year = int(year)
            year_num[int(year)]+=1

        xs = []
        ys = []

        for year in sorted(year_num.keys()):
            # print year,y0
            xs.append(year-y0)
            ys.append(year_num[year])

        ax.plot(xs,ys)
        ax.set_title(pid)
        ax.set_xlabel('years after publication')
        ax.set_ylabel('number of citations')

    open('data/highly_cited_papers_ids_years.json','w').write(json.dumps(highly_cited_papers_ids))
    plt.tight_layout()
    plt.savefig('pdf/cds/plots_of_highly_cited_papers_{:}.jpg'.format(i),dpi=200)
    logging.info('figure saved to pdf/plots_of_highly_cited_papers.jpg.')

## get citation cascade of  highly cited paper 
def fetch_highly_cited_cascades(highly_cited_papers_ids_years_path,citation_cascade_path,saved_cascade_path):
    logging.info('loading highly cited papers ...')
    highly_cited_papers_ids = json.loads(open(highly_cited_papers_ids_years_path).read()).keys()

    logging.info('{:} highly cited paper ids are loaded, loading citation cascades .. '.format(len(highly_cited_papers_ids)))
    citation_cascade = {}
    progress = 0
    for line in open(citation_cascade_path):
        line = line.strip()
        progress+=1
        logging.info('progress {:} ..'.format(progress))
        citation_cascade.update(json.loads(line))

    highly_cited_citation_cascade = {}
    progress = 0
    for pid in highly_cited_papers_ids:
        edges = citation_cascade.get(pid,[])
        if len(edges)==0:
            logging.info('error pid : {:} ..'.format(pid))
            continue

        progress+=1
        logging.info('progress {:} ..'.format(progress))
        
        highly_cited_citation_cascade[pid] = citation_cascade[pid]


    open(saved_cascade_path,'w').write(json.dumps(highly_cited_citation_cascade))

    logging.info('citation cascade of {:} saved to {:}.'.format(highly_cited_papers_ids_years_path,saved_cascade_path))


### generate highly cited papers' temporal statistics data
def gen_temporal_stats(highly_cited_papers_ids_years_path,highly_cited_papers_cits_path,highly_cited_citation_cascade,com_IDs_subjects_path):

    ## load these data
    logging.info('load highly cited paper ids ..')
    highly_cited_papers_ids = json.loads(open(highly_cited_papers_ids_years_path).read())

    ## subjects
    logging.info('loading com Ids subjects ...')
    com_IDs_subjects = json.loads(open(com_IDs_subjects_path).read())

    logging.info('load highly_cited_papers citations ..')
    highly_cited_papers_cits = json.loads(open(highly_cited_papers_cits_path).read())

    logging.info('load highly cited papers\' citation cascades ... ')
    highly_cited_citation_cascade = json.loads(open(highly_cited_citation_cascade).read())

    paper_age_stats = {}
    ## based on highly cited paper cits, get yearly cpids
    progress = 0
    for pid in highly_cited_papers_ids.keys():
        citation_list = highly_cited_papers_cits[pid]
        ## loads from cc
        diG = nx.DiGraph()
        edges =  highly_cited_citation_cascade.get(pid,[])
        
        diG.add_edges_from(edges)

        if not nx.is_directed_acyclic_graph(diG):
            continue

        progress +=1

        logging.info('progress {:} ..'.format(progress))

        ## get published year of owner
        y0 = highly_cited_papers_ids[pid]

        ## stat yearly citations
        year_cits = defaultdict(list)
        for citation,year in citation_list:
            year_cits[int(year)].append(citation)

        ## yearly stat nodes
        age_stats = {}
        age_nodes = []
        for year in sorted(year_cits.keys()):
            age = year - y0
            age_nodes.extend(year_cits[year])

            ##based on existing nodes, get subgraph of total cascade
            subgraph = diG.subgraph(age_nodes)

            late_endorser,connector,norm_endorser,depth,num_of_ils,num_of_subjects,subjects = indicators_of_graph(subgraph,len(age_nodes),pid,com_IDs_subjects)

            age_stats[age] = [late_endorser,connector,norm_endorser,depth,num_of_ils,num_of_subjects,subjects]

        paper_age_stats[pid] = age_stats

    saved_path = 'data/highly_cited_paper_age_stats.json'
    open(saved_path,'w').write(paper_age_stats)
    logging.info('statistics data saved to {:}.'.format(saved_path))

def indicators_of_graph(subgraph,size):

    size = float(size)
    depth = 0
    # modularity = 0
    num_of_ils = 0
    ## depth
    depth=nx.dag_longest_path_length(subgraph)

    ## edges
    edges = subgraph.edges()

    for edge in edges:
        if edge[1]!=pid:
            num_of_ils+=1
    
    num_of_ils = num_of_ils/float(len(edges)) 

    outdegree_dict = subgraph.out_degree()

    num_of_le = 0
    num_of_cns = 0
    num_of_nes = 0
    subject_list = 0
    for nid,od in outdegree_dict:
        subject_list.extend(com_IDs_subjects.get(nid,[]))

        if od==0:
            continue

        ind = subgraph.in_degree(nid)

        if od>1:
            num_of_le+=1

        if ind>0:
            num_of_cns+=1

        if ind==0 and od == 1:
            num_of_nes+=1


    late_endorser = num_of_le/size
    connector = num_of_cns/size
    norm_endorser = num_of_nes/size

    subjects = Counter(subject_list)
    num_of_subjects = len(subjects.keys())
    return late_endorser,connector,norm_endorser,depth,num_of_ils,num_of_subjects,subjects


if __name__ == '__main__':
    pid_cits_path = 'data/pid_cits.txt'
    com_IDs_year_path = 'data/com_ids_year.json'
    # citation_distribution(pid_cits_path,com_IDs_year_path)
    highly_cited_papers_cits_path = 'data/highly_cited_papers_cits.json'
    # plot_highly_cited_papers(highly_cited_papers_cits_path,com_IDs_year_path)
    highly_cited_papers_ids_years_path = 'data/highly_cited_papers_ids_years.json'
    citation_cascade_path = 'data/citation_cascade.json'
    highly_cited_citation_cascade = 'data/highly_cited_citation_cascade.json'
    # fetch_highly_cited_cascades(highly_cited_papers_ids_years_path,citation_cascade_path,highly_cited_citation_cascade)
    com_IDs_subjects_path = 'data/com_ids_subjects.json'
    gen_temporal_stats(highly_cited_papers_ids_years_path,highly_cited_papers_cits_path,highly_cited_citation_cascade,com_IDs_subjects_path)










