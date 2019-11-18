#coding:utf-8

from basic_config import *

def same_journal():

    sql = 'select a.id,a.vol,b.title from wos_core.wos_summary as a,wos_core.wos_titles as b where a.id=b.id and b.title_id!=6;'

    query_op = dbop()

    existing_ids = set([line.strip().split('======')[0] for line in open('wos_id.txt')])

    logging.info("{} wos id loaded.".format(len(existing_ids)))


    pid_jvol = {}
    jvol_pid = defaultdict(list)
    ## 第一次查询，得到已有id的期刊 卷期
    logging.info('query data base for journal vol ...')
    progress = 0
    for wos_id,vol,journal_title in query_op.query_database(sql):

        progress+=1

        if progress%100000==0:
            logging.info("progress {}, {} ids journal vol found.".format(progress,len(pid_jvol)))

        if wos_id in existing_ids:
            jvol = '{}=={}'.format(journal_title,vol)
            pid_jvol[wos_id]= jvol
            jvol_pid[jvol].append(wos_id)

    logging.info('id journal vol query done, {} ids journal vol found.'.format(len(pid_jvol)))


    logging.info('query data base for same journal vol ids...')

    progress = 0
    ## 第二次查询，得到同期的期刊的论文id
    for wos_id,vol,journal_title in query_op.query_database(sql):

        progress+=1

        if progress%1000000==0:
            logging.info("progress {}, {} ids journal vol found.".format(progress,len(pid_jvol)))


        jvol = '{}=={}'.format(journal_title,vol)
        if jvol_pid.get(jvol,None) is not None:
            jvol_pid[jvol].append(wos_id)

    ## 查询完成后,存储相关关系
    lines = ['pid,pid_in_same_journal']
    for pid in pid_jvol.keys():

        jvol = pid_jvol[pid]

        ##得到相同期刊论文id

        same_pids = jvol_pid[jvol]

        for same_pid in same_pids:

            line = '{},{}'.format(pid,same_pid)

            lines.append(line)

    open('data/in_same_journal.txt','w').write('\n'.join(lines))

    logging.info('data saved to data/in_same_journal.txt.')


if __name__ == '__main__':
    same_journal()


































