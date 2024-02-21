"""
Main Goal: K-prototypes algorithm on CAMHS (BUPdata) for readmission prediction. 

Script Goal: It uses the gower distance to calculate CISI for all clusters. 

The script is divided into three parts:
    1. Load the data and preprocess
    2. Define the cisi functions
    3. Call CISI function

"""

import warnings

warnings.filterwarnings("ignore")

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

import seaborn as sns
from mpl_toolkits import mplot3d
from mpl_toolkits.mplot3d import Axes3D
from sklearn.decomposition import PCA
from sklearn.preprocessing import LabelEncoder


# Define to load data and preprocess
def load_data_without_diag_med():
    original_df_1 = pd.read_csv("Full_ICD10_ATC.csv")

    # Rename the column var_no_dates_permonth with the Intensity_per_calendar_month
    original_df_1 = original_df_1.rename(
        columns={"var_no_dates_permonth": "SD_CareEvent_PerMonth"}
    )

    # Encoding 'tillnextepisode' into labels: 'not-re-admitted' and time intervals *****
    le = LabelEncoder()
    original_df_1["tillnextepisode"] = le.fit_transform(
        pd.cut(
            original_df_1["tillnextepisode"],
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
    original_df_1.fillna(
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

    # Select columns used to clusters
    without_diag_medic_selected_column_merged_df = original_df_1[
        [
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
        ]
    ]

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

    scaler = StandardScaler()
    without_diag_medic_selected_column_merged_df[numeric_columns] = (
        scaler.fit_transform(
            without_diag_medic_selected_column_merged_df[numeric_columns]
        )
    )

    return without_diag_medic_selected_column_merged_df


def load_data_with_diag_med_as_set():
    original_df_1 = pd.read_csv("Full_ICD10_ATC.csv")

    # Rename the column var_no_dates_permonth with the Intensity_per_calendar_month
    original_df_1 = original_df_1.rename(
        columns={"var_no_dates_permonth": "SD_CareEvent_PerMonth"}
    )

    # Encoding 'tillnextepisode' into labels: 'not-re-admitted' and time intervals *****
    le = LabelEncoder()
    original_df_1["tillnextepisode"] = le.fit_transform(
        pd.cut(
            original_df_1["tillnextepisode"],
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
    original_df_1.fillna(
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

    with_diag_medic_selected_column_merged_df = original_df_1[
        [
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
            "diagnosis",
            "actual_med_Full_ATC",
        ]
    ]

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
    scaler = StandardScaler()
    with_diag_medic_selected_column_merged_df[numeric_columns] = scaler.fit_transform(
        with_diag_medic_selected_column_merged_df[numeric_columns]
    )
    cat_cols = ["diagnosis", "actual_med_Full_ATC"]
    with_diag_medic_selected_column_merged_df[cat_cols] = (
        with_diag_medic_selected_column_merged_df[cat_cols].astype(str)
    )

    return with_diag_medic_selected_column_merged_df


def load_data_with_top20_diag_med():
    original_df_1_Full_ICD10_ATC = pd.read_csv("Full_ICD10_ATC.csv")
    original_df_1 = pd.read_csv("Dummies_ICD10_ATC_20.csv")

    original_df_1_merged_df = pd.merge(
        original_df_1_Full_ICD10_ATC[
            [
                "pasient",
                "episode_id",
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
        ],
        original_df_1,
        on="episode_id",
        how="inner",
    )

    # Rename the column var_no_dates_permonth with the Intensity_per_calendar_month
    original_df_1_merged_df = original_df_1_merged_df.rename(
        columns={"var_no_dates_permonth": "SD_CareEvent_PerMonth"}
    )
    # Encoding 'tillnextepisode' into labels: 'not-re-admitted' and time intervals *****
    le = LabelEncoder()
    original_df_1_merged_df["tillnextepisode"] = le.fit_transform(
        pd.cut(
            original_df_1_merged_df["tillnextepisode"],
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
    original_df_1_merged_df.fillna(
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
        "tillnextepisode",
    ]
    df_by_name = original_df_1_merged_df[cols_by_name]
    df_by_index = original_df_1_merged_df.iloc[:, 19:59]
    with_diag_medic_selected_column_merged_df_top20 = pd.concat(
        [df_by_name, df_by_index], axis=1
    )
    scaler = StandardScaler()
    with_diag_medic_selected_column_merged_df_top20[numeric_columns] = (
        scaler.fit_transform(
            with_diag_medic_selected_column_merged_df_top20[numeric_columns]
        )
    )

    return with_diag_medic_selected_column_merged_df_top20


def load_data_with_top50_diag_med():
    original_df_1_Full_ICD10_ATC = pd.read_csv("Full_ICD10_ATC.csv")
    original_df_1 = pd.read_csv("Dummies_ICD10_ATC_50.csv")

    original_df_1_merged_df = pd.merge(
        original_df_1_Full_ICD10_ATC[
            [
                "pasient",
                "episode_id",
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
        ],
        original_df_1,
        on="episode_id",
        how="inner",
    )

    # Rename the column var_no_dates_permonth with the Intensity_per_calendar_month
    original_df_1_merged_df = original_df_1_merged_df.rename(
        columns={"var_no_dates_permonth": "SD_CareEvent_PerMonth"}
    )
    # Encoding 'tillnextepisode' into labels: 'not-re-admitted' and time intervals *****
    le = LabelEncoder()
    original_df_1_merged_df["tillnextepisode"] = le.fit_transform(
        pd.cut(
            original_df_1_merged_df["tillnextepisode"],
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
    original_df_1_merged_df.fillna(
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
        "tillnextepisode",
    ]
    df_by_name = original_df_1_merged_df[cols_by_name]
    df_by_index = original_df_1_merged_df.iloc[:, 19:119]
    with_diag_medic_selected_column_merged_df_top50 = pd.concat(
        [df_by_name, df_by_index], axis=1
    )
    scaler = StandardScaler()
    with_diag_medic_selected_column_merged_df_top50[numeric_columns] = (
        scaler.fit_transform(
            with_diag_medic_selected_column_merged_df_top50[numeric_columns]
        )
    )

    return with_diag_medic_selected_column_merged_df_top50


def load_data_with_top100_diag_med():
    original_df_1_Full_ICD10_ATC = pd.read_csv("Full_ICD10_ATC.csv")
    original_df_1 = pd.read_csv("Dummies_ICD10_ATC_100.csv")

    original_df_1_merged_df = pd.merge(
        original_df_1_Full_ICD10_ATC[
            [
                "pasient",
                "episode_id",
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
        ],
        original_df_1,
        on="episode_id",
        how="inner",
    )

    # Rename the column var_no_dates_permonth with the Intensity_per_calendar_month
    original_df_1_merged_df = original_df_1_merged_df.rename(
        columns={"var_no_dates_permonth": "SD_CareEvent_PerMonth"}
    )
    # Encoding 'tillnextepisode' into labels: 'not-re-admitted' and time intervals *****
    le = LabelEncoder()
    original_df_1_merged_df["tillnextepisode"] = le.fit_transform(
        pd.cut(
            original_df_1_merged_df["tillnextepisode"],
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
    original_df_1_merged_df.fillna(
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
        "tillnextepisode",
    ]
    df_by_name = original_df_1_merged_df[cols_by_name]
    df_by_index = original_df_1_merged_df.iloc[:, 19:219]
    with_diag_medic_selected_column_merged_df_top100 = pd.concat(
        [df_by_name, df_by_index], axis=1
    )
    scaler = StandardScaler()
    with_diag_medic_selected_column_merged_df_top100[numeric_columns] = (
        scaler.fit_transform(
            with_diag_medic_selected_column_merged_df_top100[numeric_columns]
        )
    )

    return with_diag_medic_selected_column_merged_df_top100


# Define the cisi functions
def cisi_without_diag_med():
    print("*********** without_diag_med *************")
    without_diag_medic_selected_column_merged_df = load_data_without_diag_med()
    print(without_diag_medic_selected_column_merged_df.info())
    for k in range(2, 9):
        kprototypes = KPrototypes(n_clusters=k, init="Huang", random_state=42)
        clusters = kprototypes.fit_predict(
            without_diag_medic_selected_column_merged_df,
            categorical=[0, 1, 2, 3, 4, 5, 16],
        )
        without_diag_medic_selected_column_merged_df["cluster"] = clusters
        print(without_diag_medic_selected_column_merged_df["cluster"].value_counts())

        silhouette = metrics.silhouette_score(
            without_diag_medic_selected_column_merged_df, clusters, metric="euclidean"
        )
        calinski = metrics.calinski_harabasz_score(
            without_diag_medic_selected_column_merged_df, clusters
        )
        print(f"Silhouette score for k={k}: {round(silhouette, 3)}")
        print(f"Calinski-Harabasz score for k={k}: {round(calinski, 3)}")


def cisi_with_diag_med_as_set():
    print("*********** with_diag_med_as_set *************")
    with_diag_medic_selected_column_merged_df = load_data_with_diag_med_as_set()
    print(with_diag_medic_selected_column_merged_df.info())
    for k in range(2, 9):
        kprototypes = KPrototypes(n_clusters=k, init="Huang", random_state=42)
        clusters = kprototypes.fit_predict(
            with_diag_medic_selected_column_merged_df,
            categorical=[0, 1, 2, 3, 4, 5, 16, 17, 18],
        )
        with_diag_medic_selected_column_merged_df["cluster"] = clusters
        print(with_diag_medic_selected_column_merged_df["cluster"].value_counts())
        dist_matrix = gower.gower_matrix(with_diag_medic_selected_column_merged_df)
        silhouette = silhouette_score(dist_matrix, clusters, metric="precomputed")
        calinski = calinski_harabasz_score(dist_matrix, clusters)
        print(f"Silhouette score for k={k}: {round(silhouette, 3)}")
        print(f"Calinski-Harabasz score for k={k}: {round(calinski, 3)}")


def cisi_top20_diag_med():
    print("*********** top20_diag_med *************")
    with_diag_medic_selected_column_merged_df_top20 = load_data_with_top20_diag_med()
    print(with_diag_medic_selected_column_merged_df_top20.info())
    for k in range(2, 9):
        kprototypes = KPrototypes(n_clusters=k, init="Huang", random_state=42)
        clusters = kprototypes.fit_predict(
            with_diag_medic_selected_column_merged_df_top20,
            categorical=[0, 1, 2, 3, 4, 5] + list(range(16, 57)),
        )
        with_diag_medic_selected_column_merged_df_top20["cluster"] = clusters
        print(with_diag_medic_selected_column_merged_df_top20["cluster"].value_counts())
        dist_matrix = gower.gower_matrix(
            with_diag_medic_selected_column_merged_df_top20
        )
        silhouette = silhouette_score(dist_matrix, clusters, metric="precomputed")
        calinski = calinski_harabasz_score(dist_matrix, clusters)
        print(f"Silhouette score for k={k}: {round(silhouette, 3)}")
        print(f"Calinski-Harabasz score for k={k}: {round(calinski, 3)}")


def cisi_with_top50_diag_med():
    print("*********** top50_diag_med *************")
    with_diag_medic_selected_column_merged_df_top50 = load_data_with_top50_diag_med()
    print(with_diag_medic_selected_column_merged_df_top50.info())
    for k in range(2, 9):
        kprototypes = KPrototypes(n_clusters=k, init="Huang", random_state=42)
        clusters = kprototypes.fit_predict(
            with_diag_medic_selected_column_merged_df_top50,
            categorical=[0, 1, 2, 3, 4, 5] + list(range(16, 117)),
        )
        with_diag_medic_selected_column_merged_df_top50["cluster"] = clusters
        print(with_diag_medic_selected_column_merged_df_top50["cluster"].value_counts())
        dist_matrix = gower.gower_matrix(
            with_diag_medic_selected_column_merged_df_top50
        )
        silhouette = silhouette_score(dist_matrix, clusters, metric="precomputed")
        calinski = calinski_harabasz_score(dist_matrix, clusters)
        print(f"Silhouette score for k={k}: {round(silhouette, 3)}")
        print(f"Calinski-Harabasz score for k={k}: {round(calinski, 3)}")


def cisi_with_top100_diag_med():
    print("*********** top100_diag_med *************")
    with_diag_medic_selected_column_merged_df_top100 = load_data_with_top100_diag_med()
    print(with_diag_medic_selected_column_merged_df_top100.info())
    for k in range(2, 9):
        kprototypes = KPrototypes(n_clusters=k, init="Huang", random_state=42)
        clusters = kprototypes.fit_predict(
            with_diag_medic_selected_column_merged_df_top100,
            categorical=[0, 1, 2, 3, 4, 5] + list(range(16, 217)),
        )
        with_diag_medic_selected_column_merged_df_top100["cluster"] = clusters
        print(
            with_diag_medic_selected_column_merged_df_top100["cluster"].value_counts()
        )
        dist_matrix = gower.gower_matrix(
            with_diag_medic_selected_column_merged_df_top100
        )
        silhouette = silhouette_score(dist_matrix, clusters, metric="precomputed")
        calinski = calinski_harabasz_score(dist_matrix, clusters)
        print(f"Silhouette score for k={k}: {round(silhouette, 3)}")
        print(f"Calinski-Harabasz score for k={k}: {round(calinski, 3)}")


# Calls CISI function
cisi_without_diag_med()
cisi_with_diag_med_as_set()
cisi_top20_diag_med()
cisi_with_top50_diag_med()
cisi_with_top100_diag_med()
