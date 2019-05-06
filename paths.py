#coding:utf-8

## 定义需要保存的路径

class PATHS:

    def __init__(self,field):

        self.field = field

        self.name = '_'.join(field.split())

        self.selected_IDs_path = 'data/selected_IDs_from_{:}.txt'.format(self.name)

        self.com_IDs_path = 'data/com_IDs_{:}.txt'.format(self.name)

        self.pid_cits_path = 'data/pid_cits_{:}.txt'.format(self.name)

        self.cascade_path = 'data/cascade_{:}.txt'.format(self.name)

        self.cascade_bak_path = 'data/cascade_{:}_bak.txt'.format(self.name)

        self.paper_year_path = 'data/pubyear_{:}.json'.format(self.name)

        self.all_subcasdes_path = 'subcascade/data/all_subcascades_{:}.json'.format(self.name)

        self.paper_subcascades_path = 'subcascade/data/paper_subcascades_{:}.json'.format(self.name)

        self.radical_num_dis_path = 'subcascade/data/radical_num_dis_{:}.json'.format(self.name)

        self.paper_cit_num = 'data/paper_cit_num_{:}.json'.format(self.name)

        ###  figure path and fig data path
        self._f_radical_num_dis_path = 'subcascade/fig/radical_num_dis_{:}.jpg'.format(self.name)
        self._fd_radical_num_dis_path = 'subcascade/fig/data/radical_num_dis_{:}.json'.format(self.name)

        ## number of componets
        self._f_num_of_comps_path = 'subcascade/fig/num_of_comps_{:}.jpg'.format(self.name)
        self._fd_num_of_comps_path = 'subcascade/fig/data/num_of_comps_{:}.txt'.format(self.name)

        ## max size
        self._f_maxsize_of_comps_path = 'subcascade/fig/maxsize_of_comps_{:}.jpg'.format(self.name)
        self._fd_maxsize_of_comps_path = 'subcascade/fig/data/maxsize_of_comps_{:}.txt'.format(self.name)

        ## 不同size的sub-cascade的比例分布
        self._f_size_percent_path = 'subcascade/fig/size_percent_{:}.jpg'.format(self.name)
        self._fd_size_percent_path = 'subcascade/fig/data/size_percent_{:}.json'.format(self.name)

        ## 直接相连的结点所占的比例
        self._f_0_percent_path = 'subcascade/fig/direct_connected_percentage_{:}.jpg'.format(self.name)
        self._fd_0_percent_path = 'subcascade/fig/data/direct_connected_percentage_{:}.txt'.format(self.name)

        ## subcascade citation distritbuion
        self._f_citation_distribution_path = 'subcascade/fig/citation_distribution_{:}.jpg'.format(self.name)
        self._fd_citation_distribution_path = 'subcascade/fig/data/citation_distribution_{:}.json'.format(self.name)

        ## slice distribution
        self._f_slice_distribution_path = 'subcascade/fig/slice_distribution_{:}.jpg'.format(self.name)
        self._fd_slice_distribution_path = 'subcascade/fig/data/slice_distribution_{:}.json'.format(self.name)



