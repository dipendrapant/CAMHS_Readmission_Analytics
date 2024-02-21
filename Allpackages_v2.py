import warnings
warnings.filterwarnings("ignore")

import math
import os
import random

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
# from dotenv import load_dotenv
# from gower import gower_matrix
from IPython.display import Image, display
from kmodes.kprototypes import KPrototypes
from sklearn import metrics
from sklearn.cluster import KMeans
from sklearn.metrics import calinski_harabasz_score, silhouette_score
from sklearn.preprocessing import StandardScaler

import seaborn as sns
from mpl_toolkits import mplot3d

# Import the Axes3D module from mpl_toolkits
from mpl_toolkits.mplot3d import Axes3D
from sklearn.decomposition import PCA

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import kaleido
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from xgboost import XGBClassifier
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.model_selection import TimeSeriesSplit
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.tree import export_graphviz
import graphviz
from sklearn.impute import SimpleImputer
from sklearn.metrics import make_scorer, balanced_accuracy_score, f1_score
from sklearn.utils.class_weight import compute_sample_weight
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
from imblearn.over_sampling import SMOTE
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
from imblearn.over_sampling import RandomOverSampler
import random
random_seed = 42
random.seed(random_seed)
import plotly.express as px


import plotly.graph_objects as go
import warnings
warnings.filterwarnings("ignore")

import math
import os
import random

from IPython.display import Image, display
from sklearn.preprocessing import LabelEncoder
import plotly.io as pio






