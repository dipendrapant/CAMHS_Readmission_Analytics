"""
Main Goal: K-prototypes algorithm on CAMHS (BUPdata) for readmission prediction. 

Script Goal: Take most frequent 20 diagnosis and medication and apply K-prototypes algorithm to cluster the data into 3 clusters. And assign, save the cluster labels and distances to the original data.

The script is divided into two parts:
    1. Load the data and preprocess
    2. Calculate the distance (by calling calc_distance() ) and apply K-prototypes algorithm

"""

import warnings

warnings.filterwarnings("ignore")
import os

import gower
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from dotenv import load_dotenv
from gower import gower_matrix
from IPython.display import Image, display
from kmodes.kprototypes import KPrototypes
from mpl_toolkits import mplot3d
from sklearn import metrics
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import calinski_harabasz_score, silhouette_score
from sklearn.preprocessing import LabelEncoder, StandardScaler


def load_data_with_top20_diag_med():
    original_df_1 = pd.read_csv("Dummies_ICD10_ATC_20.csv")

    original_df_Full_ICD10_ATC = pd.read_csv("Full_ICD10_ATC.csv")

    original_df_1merged_df = original_df_Full_ICD10_ATC[
        [
            "episode_id",
            "pasient",
            "episode_start_date",
            "episode_end_date",
            "gender",
            "age",
            "diagnosis",
            "actual_med_Full_ATC",
            "MiddleChildhood",
            "Preschooler",
            "Teenager",
            "F",
            "M",
            "gender_0",
            "Length_of_Episode",
            "Count_visit",
            "var_no_dates_permonth",
            "num_diagnoses",
            "num_medications",
            "Inpatient_day_ratio",
            "Outpatient_ratio",
            "Therapy_ratio",
            "TreatmentPlanning_ratio",
            "Advisory_ratio",
            "tillnextepisode",
        ]
    ].merge(
        original_df_1,
        on="episode_id",
        how="inner",
    )
    # Rename the column var_no_dates_permonth with the Intensity_per_calendar_month
    original_df_1merged_df = original_df_1merged_df.rename(
        columns={"var_no_dates_permonth": "SD_CareEvent_PerMonth"}
    )
    # Encoding 'tillnextepisode' into labels: 'not-re-admitted' and time intervals *****
    le = LabelEncoder()
    original_df_1merged_df["tillnextepisode_label"] = le.fit_transform(
        pd.cut(
            original_df_1merged_df["tillnextepisode"],
            bins=[float("-inf"), 0, 182, 730, float("inf")],
            labels=[
                "not-re-admitted",
                "re-admitted in 0-182 days",
                "re-admitted in 182-730 days",
                "re-admitted in more than 730 days",
            ],
        )
    )
    # Fillna with zero
    original_df_1merged_df.fillna(
        {
            "num_diagnoses": 0,
            "num_medications": 0,
            "Inpatient_day_ratio": 0,
            "Outpatient_ratio": 0,
            "TreatmentPlanning_ratio": 0,
            "Therapy_ratio": 0,
            "TreatmentPlanning_ratio": 0,
            "Advisory_ratio": 0,
        },
        inplace=True,
    )
    original_df_Full_ICD10_ATC_backup = original_df_1merged_df.copy()

    numeric_columns = [
        "Length_of_Episode",
        "Count_visit",
        "SD_CareEvent_PerMonth",
        "num_diagnoses",
        "num_medications",
        "Inpatient_day_ratio",
        "Outpatient_ratio",
        "Therapy_ratio",
        "TreatmentPlanning_ratio",
        "Advisory_ratio",
    ]
    cols_by_name = [
        "MiddleChildhood",
        "Preschooler",
        "Teenager",
        "F",
        "M",
        "gender_0",
        "Length_of_Episode",
        "Count_visit",
        "SD_CareEvent_PerMonth",
        "num_diagnoses",
        "num_medications",
        "Inpatient_day_ratio",
        "Outpatient_ratio",
        "Therapy_ratio",
        "TreatmentPlanning_ratio",
        "Advisory_ratio",
        "tillnextepisode_label",
    ]

    df_by_name = original_df_1merged_df[cols_by_name]

    df_by_index = original_df_1merged_df.iloc[:, 25:65]
    with_diag_medic_selected_column_merged_df_top20 = pd.concat(
        [df_by_name, df_by_index], axis=1
    )
    scaler = StandardScaler()
    with_diag_medic_selected_column_merged_df_top20[numeric_columns] = (
        scaler.fit_transform(
            with_diag_medic_selected_column_merged_df_top20[numeric_columns]
        )
    )

    print(with_diag_medic_selected_column_merged_df_top20.info())
    return (
        with_diag_medic_selected_column_merged_df_top20,
        original_df_Full_ICD10_ATC_backup,
        original_df_1merged_df,
    )


def calc_distance(X, centroid, categorical):
    distance = 0
    for i in range(len(X)):
        if i in categorical:
            # Simple matching dissimilarity measure for categorical attributes
            distance += X[i] != centroid[i]
        else:
            # Euclidean distance for numerical attributes
            distance += (X[i] - centroid[i]) ** 2
    return np.sqrt(distance)


def with_with_top20_diag_med():
    (
        with_diag_medic_selected_column_merged_df_top20,
        original_df_Full_ICD10_ATC_backup,
        original_df_1merged_df,
    ) = load_data_with_top20_diag_med()

    categorical = [0, 1, 2, 3, 4, 5] + list(range(16, 57))
    print("******** With Diagnosis & Medication using gower distance ******** \n")
    kprototypes = KPrototypes(n_clusters=3, init="Huang", random_state=42)
    clusters = kprototypes.fit_predict(
        with_diag_medic_selected_column_merged_df_top20,
        categorical=categorical,
    )
    print(with_diag_medic_selected_column_merged_df_top20.info())

    distances = []
    for i in range(len(with_diag_medic_selected_column_merged_df_top20)):
        centroid = kprototypes.cluster_centroids_[kprototypes.labels_[i]]
        distance = calc_distance(
            with_diag_medic_selected_column_merged_df_top20.values[i],
            centroid,
            categorical,
        )
        distances.append(distance)

    # Assign the list to the column
    original_df_Full_ICD10_ATC_backup["cluster"] = clusters
    original_df_Full_ICD10_ATC_backup["cluster_distances"] = distances
    merged_df = original_df_Full_ICD10_ATC_backup[
        [
            "pasient",
            "episode_id",
            "episode_start_date",
            "episode_end_date",
            "gender",
            "age",
            "diagnosis",
            "actual_med_Full_ATC",
            "MiddleChildhood",
            "Preschooler",
            "Teenager",
            "F",
            "M",
            "gender_0",
            "Length_of_Episode",
            "Count_visit",
            "SD_CareEvent_PerMonth",
            "num_diagnoses",
            "num_medications",
            "Inpatient_day_ratio",
            "Outpatient_ratio",
            "Therapy_ratio",
            "TreatmentPlanning_ratio",
            "Advisory_ratio",
            "tillnextepisode",
            "tillnextepisode_label",
            "cluster",
            "cluster_distances",
        ]
    ]
    merged_df.to_csv(
        "Cluster3Label_Full_ICD10_ATC_Dummies_ICD10_ATC_20.csv",
        index=False,
    )


with_with_top20_diag_med()
