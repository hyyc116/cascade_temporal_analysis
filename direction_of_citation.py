#coding:utf-8

'''
	Tasks in this script:

	 1. based on the pid_cits, get co-citation pair


'''


def co_citation_pair(pid_cits_path):
	logging.info("build co-citation pair from {:} .".format(pid_cits_path))

	pid_refs = defaultdict(list)
	pid_count = defaultdict(int)

	for line in open(pid_cits_path):

		line = line.strip()
		pid,citing_id = line.split("\t")

		if pid =='' or citing_id=='' or pid is None or citing_id is None:
			continue

		pid_refs[citing_id].append(pid)
		pid_count[pid]+=1

	open('data/pid_count.json','w').write(json.dumps(pid_count))
	logging.info('data saved to data/pid_count.json.')


	refkey_dict = defaultdict(int)
	for pid in pid_refs.keys():

		refs = pid_refs[pid]

		for i,ref1 in enumerate(refs):
			for ref2 in refs[i+1:]:
				key = '\t'.join(sorted([ref1,ref2]))

				refkey_dict[key] +=1

	open('data/refkey_dict.json','w').write(json.dumps(refkey_dict))

	logging.info('data saved to data/refkey_dict.json')


if __name__ == '__main__':
	pid_cits_path = 'data/pid_cits.txt'
	co_citation_pair(pid_cits_path)

