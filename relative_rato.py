#coding:utf-8
from basic_config import *
from skmisc.loess import loess


'''
    
    1. 计算所有学科的每一篇论文 本领域引用与全领域引用的比例
    2. 不同领域的RR的分布
    3. 分高中低 的箱式图
    4. 随着citation count的变化的变化曲线
    5. 随时间的变化曲线

    6 计算与size_of_component，num_of_component


'''

def cal_correlation():

    field = 'ALL'
    pathObj = PATHS(field)

    logging.info('loading paper subcascades  ...')
    paper_size_id=json.loads(open(pathObj.paper_subcascades_path).read())

    logging.info('loading paper relative_ratio ...')
    pid_rr = json.loads(open('data/pid_relative_ratio.json').read())

    nums = []
    rrs = []
    sizes = []

    for pid in paper_size_id.keys():

        rr = pid_rr.get(pid,None)

        if rr is None:
            continue

        num = 0
        ss = []
        for size in paper_size_id[pid].keys():
            num+=len(paper_size_id[pid][size])
            ss.extend([int(size)]*len(paper_size_id[pid][size]))

        avgSize = np.mean(ss)


        rrs.append(rr)
        nums.append(num)
        sizes.append(avgSize)

    r,p = scipy.stats.spearmanr(rrs,nums)
    logging.info(f'rr vs num:{r},{p}')

    r,p = scipy.stats.spearmanr(rrs,sizes)
    logging.info(f'rr vs size:{r},{p}')

    r,p=scipy.stats.spearmanr(sizes,nums)
    logging.info(f'size vs num:{r},{p}')



def plot_rr_figure_data():


    pid_topsubjs,pid_pubyear,pid_cn = load_basic_data(['topsubj','year','cn'])

    pid_rr = json.loads(open('data/pid_relative_ratio.json').read())


    field_rrs = defaultdict(list)

    field_year_rrs = defaultdict(lambda:defaultdict(list))

    field_cn_rrs = defaultdict(lambda:defaultdict(list))


    for pid in pid_rr.keys():

        rr = pid_rr[pid]

        for topsubj in pid_topsubjs[pid]:

            field_rrs[topsubj].append(rr)

            field_year_rrs[topsubj][pid_pubyear[pid]].append(rr)

            field_cn_rrs[topsubj][pid_cn[pid]].append(rr)


    open('data/field_rrs.json','w').write(json.dumps(field_rrs))
    logging.info('data saved to data/field_rrs.json.')

    open('data/field_year_rrs.json','w').write(json.dumps(field_year_rrs))
    logging.info('data saved to data/field_year_rrs.json')

    open('data/field_cn_rrs.json','w').write(json.dumps(field_cn_rrs))
    logging.info('data saved to data/field_cn_rrs.json')


## use local weighted regression to fit data
def loess_data(xs,ys):

    ixes = range(len(xs))

    sorted_xs = []
    sorted_ys = []

    for ix in sorted(ixes,key=lambda x:xs[x]):

        sorted_xs.append(xs[ix])
        sorted_ys.append(ys[ix])

    l = loess(sorted_xs,sorted_ys)
    l.fit()

    pred_x = sorted(list(set(sorted_xs)))
    pred = l.predict(pred_x, stderror=True)
    conf = pred.confidence()

    lowess = pred.values
    ll = conf.lower
    ul = conf.upper

    return pred_x,lowess,ll,ul

