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

    query_op = dbop()

    sql = 'select author_id,display_name,last_known_affiliation_id from mag_core.authors'

    auhtors = []
    for author_id,display_name,last_known_affiliation_id in query_op.query_database(sql):

        if display_name.strip() in author_names:

            authors.append('{},{},{}'.format(author_id,display_name,last_known_affiliation_id))


    open('data/authors.txt','w').write('\n'.join(authors))

    print(len(authors))



if __name__ == '__main__':
    test_author_collaborators()












