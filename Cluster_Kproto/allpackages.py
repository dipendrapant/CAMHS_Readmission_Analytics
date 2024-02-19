"""
Main Goal: K-prototypes algorithm on CAMHS (BUPdata) for readmission prediction. 

Script Goal: Imports all the packages used. 

"""

import warnings

warnings.filterwarnings("ignore")

import math
import os
import random

import gower
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from gower import gower_matrix
from IPython.display import Image, display
from kmodes.kprototypes import KPrototypes
from sklearn import metrics
from sklearn.cluster import KMeans
from sklearn.metrics import calinski_harabasz_score, silhouette_score
from sklearn.preprocessing import StandardScaler

load_dotenv()

import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import scipy.stats as stats
import seaborn as sns
from mpl_toolkits import mplot3d

# Import the Axes3D module from mpl_toolkits
from mpl_toolkits.mplot3d import Axes3D
from plotly.subplots import make_subplots
from scipy.stats import gaussian_kde
from sklearn.decomposition import PCA
from sklearn.preprocessing import LabelEncoder
