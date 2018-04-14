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

def plot_curve_of_all_attrs(highly_cited_paper_age_stat_path):
	logging.info('loading highly cited papers age statistics ...')
	highly_cited_paper_age_stat = json.loads(open(highly_cited_paper_age_stat_path).read())

	logging.info('plotting ...')	
	for pid in highly_cited_paper_age_stat.keys():
		logging.info('plot {:} ...'.format(pid))

		age_stat = highly_cited_paper_age_stat[pid]

		ages = []
		values = []
		for age in sorted(age_stat.keys()):
			attrs = age_stats[age]

			ages.append(age)
			values.append(attrs)


		labels = ['numer of citations','late endorser','connector','normal endorser','depth','ICRs','number of subjects','subjects']
		values = zip(*values)
		
		fig,axes = plt.subplots(1,2,figsize=(14,5))
		ax = axes[0]
		for i,label in enumerate(labels):

			if label == 'depth':
				continue

			if label == 'number of subjects':
				num_of_subjects = values[i]
				continue

			if label == 'subjects':
				subjects = values[i]
				continue

			ax.plot(ages,values[i],label=label,c=color_sequence[i],linewidth=2)


		ax.set_xlabel('citation delay')
		ax.set_ylabel('percentage')

		ax2 = axes[1]

		ax2.plot(ages,num_of_subjects,c=color_sequence[2])
		ax2.set_xlabel('ciattion delay')
		ax2.set_ylabel('number of subjects')
		plt.tight_layout()

		plt.savefig('pdf/high_cascade/{:}.jpg'.format(pid.replace(':','_')),dpi=400)
		logging.info('saved to pdf/high_cascade/{:}.jpg ...'.format(pid.replace(':','_')))

	
	logging.info('Done')

if __name__ == '__main__':
	highly_cited_paper_age_stat_path = 'data/highly_cited_paper_age_stats.json'
	plot_curve_of_all_attrs(highly_cited_paper_age_stat_path)



			






