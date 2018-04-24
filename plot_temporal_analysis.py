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

		age_stats = highly_cited_paper_age_stat[pid]

		ages = []
		values = []
		for age in sorted([int(a) for a  in age_stats.keys()]):
			attrs = age_stats[str(age)]

			ages.append(age)
			values.append(attrs)


		labels = ['number of citations','late endorser','connector','normal endorser','depth','ICRs','number of subjects','subjects','late endorser','connector','normal endorser','depth','ICRs','number of subjects']
		values = zip(*values)
		
		fig,axes = plt.subplots(2,3,figsize=(17,10))
		ax1 = axes[0,1]
		for i,label in enumerate(labels[:7]):

			if label == 'depth':
				continue

			if label == 'number of subjects':
				num_of_subjects = values[i]
				continue

			if label == 'subjects':
				subjects = values[i]
				continue

			if label == 'ICRs':
				ICRs = values[i]
				continue

			if label == 'number of citations':
				cits = values[i]
				continue

			ax1.plot(ages,values[i],label=label,linewidth=2)

		ax1.set_xlabel('citation delay')
		ax1.set_ylabel('percentage')
		ax1.legend()

		ax = axes[0,0]
		ax.plot(ages,cits)
		ax1.set_xlabel('citation delay')
		ax1.set_ylabel('percentage of citations')

		ax2 = axes[1,0]

		ax2.plot(ages,num_of_subjects,c=color_sequence[2],label='accumulative')
		ax2.set_xlabel('ciattion delay')
		ax2.set_ylabel('number of subjects')
		plt.tight_layout()

		ax3 = axes[1,1]
		ax3.plot(ages,ICRs,c=color_sequence[2],label='accumulative')
		ax3.set_xlabel('ciattion delay')
		ax3.set_ylabel('ICRs')
		plt.tight_layout()

		ax1 = axes[0,2]
		for i in range(8,len(labels)):
			label = labels[i]
			if label == 'depth':
				continue

			if label == 'number of subjects':
				num_of_subjects = values[i]
				continue

			if label == 'subjects':
				subjects = values[i]
				continue

			if label == 'ICRs':
				ICRs = values[i]
				continue

			if label == 'number of citations':
				cits = values[i]
				continue

			ax1.plot(ages,values[i],label=label,c=color_sequence[i],linewidth=2)

		ax1.set_xlabel('citation delay')
		ax1.set_ylabel('incremental percentage')
		ax1.legend()

		ax2.plot(ages,num_of_subjects,c=color_sequence[3],label='incremental')
		ax3.plot(ages,ICRs,c=color_sequence[3],label='incremental')

		ax2.legend()
		ax3.legend()
		plt.savefig('pdf/high_cascade/{:}.jpg'.format(pid.replace(':','_')),dpi=400)
		logging.info('saved to pdf/high_cascade/{:}.jpg ...'.format(pid.replace(':','_')))

	
	logging.info('Done')

if __name__ == '__main__':
	highly_cited_paper_age_stat_path = 'data/highly_cited_paper_age_stats.json'
	plot_curve_of_all_attrs(highly_cited_paper_age_stat_path)



			






