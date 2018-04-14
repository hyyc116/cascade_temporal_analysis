#coding:utf-8

'''
    Plot all attrs in One figure:

        1. number of citations changes over age
        2. late endorser changes over time
        3. connector distribution over time
        4. normal endorser changes over time
        5. Indirect links changes over time
        6. subjects changes over time

        other:

        1 depth: cannot plot
        2 Homophily 
        3 hidden influential

'''

from basic_config import *

def plot_curve(highly_cited_paper_age_stat_path):

	highly_cited_paper_age_stat = json.loads(open(highly_cited_paper_age_stat_path).read())

	for pid in highly_cited_paper_age_stat.keys():
		age_stat = highly_cited_paper_age_stat[pid]

		ages = []

		for age in sorted(age_stat.keys()):
			noc,late_endorser,connector,norm_endorser,depth,num_of_ils,num_of_subjects,subjects = 
