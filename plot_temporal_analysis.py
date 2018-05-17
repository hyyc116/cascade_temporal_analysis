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
		accumulative_indicators  = []
		incremental_indicators = []
		for age in sorted([int(a) for a  in age_stats.keys()]):
			attrs = age_stats[str(age)]

			ages.append(age)
			accumulative_indicators.append(attrs['accumulative'])
			incremental_indicators.append(attrs['incremental'])

		labels = ['number of citations','late endorser','connector','normal endorser','depth','ICRs','number of subjects','subjects','in degree distribution']
		accumulative_values = zip(*accumulative_indicators)
		incremental_values = zip(*incremental_indicators)
		## 画的图分为两列，左边是accumulative的图， 右边是incremental的图
		fig,axes = plt.subplots(6,2,figsize=(12,30))
		
		## 第一行， number of citations
		ax00 = axes[0,0]
		ax00.plot(ages,accumulative_values[0])
		ax00.set_xlabel('citation delay')
		ax00.set_ylabel('number of citations')
		ax00.set_title('accumulative')

		ax01 = axes[0,1]
		ax01.plot(ages,incremental_values[0])
		ax01.set_xlabel('citation delay')
		ax01.set_ylabel('number of citations')
		ax01.set_title('incremental')

		##第二行，三种不同的endorser的比例变化
		ax10 = axes[1,0]
		ax10.plot(ages,accumulative_values[1],label=labels[1])
		ax10.plot(ages,accumulative_values[2],label=labels[2])
		ax10.plot(ages,accumulative_values[3],label=labels[3])
		ax10.plot(ages,accumulative_values[-1],label='normal endorser and connector')
		ax10.plot(ages,accumulative_values[-2],label='late endorser and connector')

		ax10.set_xlabel('citation delay')
		ax10.set_ylabel('percentage of endorsers')
		ax10.legend()

		ax11 = axes[1,1]
		ax11.plot(ages,incremental_values[1],label=labels[1])
		ax11.plot(ages,incremental_values[2],label=labels[2])
		ax11.plot(ages,incremental_values[3],label=labels[3])

		ax11.set_xlabel('citation delay')
		ax11.set_ylabel('percentage of endorsers')
		ax11.legend()

		##第三行， 领域的数量
		ax20 = axes[2,0]
		ax20.plot(ages,accumulative_values[6])
		ax20.set_xlabel('citation delay')
		ax20.set_ylabel('number of subjects')
		
		ax21 = axes[2,1]
		ax21.plot(ages,incremental_values[5])
		ax21.set_xlabel('citation delay')
		ax21.set_ylabel('number of subjects')

		## 第四行，indirect links的数量
		ax30 = axes[3,0]
		ax30.plot(ages,accumulative_values[5])
		ax30.set_xlabel('citation delay')
		ax30.set_ylabel('ICRs')
		
		ax31 = axes[3,1]
		ax31.plot(ages,incremental_values[4])
		ax31.set_xlabel('citation delay')
		ax31.set_ylabel('ICRs')

		## 第五行，分别画出最后一年的的in degree distribution

		ax40 = axes[4,1]
		last_ind_dis = accumulative_values[-3][-1]
		xs = []
		ys = []
		for ind in sorted(last_ind_dis.keys()):
			xs.append(ind)
			ys.append(last_ind_dis[ind])

		ax40.plot(xs,ys,'o',c=color_sequence[0],fillstyle='none')
		ax40.set_xlabel('Indegree of connectors')
		ax40.set_ylabel('#(connectors)')
		# ax40.set_title('Last year')
		ax40.set_xscale('log')
		ax40.set_yscale('log')
		
		##connector的degree distribution，将每年带来80% indirect links的数量的曲线画出来
		## 确定在后面是新的late endorser

		ax41 = axes[4,0]
		ind_dises= accumulative_values[-3]
		ys = []
		for ind_dis in ind_dises:

			## 计算超过80%的个数
			total_ind = np.sum(ind_dis.values())
			nc = 0
			count=0
			for ind in sorted(ind_dis.keys(),key = lambda x:ind_dis[x], reverse=True):
				nc+=ind_dis[ind]
				count+=1
				if nc/float(total_ind)>0.8:
					break
			ys.append(count)

		ax41.plot(ages,ys)
		ax41.set_xlabel('citation delay')
		ax41.set_ylabel('#(connectors)')
		# ax41.set_title('mid year')
		# ax41.set_yscale('log')
		# ax41.set_xscale('log')


		### normal endorser, late endorser 转换成 connector 需要的时间
		node_roles = accumulative_values[-4]
		nid_roles = defaultdict(list)
		for nr in node_roles:
			for nid in nr.keys():

				nid_roles[nid].append(nr[nid])

		changes_role_times = defaultdict(list)
		for nid in nid_roles.keys():
			roles = nid_roles[nid]
			initial_role = roles[0]
			cy = 0
			for i,role in enumerate(roles):

				if role==2:
					cy = i
					break

			changes_role_times[initial_role].append(cy)


		## 对于两种角色转换成connector所需要的时间分布

		normal_endorser_times = Counter(changes_role_times[0])

		xs = []
		ys = []
		for time in sorted(normal_endorser_times.keys()):
			xs.append(time)
			ys.append(normal_endorser_times[time])

		ax50 = axes[5,0]

		ax50.plot(xs,ys,'o',fillstyle='none')
		ax50.set_xlabel('years for conversion')
		ax50.set_ylabel('#(normal endorser)')
		ax50.set_xscale('log')
		ax50.set_yscale('log')

		late_endorser_times = Counter(changes_role_times[1])

		xs = []
		ys = []
		for time in sorted(late_endorser_times.keys()):
			xs.append(time)
			ys.append(late_endorser_times[time])

		ax51 = axes[5,1]

		ax51.plot(xs,ys,'o',fillstyle='none')
		ax51.set_xlabel('years for conversion')
		ax51.set_ylabel('#(late endorser)')
		ax51.set_xscale('log')
		ax51.set_yscale('log')

		plt.savefig('pdf/high_cascade/{:}.jpg'.format(pid.replace(':','_')),dpi=400)
		logging.info('saved to pdf/high_cascade/{:}.jpg ...'.format(pid.replace(':','_')))

	
	logging.info('Done')

if __name__ == '__main__':
	highly_cited_paper_age_stat_path = 'data/highly_cited_paper_age_stats.json'
	plot_curve_of_all_attrs(highly_cited_paper_age_stat_path)



			






