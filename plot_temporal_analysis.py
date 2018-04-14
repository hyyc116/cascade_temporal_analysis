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
		values = []
		for age in sorted(age_stat.keys()):
			attrs = age_stats[age]

			ages.append(age)
			values.append(attrs)


		labels = ['numer of citations','late endorser','connector','normal endorser','depth','ICRs$','number of subjects','subjects']
		values = zip(*values)
		
		plt.figure(figsize=(7,5))
		for i,label in enumerate(labels):

			if label == 'depth':
				continue

			if label == 'number of subjects':
				num_of_subjects = values[i]
				continue

			if label == 'subjects':
				subjects = values[i]
				continue

			plt.plot(ages,values[i],label=label,c=color_sequence[i],linewidth=2)


		plt.xlabel('citation delay')
		plt.ylabel('percentage')
		plt.tight_layout()

		plt.savefig('pdf/')



			






