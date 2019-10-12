#coding:utf-8
'''
不同类型论文cascade的node角色分布

'''
from basic_config import *

## 根据cascade的出度入度对node的角色进行分析
def cascade_role(pathObj):

    cc_path = pathObj.cascade_path
    progress = 0
    owner_count = 0
    pid_role_dict = defaultdict(dict)

    for line in open(cc_path):

        line = line.strip()

        citation_cascade = json.loads(line)

        for pid in citation_cascade.keys():

            progress+=1

            if progress%100000==0:
                logging.info('progress report {:} ...'.format(progress))

            edges = citation_cascade[pid]

            ## 创建graph
            dig  = nx.DiGraph()
            dig.add_edges_from(edges)

            # if citation cascade is not acyclic graph
            if not nx.is_directed_acyclic_graph(dig):
                continue

            ## 根据出度以及入度对结点的角色进行分析
            node_count = 0 
            connector_count = 0
            le_count = 0
            ie_count = 0
            for nid,od in dig.out_degree():

                ## 出度为0的是owner
                if od==0:
                    owner_count+=1
                else:
                    node_count+=1
                    ## 如果大于0，表示是endoser的一种
                    ind = dig.in_degree(nid)
                    
                    if ind==0 and od==1:
                        ie_count+=1

                    if od>1:
                        le_count+=1

                    if ind>0 and od>0:
                        connector_count+=1

            pc = connector_count/float(node_count)
            ple = le_count/float(node_count)
            pie = ie_count/float(node_count)

            pid_role_dict[pid]['pc'] = pc
            pid_role_dict[pid]['ple'] = ple
            pid_role_dict[pid]['pie'] = pie

    open(pathObj._node_role_dict_path,'w').write(json.dumps(pid_role_dict))
    logging.info('data saved to {}.'.format(pathObj._node_role_dict_path))


if __name__ == '__main__':
    field = 'ALL'
    paths = PATHS(field)
    cascade_role(paths)






