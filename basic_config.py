#coding:utf-8
import os
import sys
import json
from collections import defaultdict
from collections import Counter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score
import math
import numpy as np
import random
import logging
import networkx as nx
from itertools import combinations
import pylab
import itertools
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import spline
from multiprocessing.dummy import Pool as ThreadPool
from networkx.algorithms import isomorphism
from matplotlib import cm as CM
from collections import Counter
from scipy.signal import wiener
import matplotlib as mpl
from matplotlib.patches import Circle
from matplotlib.patheffects import withStroke
import matplotlib.colors as colors
from matplotlib.colors import LogNorm
from matplotlib.colors import LinearSegmentedColormap
from networkx.algorithms.core import core_number
from networkx.algorithms.core import k_core
import psycopg2

# from gini import gini


mpl.rcParams['agg.path.chunksize'] = 10000


color_sequence = ['#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c',
                  '#98df8a', '#d62728', '#ff9896', '#9467bd', '#c5b0d5',
                  '#8c564b', '#c49c94', '#e377c2', '#f7b6d2', '#7f7f7f',
                  '#c7c7c7', '#bcbd22', '#dbdb8d', '#17becf', '#9edae5']

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',level=logging.DEBUG)
PREFIX='all'
PROGRAM_ID='cascade'
FIGDIR='pdf'
DATADIR='data'

params = {'legend.fontsize': 8,
         'axes.labelsize': 15,
         'axes.titlesize':20,
         'xtick.labelsize':15,
         'ytick.labelsize':15}
pylab.rcParams.update(params)


## 定义需要保存的路径

class PATHS:

    def __init__(self,field):

        self.field = field

        self.name = '_'.join(field.split())

        self.selected_IDs_path = 'data/selected_IDs_from_{:}.txt'.format(self.name)

        self.com_IDs_path = 'data/com_IDs_{:}.txt'.format(self.name)

        self.pid_cits_path = 'data/pid_cits_{:}.txt'.format(self.name)

        self.cascade_path = 'data/cascade_{:}.txt'.format(self.name)

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


def circle(ax,x,y,radius=0.15):

    circle = Circle((x, y), radius, clip_on=False, zorder=10, linewidth=1,
                    edgecolor='black', facecolor=(0, 0, 0, .0125),
                    path_effects=[withStroke(linewidth=5, foreground='w')])
    ax.add_artist(circle)

def power_low_func(x,a,b):
    return b*(x**(-a))

def exponential_func(x,a,b):
    return b*np.exp(-a*x)

def square_x(x,a,b,c):
  return a*pow(x,2)+b*x+c

def autolabel(rects,ax,total_count=None,step=1,):
    """
    Attach a text label above each bar displaying its height
    """
    for index in np.arange(len(rects),step=step):
        rect = rects[index]
        height = rect.get_height()
        # print height
        if not total_count is None:
            ax.text(rect.get_x() + rect.get_width()/2., 1.005*height,
                    '{:}\n({:.6f})'.format(int(height),height/float(total_count)),
                    ha='center', va='bottom')
        else:
            ax.text(rect.get_x() + rect.get_width()/2., 1.005*height,
                    '{:}'.format(int(height)),
                    ha='center', va='bottom')


class dbop:

    def __init__(self,insert_index=0):
        
        self._insert_index=insert_index
        self._insert_values=[]
        logging.debug("connect database with normal cursor.")
        self._db = psycopg2.connect(database='wos_core_3',user="huanyong",password = "pendulum_wist_estival")    
        self._cursor = self._db.cursor()



    def query_database(self,sql):
        self._cursor.close()
        self._cursor = self._db.cursor()
        self._cursor.execute(sql)
        logging.debug("query database with sql {:}".format(sql))
        return self._cursor

    def insert_database(self,sql,values):
        self._cursor.close()
        self._cursor = self._db.cursor()
        self._cursor.executemany(sql,values)
        logging.debug("insert data to database with sql {:}".format(sql))
        self._db.commit()
        

    def batch_insert(self,sql,row,step,is_auto=True,end=False):
        if end:
            if len(self._insert_values)!=0:
                logging.info("insert {:}th data into database,final insert.".format(self._insert_index))
                self.insert_database(sql,self._insert_values)
        else:
            self._insert_index+=1
            if is_auto:
                row[0] = self._insert_index
            self._insert_values.append(tuple(row))
            if self._insert_index%step==0:
                logging.info("insert {:}th data into database".format(self._insert_index))
                self.insert_database(sql,self._insert_values)
                self._insert_values=[]

    def get_insert_count(self):
        return self._insert_index

    def execute_del_update(self,sql):
        self._cursor.execute(sql)
        self._db.commit()
        logging.debug("execute delete or update sql {:}.".format(sql))

    def execute_sql(self,sql):
        self._cursor.execute(sql)
        self._db.commit()
        logging.debug("execute sql {:}.".format(sql))

    def close_db(self):
        self._db.close()



def plot_line_from_data(fig_data,ax=None):

    xs = fig_data['x']
    ys = fig_data['y']
    title = fig_data['title']
    xlabel = fig_data['xlabel']
    ylabel = fig_data['ylabel']
    marker = fig_data['marker']
    xscale = fig_data.get('xscale','linear')
    yscale = fig_data.get('yscale','linear')


    if ax is None:

        plt.plot(xs,ys,marker)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.xscale(xscale)
        plt.yscale(yscale)
        plt.title(title)
        plt.tight_layout()

    else:

        ax.plot(xs,ys,marker)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.set_xscale(xscale)
        ax.set_yscale(yscale)



def plot_multi_lines_from_data(fig_data,ax=None):

    xs = fig_data['x']
    yses = fig_data['ys']
    title = fig_data['title']
    xlabel = fig_data['xlabel']
    ylabel = fig_data['ylabel']
    markers = fig_data['markers']
    labels = fig_data['labels']
    xscale = fig_data.get('xscale','linear')
    yscale = fig_data.get('yscale','linear')


    if ax is None:
        for i,ys in enumerate(yses):
            plt.plot(xs,ys,markers[i],label=labels[i])
        
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.xscale(xscale)
        plt.yscale(yscale)
        plt.title(title)
        plt.legend()
        plt.tight_layout()

    else:
        for i,ys in enumerate(yses):
            ax.plot(xs,ys,markers[i],label=labels[i])

        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.set_xscale(xscale)
        ax.set_yscale(yscale)
        ax.legend()


def plot_multi_lines_from_two_data(fig_data,ax=None):

    xses = fig_data['xs']
    yses = fig_data['ys']
    title = fig_data['title']
    xlabel = fig_data['xlabel']
    ylabel = fig_data['ylabel']
    markers = fig_data['markers']
    labels = fig_data['labels']
    xscale = fig_data.get('xscale','linear')
    yscale = fig_data.get('yscale','linear')

    if ax is None:
        for i,ys in enumerate(yses):
            plt.plot(xses[i],ys,markers[i],label=labels[i])
        
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.xscale(xscale)
        plt.yscale(yscale)
        plt.title(title)
        plt.legend()
        plt.tight_layout()

    else:
        for i,ys in enumerate(yses):
            ax.plot(xses[i],ys,markers[i],label=labels[i])

        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.set_xscale(xscale)
        ax.set_yscale(yscale)
        ax.legend()