def plot_rr_figure():
    logging.info('start to cal field_rrs ...')
    field_rrs = json.loads(open('data/field_rrs.json').read())

    plt.figure(figsize=(6,4))

    for subj in sorted(field_rrs.keys()):
        xs,ccdf = cdf(field_rrs[subj])

        plt.plot(xs,ccdf,label=subj)

    plt.legend(prop={'size':6})

    plt.xlabel('relative ratio')
    plt.ylabel('probability')

    # plt.xscale('log')
    # plt.yscale('log')

    plt.tight_layout()

    plt.savefig('fig/rr_ccdf.png',dpi=300)
    logging.info('data saved to fig/rr_ccdf.png')

    # 不同field随year的变化
    field_year_rrs = json.loads(open('data/field_year_rrs.json').read())
    plt.figure(figsize=(6,4))
    for subj in sorted(field_year_rrs.keys()):
        xs = []
        ys = []
        for year in sorted(field_year_rrs[subj].keys(),key=lambda x:int(x)):
            xs.append(int(year))
            ys.append(np.mean(field_year_rrs[subj][year]))

        plt.plot(xs,ys,label=subj)

    plt.legend(prop={'size':6})

    plt.xlabel('year')
    plt.ylabel('relative ratio')
    # plt.yscale('log')


    plt.tight_layout()

    plt.savefig('fig/field_year_rrs.png',dpi=300)
    logging.info('data saved to fig/field_year_rrs.png')

    MAXMIN,MINMAX = minmax_maxmin()
    field_cls_rrs = defaultdict(lambda:defaultdict(list))
    # 不同field随year的变化
    field_cn_rrs = json.loads(open('data/field_cn_rrs.json').read())
    plt.figure(figsize=(6,4))
    for subj in sorted(field_cn_rrs.keys()):
        xs = []
        ys = []
        for cn in sorted(field_cn_rrs[subj].keys(),key=lambda x:int(x)):

            if int(cn)<MAXMIN:
                CLS = 0

            elif int(cn)<MINMAX:
                CLS = 1
            else:
                CLS = 2

            field_cls_rrs[subj][CLS].extend(field_cn_rrs[subj][cn])

            xs.append(int(cn))
            ys.append(np.mean(field_cn_rrs[subj][cn]))
        

        # new_ys = []

        # for i in range(len(ys)):
        #     start = i-100 if i-100>0 else 0
        #     end = i+5 if i+5<=len(ys) else len(ys)

        #     new_ys.append(np.mean(ys[start:end]))

        xs,new_ys,_,_  = lowess_data(xs,ys)
        plt.plot(xs,new_ys,label=subj)

    plt.legend(prop={'size':6})

    plt.xlabel('number of citations')



    plt.ylabel('relative ratio')

    plt.xscale('log')
    # plt.yscale('log')


    plt.tight_layout()
# 
    plt.savefig('fig/field_cn_rrs.png',dpi=300)
    logging.info('data saved to fig/field_cn_rrs.png')

    fig,axes = plt.subplots(3,2,figsize=(12,12))
    for i,subj in enumerate(list(sorted(field_cls_rrs.keys()))):
        data = []

        for CLS in sorted(field_cls_rrs[subj].keys()):

            data.append(field_cls_rrs[subj][CLS])

        print(subj,len(data))

        ax = axes[int(i/2)][int(i%2)]

        ax.boxplot(data,labels=['lowly cited','medium cited','highly cited'],showfliers=True)

        ax.set_xlabel('Paper Impact Level')
        ax.set_ylabel('relative ratio')

        # ax.set_yscale('log')

        # ax.set_ylabel()
        ax.set_title('{}'.format(subj))

    plt.tight_layout()

    plt.savefig('fig/rr_boxplot.png',dpi=400)
    logging.info('fig saved to fig/rr_boxplot.png')


def minmax_maxmin():

    id_num = json.loads(open('data/paper_cit_num_ALL.json').read())

    total = len(id_num)
    logging.info('number of papers {}.'.format(total))

    citnums = sorted(id_num.values(),reverse=True)

    maxmin_index = int(total/2)

    minmax_index = int(total*0.05)

    maxmin = citnums[maxmin_index]
    minmax = citnums[minmax_index]

    logging.info('maxmin:{}, minmax:{}'.format(maxmin,minmax))

    return maxmin,minmax

def cdf(data):

    v_counter = Counter(data)

    length = len(data)
    xs = []
    ys = []
    for x in sorted(v_counter):
        xs.append(x)
        ys.append(v_counter[x])

    ccdf = []
    for i,x in enumerate(xs):
        ccdf.append(np.sum(ys[i:])/float(length))

    return xs,ccdf




