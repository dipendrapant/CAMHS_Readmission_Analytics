"""
Main Goal: K-prototypes algorithm on CAMHS (BUPdata) for readmission prediction. 

Script Goal: It calculated the elbow for all clusters. 

The script is divided into three parts:
    1. Load the data and preprocess
    2. Define the elbow functions
    3. Call and plot the elbow function

"""

import warnings

warnings.filterwarnings("ignore")

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
    print(without_diag_medic_selected_column_merged_df.info())
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
    print(with_diag_medic_selected_column_merged_df.info())
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
    print(with_diag_medic_selected_column_merged_df_top20.info())
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
    print(with_diag_medic_selected_column_merged_df_top50.info())
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
    print(with_diag_medic_selected_column_merged_df_top100.info())
    return with_diag_medic_selected_column_merged_df_top100


# Define the elbow functions
def elbow_without_diag_med():
    without_diag_medic_selected_column_merged_df = load_data_without_diag_med()

    k_range = range(2, 9)
    costs = []
    for k in k_range:
        kprototypes = KPrototypes(n_clusters=k, init="Huang", random_state=42)
        kprototypes.fit(
            without_diag_medic_selected_column_merged_df,
            categorical=[0, 1, 2, 3, 4, 5, 16],
        )
        costs.append(kprototypes.cost_)
    return k_range, costs


def elbow_with_diag_med_as_set():
    with_diag_medic_selected_column_merged_df = load_data_with_diag_med_as_set()

    k_range = range(2, 9)
    costs = []
    for k in k_range:
        kprototypes = KPrototypes(n_clusters=k, init="Huang", random_state=42)
        kprototypes.fit(
            with_diag_medic_selected_column_merged_df,
            categorical=[0, 1, 2, 3, 4, 5, 16, 17, 18],
        )
        costs.append(kprototypes.cost_)
    return k_range, costs


def elbow_top20_diag_med():
    with_diag_medic_selected_column_merged_df_top20 = load_data_with_top20_diag_med()

    k_range = range(2, 9)
    costs = []
    for k in k_range:
        km = KPrototypes(n_clusters=k, init="Huang", random_state=42)
        km.fit(
            with_diag_medic_selected_column_merged_df_top20,
            categorical=[0, 1, 2, 3, 4, 5] + list(range(16, 57)),
        )
        costs.append(km.cost_)
    return k_range, costs


def elbow_with_top50_diag_med():
    with_diag_medic_selected_column_merged_df_top50 = load_data_with_top50_diag_med()

    k_range = range(2, 9)
    costs = []
    for k in k_range:
        km = KPrototypes(n_clusters=k, init="Huang", random_state=42)
        km.fit(
            with_diag_medic_selected_column_merged_df_top50,
            categorical=[0, 1, 2, 3, 4, 5] + list(range(16, 117)),
        )
        costs.append(km.cost_)
    return k_range, costs


def elbow_with_top100_diag_med():
    with_diag_medic_selected_column_merged_df_top100 = load_data_with_top100_diag_med()

    k_range = range(2, 9)
    costs = []
    for k in k_range:
        km = KPrototypes(n_clusters=k, init="Huang", random_state=42)
        km.fit(
            with_diag_medic_selected_column_merged_df_top100,
            categorical=[0, 1, 2, 3, 4, 5] + list(range(16, 217)),
        )
        costs.append(km.cost_)
    return k_range, costs


# Get the data for each function
k_range1, costs1 = elbow_without_diag_med()
k_range2, costs2 = elbow_with_diag_med_as_set()
k_range3, costs3 = elbow_top20_diag_med()
k_range4, costs4 = elbow_with_top50_diag_med()
k_range5, costs5 = elbow_with_top100_diag_med()

fig, ax = plt.subplots(figsize=(14, 14))

# Plot both functions on the same axes
ax.plot(
    k_range1, costs1, marker="o", color="blue", label="Without medication & diagnosis"
)
ax.plot(
    k_range2,
    costs2,
    marker="o",
    color="orange",
    label="With all medications & diagnoses",
)
ax.plot(
    k_range3,
    costs3,
    marker="o",
    color="green",
    label="With 20 most frequent medications & diagnoses",
)
ax.plot(
    k_range4,
    costs4,
    marker="o",
    color="red",
    label="With 50 most frequent medications & diagnoses",
)
ax.plot(
    k_range5,
    costs5,
    marker="o",
    color="purple",
    label="With 100 most frequent medications & diagnoses",
)

ax.set_xlabel("Number of Clusters", fontsize=12)
ax.set_ylabel("Cost", fontsize=12)
ax.set_title("Elbow Plot for K-Prototype", fontsize=14)
ax.legend(loc="upper center")
plt.savefig("Elbow.jpg", bbox_inches="tight", dpi=300)
plt.show()
