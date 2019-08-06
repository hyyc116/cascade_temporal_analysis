#coding:utf-8
'''
buyi的指标，使用mag

SELECT * FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema';
 mag_core   | affiliations                         |
 mag_core   | journals                             |
 mag_core   | conference_series                    |
 mag_core   | conference_instances                 |
 mag_core   | papers                               |
 mag_core   | paper_resources                      |
 mag_core   | fields_of_study                      |
 mag_core   | related_field_of_study               |
 mag_core   | paper_urls                           |
 mag_core   | paper_abstract_inverted_index        |
 mag_core   | paper_author_affiliations            |
 mag_core   | authors                              |
 mag_core   | paper_citation_contexts              |
 mag_core   | paper_fields_of_study                |
 mag_core   | paper_languages                      |
 mag_core   | paper_recommendations                |
 mag_core   | paper_references                     |
 mag_core   | fields_of_study_children             |


'''
from basic_config import *

### 使用mag的数据进行作者的合作机构以及合作者的数量随时间的变化曲线
def test_author_collaborators():

    author_names = []
    for line in open('test_authors.csv'):
        line = line.strip()

        secondname,firstname,field = line.split(',')[0:3]

        author_names.append('{:} {:}'.format(firstname,secondname))

    author_names= set(author_names)
    print(author_names)

    query_op = dbop()

    sql = 'select author_id,display_name,last_known_affiliation_id,paper_count from mag_core.authors'

    authors = []
    for author_id,display_name,last_known_affiliation_id,paper_count in query_op.query_database(sql):

        if display_name.strip() in author_names and last_known_affiliation_id.strip()!='' and paper_count>10:

            authors.append('{},{},{}'.format(author_id,display_name,last_known_affiliation_id))


    open('data/authors.txt','w').write('\n'.join(authors))

    print(len(authors))



def author_papers():

    authors = []

    for line in open('data/authors.txt'):
        authors.append(line.split(',')[0])

    authors = set(authors)

    sql = 'select author_id,paper_id from mag_core.paper_author_affiliations'

    query_op = dbop()

    papers_ids = []
    for author_id,paper_id in query_op.query_database(sql):

        if str(author_id) in authors:

            papers_ids.append(str(paper_id))


    open('data/author_papers.txt','w').write('\n'.join(papers_ids))



if __name__ == '__main__':
    # test_author_collaborators()

    author_papers()












