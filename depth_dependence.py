#coding:utf-8

from basic_config import *

## 计算后面所需要用到的所有数据
def cal_data(pathObj):

    logging.info('loading _id_subjects ...')
    _id_subjects = json.loads(open(pathObj.paper_id_topsubj).read())

    logging.info('loading _id_pubyear ...')
    _id_pubyear = json.loads(open(pathObj.paper_year_path).read())

    ## 一篇论文的被引
    pid_citations = defaultdict(set)
    ## 一篇论文的参考
    pid_refs = defaultdict(set)
    progress = 0

    for line in open(pathObj.pid_cits_path):

        progress+=1

        if progress%10000000==0:
            logging.info('reading %d citation relations....' % progress)

        line = line.strip()
        pid,citing_id = line.split("\t")



        pid_citations[pid].add(citing_id)

        pid_refs[citing_id].add(pid)

    logging.info('stating all data ..')
    ## 计算文章的值
    attr_subj_list = defaultdict(lambda:defaultdict(list))

    progress = 0
    total = len(pid_citations.keys())
    for pid in pid_citations.keys():

        progress+=1

        if progress%10000000==0:
            logging.info('stating data %d/%d ....' % (progress,total))

        if int(_id_pubyear.get(pid,9999))>2016:
            continue

        subjects = _id_subjects.get(pid,None)

        if subjects is None:
            continue

        citing_ids = pid_citations[pid]
        refs = pid_refs[pid]

        ## CP
        cp = len(citing_ids)

        ## R(citing_pubs), R(cited pubs)

        R_citings = []
        R_citeds = []
        TR_citings = 0
        TR_citeds = 0

        for citing_id in citing_ids:

            c_refs = pid_refs[citing_id]

            ## R_citing是引证文献与其参考文献共引本文的篇数
            R_citing = len(c_refs&citing_ids)
            ## R_cited 是本文与引证文献共同参考文献的数量
            R_cited = len(c_refs&refs)

            R_citings.append(R_citing)
            R_citeds.append(R_cited)

            TR_citings +=R_citing
            TR_citeds += R_cited

        cp_r_citing_e0 = len([r for r in R_citings if r==0])
        cp_r_citing_g0 = len([r for r in R_citings if r>0])

        cp_r_cited_e0 = len([r for r in R_citeds if r==0])
        cp_r_cited_g0 = len([r for r in R_citeds if r>0])

        pcp_r_citing_e0 = cp_r_citing_e0/float(cp)
        pcp_r_citing_g0 = cp_r_citing_g0/float(cp)

        pcp_r_cited_e0 = cp_r_cited_e0/float(cp)
        pcp_r_cited_g0 = cp_r_cited_g0/float(cp)

        MR_citings = TR_citings/float(cp)
        MR_citeds = TR_citeds/float(cp)

        # line = [cp,cp_r_citing_e0,cp_r_citing_g0,TR_citings,cp_r_cited_e0,cp_r_cited_g0,TR_citeds,pcp_r_citing_e0,pcp_r_citing_g0,MR_citings,pcp_r_cited_e0,pcp_r_cited_g0,MR_citeds]

        # lines.append(line)



        for subj in subjects:

            attr_subj_list['cp'][subj].append(cp)
            attr_subj_list['cp_r_citing_e0'][subj].append(cp_r_citing_e0)
            attr_subj_list['cp_r_citing_g0'][subj].append(cp_r_citing_g0)
            attr_subj_list['cp_r_cited_e0'][subj].append(cp_r_cited_e0)
            attr_subj_list['cp_r_cited_g0'][subj].append(cp_r_cited_g0)
            attr_subj_list['TR_citings'][subj].append(TR_citings)
            attr_subj_list['TR_citeds'][subj].append(TR_citeds)

            attr_subj_list['pcp_r_citing_e0'][subj].append(pcp_r_citing_e0)
            attr_subj_list['pcp_r_citing_g0'][subj].append(pcp_r_citing_g0)
            attr_subj_list['pcp_r_cited_e0'][subj].append(pcp_r_cited_e0)
            attr_subj_list['pcp_r_cited_g0'][subj].append(pcp_r_cited_g0)

            attr_subj_list['MR_citings'][subj].append(MR_citings)
            attr_subj_list['MR_citeds'][subj].append(MR_citeds)



        attr_subj_list['cp']['WOS_ALL'].append(cp)
        attr_subj_list['cp_r_citing_e0']['WOS_ALL'].append(cp_r_citing_e0)
        attr_subj_list['cp_r_citing_g0']['WOS_ALL'].append(cp_r_citing_g0)
        attr_subj_list['cp_r_cited_e0']['WOS_ALL'].append(cp_r_cited_e0)
        attr_subj_list['cp_r_cited_g0']['WOS_ALL'].append(cp_r_cited_g0)
        attr_subj_list['TR_citings']['WOS_ALL'].append(TR_citings)
        attr_subj_list['TR_citeds']['WOS_ALL'].append(TR_citeds)

        attr_subj_list['pcp_r_citing_e0']['WOS_ALL'].append(pcp_r_citing_e0)
        attr_subj_list['pcp_r_citing_g0']['WOS_ALL'].append(pcp_r_citing_g0)
        attr_subj_list['pcp_r_cited_e0']['WOS_ALL'].append(pcp_r_cited_e0)
        attr_subj_list['pcp_r_cited_g0']['WOS_ALL'].append(pcp_r_cited_g0)

        attr_subj_list['MR_citings']['WOS_ALL'].append(MR_citings)
        attr_subj_list['MR_citeds']['WOS_ALL'].append(MR_citeds)

    ##
    open('data/all_dd.json','w').write(json.dumps(attr_subj_list))

    logging.info('statting done.')


