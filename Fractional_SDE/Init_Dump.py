#!/usr/bin/env python
# coding: utf-8

# # Initialization Dump
# 
# **Note:** Some Modules may be re-loaded multiple times but this is intentional so as to make clear which script has which dependancies!


# In[1]:


# Alert(s)
import smtplib

# Compression
from scipy import sparse
from scipy.sparse import random as randsp
from scipy.sparse import csr_matrix

# CV
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold

# DL: Tensorflow
import tensorflow as tf
from keras.utils.layer_utils import count_params
from tensorflow.python.framework import ops # Custome Tensorflow Functions
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Dense, Input
# DL: Tensorflow - Keras
from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasRegressor
from keras import backend as K
from sklearn.compose import TransformedTargetRegressor

# Evaluation
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Forests (Random)
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor


# Formatting:
import pandas as pd
import numpy as np
import itertools

# Gaussian Process Regressor
from sklearn.model_selection import *
from sklearn.ensemble import *
from sklearn.gaussian_process import *

# Learning
from sklearn.cluster import KMeans

# Optimal Transport
import ot
# Optimization
from scipy.optimize import minimize

# Pre-Processing
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
from sklearn import preprocessing

# Random Forest & Gradient Boosting (Arch. Construction)
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor

# Simulation
from fbm import FBM

# Statistics
from scipy import stats
from sklearn.mixture import GaussianMixture

# Structuring
from pathlib import Path

# Visulatization
import matplotlib.pyplot as plt
# necessary for 3d plot even if not used
from mpl_toolkits.mplot3d import Axes3D  # noqa
from matplotlib.collections import PolyCollection  # noqa
from tqdm import tqdm
import seaborn as sns
sns.set()

# Writing, Reading, Exporting, and Importing
#from sklearn.externals import joblib
import pickle

# Timing
import time

# Misc
import gc
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
import os
import math
from scipy.stats import norm
from itertools import compress
import copy
from operator import itemgetter 
from itertools import compress


# ## Regression

# In[2]:


# Overall Use
import numpy as np
import pandas as pd

# For Initialization of Initial Radius
from scipy.spatial.distance import pdist, squareform

# For Plotting
import matplotlib.pyplot as plt

# For Signaling User With Noise(s)
import os

# For Random Colouring
import random

# path expansion and existance checking
from pathlib import Path

# Training Test Split
from sklearn.model_selection import train_test_split


### LASSO
from sklearn.linear_model import LassoCV


# ## Random Lipschitz Partition

# In[3]:


# Geometric Stuff
from scipy.spatial import distance_matrix

# Overall Use
import numpy as np
import pandas as pd

# For Initialization of Initial Radius
from scipy.spatial.distance import pdist, squareform

# For Plotting
import matplotlib.pyplot as plt

# For Signaling User With Noise(s)
import os
import sys
import warnings

# For Random Colouring
import random

# path expansion and existance checking
from pathlib import Path

# Training Test Split
from sklearn.model_selection import train_test_split

# Vanilla
from sklearn.linear_model import Ridge

# ## Helper Function(s)

# #### General Helper Function(s)

# In[4]:


def check_path(path):
    path = os.path.expanduser(path)
    if not os.path.exists(path):
        Path(path).mkdir(parents=True, exist_ok=True)
    return(path)


# #### Helper Function for Random Lipschitz Partitioning

# In[5]:


# Function for Testing Random Partition
def is_in_random_ball(x_test,center,radius_in):
    TF_val = bool (np.linalg.norm((x_test-center), ord=1)<radius_in)
    return TF_val

# Delta (Radius...Deterministic Hyperparameter Part...)
def init_delta(X_train):
    X_train_subsample = X_train.loc[np.random.choice(X_train.index, 100, replace=False)]
    dis_sample = pdist(X_train_subsample , 'minkowski', p=1)
    radius_delta_init = np.mean(dis_sample)/2
    
    return radius_delta_init


# ## Set Seed(s)

# In[6]:


random.seed(2020)
np.random.seed(2020)


# ---
# NN Dependancies
# ---

# DL: Tensorflow
import tensorflow as tf
from keras.utils.layer_utils import count_params
# Tf - Optimizers
from tensorflow.keras.optimizers import Adam
# DL: Tensorflow - Keras
from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasRegressor
from keras import backend as K

# Grid-Search and CV
from sklearn.model_selection import RandomizedSearchCV, KFold
from keras.wrappers.scikit_learn import KerasRegressor
from sklearn.pipeline import Pipeline
from keras.models import Sequential
from keras.layers import Dense, Dropout
from sklearn.metrics import mean_absolute_error, mean_squared_error
import os
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, RepeatedStratifiedKFold

# Linear Algebra
from scipy.linalg import expm

# Model(s)
## Basic Model(s)
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression

# Prepreocessing
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn import preprocessing


# Misc.
import math
import pandas as pd
import numpy as np
from time import process_time, time
import gc
from sklearn.pipeline import Pipeline




# System and packup
import os
import argparse
import pickle
import warnings




# ## Initialize Output Path(s)

# In[15]:

Path('./outputs/models/').mkdir(parents=True, exist_ok=True)
# Vanilla Benchmark(s)
Path('./outputs/models/ffNNs/').mkdir(parents=True, exist_ok=True)
# LaTeX and misc. output(s)
Path('./outputs/plots/').mkdir(parents=True, exist_ok=True)
Path('./outputs/tables/').mkdir(parents=True, exist_ok=True)
Path('./outputs/results/').mkdir(parents=True, exist_ok=True)
Path('./outputs/results/Final_Results/').mkdir(parents=True, exist_ok=True)


# ---
# # Fin
# ---