def stat_relative_ratio():
    # 加载基本数据
    pid_topsubjs,pid_pubyear,pid_cn = load_basic_data(['topsubj','year','cn'])


    ref_citations = defaultdict(list)
    progress=0
    for line in open('../WOS_data_processing/data/pid_refs.txt'):
        line = line.strip()
        pid_refs = json.loads(line)
        logging.info(f'progress {progress} ..')
        for pid in pid_refs.keys():

            topsubjs = pid_topsubjs[pid]

            if int(pid_pubyear[pid])>2016 or int(pid_pubyear[pid])<1900:
                continue

            for ref in pid_refs[pid]:

                ref_citations[ref].append(topsubjs)


    logging.info('processing done, start to cal relative ratio')

    pid_rr = {}

    for ref in ref_citations.keys():

        topsubjs = set(pid_topsubjs[ref])

        focal_num = len([1 for subjs in ref_citations[ref] if len(topsubjs&set(subjs))>0]) 

        relative_ratio = focal_num/float(len(ref_citations[ref]))

        pid_rr[ref] = relative_ratio


    open('data/pid_relative_ratio.json','w').write(json.dumps(pid_rr))

    logging.info('data saved to data/pid_relative_ratio.json.')


def load_basic_data(attrs=['year','subj','topsubj','teamsize','doctype','cn'],isStat=False):

    logging.info('======== LOADING BASIC DATA =============')
    logging.info('======== ================== =============')

    results = {}

    if 'year' in attrs:

        logging.info('loading paper pubyear ...')
        pid_pubyear = json.loads(open('../WOS_data_processing/data/pid_pubyear.json').read())
        logging.info('{} papers has year label.'.format(len(pid_pubyear.keys())))

        results['year']=pid_pubyear

    if 'subj' in attrs:
        logging.info('loading paper subjects ...')
        pid_subjects = json.loads(open('../WOS_data_processing/data/pid_subjects.json').read())
        logging.info('{} papers has subject label.'.format(len(pid_subjects.keys())))

        results['subj'] = pid_subjects

    if 'topsubj' in attrs:
        logging.info('loading paper top subjects ...')
        pid_topsubjs = json.loads(open('../WOS_data_processing/data/pid_topsubjs.json').read())
        logging.info('{} papers has top subject label.'.format(len(pid_topsubjs.keys())))
        
        results['topsubj']=pid_topsubjs


    if 'teamsize' in attrs:

        logging.info('loading paper teamsize ...')
        pid_teamsize = json.loads(open('../WOS_data_processing/data/pid_teamsize.json').read())
        logging.info('{} papers has teamsize label.'.format(len(pid_teamsize.keys())))

        results['teamsize'] = pid_teamsize

    if 'doctype'  in attrs:

        logging.info('loading paper doctype ...')
        pid_doctype = json.loads(open('../WOS_data_processing/data/pid_doctype.json').read())
        logging.info('{} papers has doctype label.'.format(len(pid_doctype.keys())))

        results['doctype'] = pid_doctype

    
    if 'c5' in attrs:

        logging.info('loading paper citation c5 ...')
        pid_cn = json.loads(open('../WOS_data_processing/data/pid_c5.json').read())
        logging.info('{} papers has c5 label.'.format(len(pid_cn.keys())))

        results['c5']=pid_cn

    if 'c10' in attrs:

        logging.info('loading paper citation c10 ...')
        pid_cn = json.loads(open('../WOS_data_processing/data/pid_c10.json').read())
        logging.info('{} papers has c10 label.'.format(len(pid_cn.keys())))

        results['c10']=pid_cn

    if 'cn' in attrs:

        logging.info('loading paper citation count ...')
        pid_cn = json.loads(open('../WOS_data_processing/data/pid_cn.json').read())
        logging.info('{} papers has citation count label.'.format(len(pid_cn.keys())))

        results['cn']=pid_cn

    if isStat:
        interset = set(pid_pubyear.keys())&set(pid_teamsize.keys())&set(pid_topsubjs.keys())&set(pid_topsubjs.keys())
        logging.info('{} papers has both four attrs.'.format(len(interset)))

    logging.info('======== LOADING BASIC DATA DONE =============')
    logging.info('======== ======================= =============')


    if len(attrs)>=1:
        
        return [results[attr] for attr in attrs]

    else:
        return None



if __name__ == '__main__':
    # stat_relative_ratio()

    # plot_rr_figure_data()

    plot_rr_figure()

    # cal_correlation()