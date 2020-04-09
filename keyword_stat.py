#coding:utf-8
from basic_config import *
def read_keywords():
	query_op = dbop()
    sql = 'select id,keyword_id,keyword from wos_core.wos_keywords'
    progress=0
    pid_keywords = defaultdict(list)
    saved_path = 'data/pid_keywords.json'
    keywords = []
    os.remove(saved_path) if os.path.exists(saved_path) else None
    for _id,keyword_id,keyword in query_op.query_database(sql):
    	progress+=1
    	pid_keywords[_id].append(keyword)
    	keywords.append(keyword)

    	if progress%1000000==0:
    		logging.info('progress:{} ...'.format(progress))


    keywords = list(set(keywords))

    logging.info('Number of keywords {} in {} papers.'.format(len(keywords),len(pid_keywords.keys())))

    open(saved_path,'w').write(json.dumps(pid_keywords))

    logging.info('pid_keywords saved to {}'.format(saved_path))

    open('data/wos_keywords.txt','w').write('\n'.join(keywords))

    logging.info('pid_keywords saved to data/wos_keywords.txt')


if __name__ == '__main__':
	read_keywords()