def plot_dd():

    attr_subj_list = json.loads(open('data/all_dd.json').read())


    cp_subj_list = attr_subj_list['cp']
    headline = 'attr$stats${}'.format('$'.join(sorted(cp_subj_list.keys())))
    lines = [headline]

    fig,ax = plt.subplots(figsize=(5,4))
    xlabel='CP'
    mean_line,median_line = plot_attr_cdf(cp_subj_list,ax,xlabel)
    lines.append(mean_line)
    lines.append(median_line)
    plt.tight_layout()
    plt.savefig('fig/dd_cp_cdf_dis.png',dpi=400)
    logging.info('fig saved to fig/dd_cp_cdf_dis.png')


    attr_names= ['cp_r_citing_e0','cp_r_citing_g0','cp_r_cited_e0','cp_r_cited_g0','TR_citings','TR_citeds']
    attr_labels = ['CP(R[cting pub]=0)','CP(R[citing pub]>0)','CP(R[cited pub]=0)','CP(R[cited pub]>0)','TR citings','TR citeds']


    levels = attr_subj_list['cp']['WOS_ALL']
    depths = attr_subj_list['MR_citings']['WOS_ALL']
    dependence = attr_subj_list['MR_citeds']['WOS_ALL']

    import scipy.stats.pearsonr as pearson
    import scipy.stats.spearmanr as spearmanr
    print 'level depth','level dependence','depth dependence'
    print spearmanr(levels,depths)[0],spearmanr(levels,dependence)[0],spearmanr(depths,dependence)[0]

    print pearson(levels,depths)[0],pearson(levels,dependence)[0],pearson(depths,dependence)[0]



    ## 每一个属性画CDF
    fig,axes = plt.subplots(3,2,figsize=(10,12))
    for i,attr_name in enumerate(attr_names):

        ax = axes[i/2,i%2]

        subj_list = attr_subj_list[attr_name]
        xlabel = attr_labels[i]

        mean_line,median_line = plot_attr_cdf(subj_list,ax,xlabel)

        ax.set_xlim(0.9,1000)

        lines.append(mean_line)
        lines.append(median_line)

    plt.tight_layout()

    plt.savefig('fig/dd_cpt_cdf_dis.png',dpi=400)
    logging.info('fig saved to fig/dd_cpt_cdf_dis.png')

    open('data/cp_data.txt','w').write('\n'.join(lines))
    logging.info('data saved to data/cp_data.txt')

    lines = [headline]

    attr_names= ['pcp_r_citing_e0','pcp_r_citing_g0','pcp_r_cited_e0','pcp_r_cited_g0','MR_citings','MR_citeds']
    attr_labels = ['PCP(R[cting pub]=0)','PCP(R[citing pub]>0)','PCP(R[cited pub]=0)','PCP(R[cited pub]>0)','MR citings','MR citeds']

    ## 每一个属性画CDF
    fig,axes = plt.subplots(3,2,figsize=(10,12))
    for i,attr_name in enumerate(attr_names):

        logging.info(attr_name)

        ax =axes[i/2,i%2]

        subj_list = attr_subj_list[attr_name]
        xlabel = attr_labels[i]

        mean_line,median_line = plot_attr_cdf(subj_list,ax,xlabel,True)

        lines.append(mean_line)
        lines.append(median_line)

    plt.tight_layout()

    plt.savefig('fig/dd_pcpt_cdf_dis.png',dpi=400)
    logging.info('fig saved to fig/dd_pcpt_cdf_dis.png')

    open('data/pcp_data.txt','w').write('\n'.join(lines))
    logging.info('data saved to data/pcp_data.txt')

    ## 首先画出一个平均值是如何变化的





def plot_attr_cdf(subj_list,ax,xlabel,isF=False):

    means = []
    medians = []
    for subj in sorted(subj_list.keys()):

        attr_list = subj_list[subj]

        means.append(np.mean(attr_list))
        medians.append(np.median(attr_list))
        # medians.append(0)


        # if subj=='WOS_ALL':
        #     continue

        xs,ys = cdf(attr_list,isF)

        ax.plot(xs,ys,label='{}'.format(subj))


    ax.set_xlabel('{}'.format(xlabel))
    ax.set_ylabel('CDF')

    ax.set_xscale('log')

    if xlabel=='CP':
        ax.set_yscale('log')
    # else:
    #     if isF:
    #         ax.set_xlim(0.001,100)
    #     else:
    #         ax.set_xlim(1,1000)

    ax.legend()

    mean_line = '{}$mean${}'.format(xlabel,'$'.join([str(a) for a in means]))
    median_line = '{}$meidan${}'.format(xlabel,'$'.join([str(a) for a in medians]))


    return mean_line,median_line

def cdf(alist,isF =False):

    alist = [round(a,3) for a in alist]

    a_counter = Counter(alist)


    xs = []
    ys = []
    for a in sorted(a_counter.keys()):

        if a==0:
            continue

        xs.append(a)
        ys.append(a_counter[a])

    ys = [np.sum([ys[:i+1]])/float(np.sum(ys)) for i in range(len(ys))]

    return xs,ys

if __name__ == '__main__':

    field = 'ALL'
    paths = PATHS(field)
    # cal_data(paths)
    plot_dd()














