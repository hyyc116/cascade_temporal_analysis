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
    logging.info('{:} highly cited paper ids loaded ..'.format(len(highly_cited_papers_ids.keys())))

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
        
        if len(edges)==0:
            logging.debug('paper:{:} has no edges.'.format(pid))
            continue

        diG.add_edges_from(edges)

        logging.debug('number of nodes: {:}, number of citations:{:} .'.format(len(diG.nodes()),len(citation_list)))

        # WOS 中存在大量的相互引用，似乎，尤其是在物理学领域。
        # if not nx.is_directed_acyclic_graph(diG):
            # analyze_acyclic(edges)
            # continue

            

        progress +=1
        logging.info('progress {:} ..'.format(progress))

        ## get published year of owner
        y0 = highly_cited_papers_ids[pid]
        ## stat yearly citations
        year_cits = defaultdict(list)
        for citation,year in citation_list:
            year_cits[int(year)].append(citation)

        ## yearly stat nodes
        age_stats = defaultdict(dict)
        age_nodes = [pid]
        last_attr = [0]*7
        for year in sorted(year_cits.keys()):
            age = year - y0
            # print year,year_cits[year]
            cits = year_cits[year]
            age_nodes.extend(cits)
            noc = float(len(cits))

            ##based on existing nodes, get subgraph of total cascade
            subgraph = diG.subgraph(age_nodes)

            ## 获得所有可以获得的属性
            attr = indicators_of_graph(subgraph,pid,com_IDs_subjects,cits)
            late_endorser,connector,norm_endorser,depth,num_of_ils,num_of_subjects,subjects,nid_of_connector_dis,new_les,new_nes,num_of_lc,num_of_nc,node_role,le_od_dis = attr
            present_size = float(len(age_nodes))
            indicators = []
            accumulative_indicators = [present_size,late_endorser/present_size,connector/present_size,norm_endorser/present_size,depth,num_of_ils/present_size,num_of_subjects,subjects,le_od_dis,node_role,nid_of_connector_dis,num_of_lc/present_size,num_of_nc/present_size]
            indicators.extend(accumulative_indicators)

            ## incremental的属性比例，也即是当年获得的引用中各种点所占的比例
            incremental_indicators = [noc]

            ## 每年新增的引用中有多少是late endorser
            incremental_indicators.append(new_les/noc)

            
            ## 每年新增一个citation,需要增加多少connector
            incremental_indicators.append((attr[1]-last_attr[1])/noc)


            ## 每年增加的点中有多少是 normal endorser
            incremental_indicators.append(new_nes/noc)

            ##每增加一个citation 所需要的indreict link的数量
            incremental_indicators.append((attr[4]-last_attr[4])/noc)

            ##每年增加subject的数量
            incremental_indicators.append(attr[5]-last_attr[5])

            age_stats[age]['accumulative'] = accumulative_indicators
            age_stats[age]['incremental'] = incremental_indicators

            last_attr = attr

        paper_age_stats[pid] = age_stats

    saved_path = 'data/highly_cited_paper_age_stats.json'
    open(saved_path,'w').write(json.dumps(paper_age_stats))
    logging.info('statistics data saved to {:}.'.format(saved_path))


def analyze_acyclic(edges):
    known_edges=set()

    for edge in edges:

        e = '=='.join(sorted(edge))

        if e in known_edges:
            print e, edge
        else:
            known_edges.add(e)



def indicators_of_graph(subgraph,pid,com_IDs_subjects,new_cits):

    depth = 0
    # modularity = 0
    num_of_ils = 0
    ## depth
    # depth = 0
    # depth=nx.dag_longest_path_length(subgraph)
    while True:
        try:
            
            edgeList = nx.find_cycle(subgraph, orientation='original')
            rn_edge = random.choice(edgeList)
            subgraph.remove_edge(rn_edge[0],rn_edge[1])

        except:
            break

    ### 新的节点集合
    new_cits = set(new_cits)

    ## edges
    edges = subgraph.edges()
    # print edges
    for edge in edges:
        if edge[1]!=pid:
            num_of_ils+=1
    
    outdegree_dict = subgraph.out_degree()

    num_of_le = 0
    num_of_cns = 0
    num_of_nes = 0
    num_of_lc = 0
    num_of_nc = 0


    subject_list = []

    new_les = 0
    new_nes = 0

    ### connector的入度的distribution
    nid_of_connector_dis = defaultdict(int)

    ### late endorser的出度，每年新的late endorser的出度
    le_od_dis = defaultdict(int)

    ### 每个节点在该阶段的角色,主要记录0 normal endorser, 1 late endorser, 2 connector
    node_role = {}

    for nid,od in outdegree_dict:
        # od = outdegree_dict[nid]
        subject_list.extend(com_IDs_subjects.get(nid,[]))

        if od==0:
            continue

        ind = subgraph.in_degree(nid)
        ## late endorser
        if od>1:
            num_of_le+=1
            role = 1

            le_od_dis[od]+=1

            if ind>0:
                num_of_lc+=1
                role = 2

        ## connector
        if ind>0:
            num_of_cns+=1
            nid_of_connector_dis[ind]+=1
            role = 2

        ## normal endorser
        if od == 1:
            if ind==0:
                num_of_nes+=1
                role = 0

            if ind>0:
                num_of_nc +=1
                role = 2


        node_role[nid] = role
        ## 对于每年新的点，有多少点是late endorser, 有多少点是normal endorser, 这两个是互斥的
        if nid in new_cits:

            if od>1:
                new_les +=1
            else:
                new_nes +=1



    late_endorser = num_of_le
    connector = num_of_cns
    norm_endorser = num_of_nes

    subjects = Counter(subject_list)
    num_of_subjects = len(subjects.keys())


    return late_endorser,connector,norm_endorser,depth,num_of_ils,num_of_subjects,subjects,nid_of_connector_dis,new_les,new_nes,num_of_lc,num_of_nc,node_role,le_od_dis


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
    ### WARNING: DEPTH IS SET TO 0, SINCE THE OUTDATE  ====> DONE 
    gen_temporal_stats(highly_cited_papers_ids_years_path,highly_cited_papers_cits_path,highly_cited_citation_cascade,com_IDs_subjects_path)










