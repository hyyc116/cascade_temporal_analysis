#coding:utf-8

'''
    Tasks in this script:

        1. select physics papers IDs from WOS as selected_IDs
        2. get all citing papers' ID of these papers as citing_IDs
        3. combine these two IDs as com_IDs
        4. get all citing papers of these com_IDs
        5. build citation cascade for every paper in selected_IDs

'''
## task 1

from basic_config import *

def filter_out_ids_of_field(field):
    logging.info('filter out paper ids from wos_subjects of field:[{:}].'.format(field))
    selected_IDs = []
    
    ## query database 
    query_op = dbop()

    sql = 'select id,subject from wos_subjects'

    progress = 0
    for fid,subject in query_op.query_database(sql):
        progress+=1
        if progress%10000000==0:
            logging.info('progress {:} .... ' .format(progress))

            
        if field in subject.lower():
            selected_IDs.append(str(fid))

    query_op.close_db()
    selected_IDs = list(set(selected_IDs))
    saved_path = 'data/selected_IDs_from_{:}.txt'.format(field)
    open(saved_path,'w').write('\n'.join(selected_IDs))
    logging.info('number of papers belong to field [{:}] is [{:}] out of total {:} papers, and saved to {:}.'.format(field,len(selected_IDs),progress,saved_path))

def fetch_ids_of_citing_papers(selected_IDs_path):
    logging.info('fetch citing papers of selected IDs ...')


    selected_IDs = set([line.strip() for line in open(selected_IDs_path)])

    logging.info('{:} selected IDs from {:}.'.format(len(selected_IDs),selected_IDs_path))


    total = len(selected_IDs)

    query_op = dbop()
    sql = 'select id,ref_id from wos_references'
    progress=0
    sub_progress = 0
    citing_IDs = []

    has_citations = []

    for pid,ref_id in query_op.query_database(sql):
        progress+=1
        if progress%10000000==0:
            logging.info('total progress {:} ...'.format(progress))
        
        if ref_id in selected_IDs:

            has_citations.append(ref_id)
            citing_IDs.append(pid)

    query_op.close_db()


    logging.info('{:} selected_IDs has 1 more citations.'.format(len(set(has_citations))))

    citing_IDs = list(set(citing_IDs))

    saved_path = 'data/citing_IDs.txt'

    open(saved_path,'w').write('\n'.join(citing_IDs))

    logging.info('{:} citing IDs are saved to {:}'.format(len(citing_IDs),saved_path))


    ## combine IDs

    com_IDs = []

    com_IDs.extend(selected_IDs)
    com_IDs.extend(citing_IDs)

    com_IDs = list(set(com_IDs))

    saved_path = 'data/com_IDs.txt'
    open(saved_path,'w').write('\n'.join(com_IDs))
    logging.info('{:} combine IDs are saved to {:}'.format(len(com_IDs),saved_path))


def fetch_citing_papers_of_com_IDs(com_IDs_path):

    logging.info('fetch citing papers of selected IDs ...')


    com_IDs = set([line.strip() for line in open(com_IDs_path)])

    logging.info('{:} selected IDs from {:}.'.format(len(com_IDs),com_IDs_path))

    query_op = dbop()
    sql = 'select id,ref_id from wos_references'
    progress=0
    sub_progress = 0
    pid_cits = []
    for pid,ref_id in query_op.query_database(sql):
        progress+=1
        if progress%10000000==0:
            logging.info('total progress {:} ...'.format(progress))
        
        if ref_id in com_IDs:
            pid_cits.append('{:}\t{:}'.format(ref_id,pid))

    query_op.close_db()

    saved_path = 'data/pid_cits.txt'
    open(saved_path,'w').write('\n'.join(pid_cits))
    logging.info('{:} citing relations are saved to {:}'.format(len(pid_cits),saved_path))

def build_cascade_from_pid_cits(pid_cits_path,selected_IDs_path):

    selected_IDs = [line.strip() for line in open(selected_IDs_path)]

    logging.info("build cascade from {:} .".format(pid_cits_path))

    pid_citations = defaultdict(list)
    for line in open(pid_citations):
        ## line format: pid \t citing_id
        line = line.strip()
        pid,citing_id = line.split("\t")

        pid_citations[pid].append(citing_id)

    logging.info('citation relation loaded, start to build cascade ...')

    progress = 0

    citation_cascade = defaultdict(list)

    for pid in selected_IDs:
        progress+=1

        if progress%100000==0:
            logging.info('Building progress {:}/{:} ...'.format(progress,len(selected_IDs)))

        citing_list = set(pid_citations.get(pid,[]))

        if len(citing_list)==0:
            continue

        for cit in citing_list:

            if pid == cit:
                continue

            citation_cascade[pid].append([cit,pid])

            ## if cit has no citation
            cit_citation_list = set(pid_citations.get(cit,[]))

            if len(cit_citation_list)==0:
                continue

            for inter_pid in citing_list & cit_citation_list:
                citation_cascade[pid].append([inter_pid,cit])

    saved_path = 'data/citation_cascade.json'
    open(saved_path,'w').write(json.dumps(saved_path))
    logging.info("{:} citation cascade has been build, and saved to {:}".format(len(citation_cascade.keys()),saved_path))


if __name__ == '__main__':
    ## task 1
    filter_out_ids_of_field('physics')

    ## task 2 and task 3
    selected_IDs_path = 'data/selected_IDs_from_physics.txt'
    fetch_ids_of_citing_papers(selected_IDs_path)

    ## task 4
    com_IDs_path = 'data/com_IDs.txt'
    fetch_citing_papers_of_com_IDs(com_IDs_path)

    ## task 5
    pid_cits_path = 'data/pid_cits.txt'
    build_cascade_from_pid_cits(pid_cits_path,selected_IDs_path)












