'''
Script to plot the trajectory of patinet (relative and actual) by reading a csv file based on episode_start_date and episode_end_date along with other info
******************************
1. To use script make change to the FILE2_PATH and install requirments
******************************
'''

# Required libraries
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import display

import os
from dotenv import load_dotenv
load_dotenv()

# Method that load file
def load_data():
    original_df = pd.read_csv(os.getenv("FILE2_PATH"))
    original_df = original_df[['pasient','episode_start_date','episode_end_date','gender','age_group','Count_visit','actual_diag','label']]
    original_df['episode_start_date'] = pd.to_datetime(original_df['episode_start_date'])
    original_df['episode_end_date'] = pd.to_datetime(original_df['episode_end_date'], errors='coerce')
    original_df = original_df.sort_values(by=['pasient', 'episode_start_date'])
    original_df = original_df.dropna(subset=['episode_start_date'])
    
    cluster_dfs = {}
    for cluster_label in range(1, 7):  
        cluster_dfs[f'original_df{cluster_label}'] = original_df[original_df['label'] == cluster_label].copy()
    return cluster_dfs

# Plots the trajectory in years
def patient_timeline_plot_yearly(original_df,ax,cmap,unique_patients):
    for i, patient_id in enumerate(unique_patients):
        patient_data = original_df[original_df['pasient'] == patient_id]
        for _, case in patient_data.iterrows():
            case_start = case['episode_start_date']
            case_end = case['episode_end_date']
            case_gender = case['gender']
            case_age_group = case['age_group']
            case_Count_visit = case['Count_visit']
            case_actual_diag = case['actual_diag']
            label_demographics = f"{case_gender} : {case_age_group}"
            label_diagnosis = f"{case_Count_visit} :{case_actual_diag}"
            ax.plot([case_start, case_end], [i, i], linewidth=15,color=cmap(i)) #color=cmap(case_axis)
            ax.annotate(label_demographics, (case_start + pd.DateOffset(days=2), i), xytext=(-8, 11), textcoords='offset points', ha='left', fontsize=8,
                        bbox=dict(boxstyle='round,pad=0.1', edgecolor='none', facecolor='white'))
            ax.annotate(label_diagnosis, (case_start + pd.DateOffset(days=2), i), xytext=(-8, -16), textcoords='offset points', ha='left', fontsize=8,
                        bbox=dict(boxstyle='round,pad=0.1', edgecolor='none', facecolor='white'))
            
    ax.set_yticks(range(len(unique_patients)))
    ax.set_yticklabels(unique_patients)
    ax.grid(True, linewidth=0.1) 
    ax.set_xlabel('Actual Date')
    ax.set_ylabel('Patient ID')
    ax.xaxis_date()

# Plots the time relatively
def patient_timeline_plot_relative(original_df,ax,cmap,unique_patients):
    starting_dates = {}
    for i, patient_id in enumerate(unique_patients):
        patient_data = original_df[original_df['pasient'] == patient_id]
        starting_dates[patient_id] = patient_data.iloc[0]['episode_start_date']
        for _, case in patient_data.iterrows():
            case_start = case['episode_start_date']
            case_end = case['episode_end_date']
            case_gender = case['gender']
            case_age_group = case['age_group']
            case_Count_visit = case['Count_visit']
            case_actual_diag = case['actual_diag']
            label_demographics = f"{case_gender} : {case_age_group}"
            label_diagnosis = f"{case_Count_visit} :{case_actual_diag}"
            relative_start = (case_start - starting_dates[patient_id]).days
            relative_end = (case_end - starting_dates[patient_id]).days
            ax.plot([relative_start, relative_end], [i, i], linewidth=15,color=cmap(i))
            ax.annotate(label_demographics, (relative_start + 2, i), xytext=(-8, 11), textcoords='offset points', ha='left', fontsize=8,
                        bbox=dict(boxstyle='round,pad=0.3', edgecolor='none', facecolor='white'))
            
            ax.annotate(label_diagnosis, (relative_start + 2, i), xytext=(-8, -16), textcoords='offset points', ha='left', fontsize=8,
                        bbox=dict(boxstyle='round,pad=0.3', edgecolor='none', facecolor='white'))

    ax.set_yticks(range(len(unique_patients)))
    ax.set_yticklabels(unique_patients)
    ax.grid(True, linewidth=0.1) 
    ax.set_xlabel('Days since first case')
    ax.set_ylabel('Patient ID')
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    
# Run the above code only
if __name__ == "__main__":
    original_df = load_data()
    original_df_1 = original_df['original_df1']
    original_df_1 = original_df_1.head(20)
    
    original_df_2 = original_df['original_df2']
    original_df_2 = original_df_2.head(20)
    
    original_df_3 = original_df['original_df3']
    original_df_3 = original_df_3.head(20)
    
    original_df_4 = original_df['original_df4']
    original_df_4 = original_df_4.head(20)
    
    original_df_5 = original_df['original_df5']
    original_df_5 = original_df_5.head(20)
    
    original_df_6 = original_df['original_df6']
    original_df_6 = original_df_6.head(20)

    unique_patients = original_df_1['pasient'].unique()
    cmap = plt.get_cmap('tab20')
    fig, axes = plt.subplots(1, 2, figsize=(30, 14))
    patient_timeline_plot_yearly(original_df_1, axes[0], cmap, unique_patients)
    patient_timeline_plot_relative(original_df_1, axes[1], cmap, unique_patients)
    
    unique_patients = original_df_2['pasient'].unique()
    cmap = plt.get_cmap('tab20')
    fig, axes = plt.subplots(1, 2, figsize=(30, 14))
    patient_timeline_plot_yearly(original_df_2, axes[0], cmap, unique_patients)
    patient_timeline_plot_relative(original_df_2, axes[1], cmap, unique_patients)
    
    unique_patients = original_df_3['pasient'].unique()
    cmap = plt.get_cmap('tab20')
    fig, axes = plt.subplots(1, 2, figsize=(30, 14))
    patient_timeline_plot_yearly(original_df_3, axes[0], cmap, unique_patients)
    patient_timeline_plot_relative(original_df_3, axes[1], cmap, unique_patients)
    
    unique_patients = original_df_4['pasient'].unique()
    cmap = plt.get_cmap('tab20')
    fig, axes = plt.subplots(1, 2, figsize=(30, 14))
    patient_timeline_plot_yearly(original_df_4, axes[0], cmap, unique_patients)
    patient_timeline_plot_relative(original_df_4, axes[1], cmap, unique_patients)
    
    unique_patients = original_df_5['pasient'].unique()
    cmap = plt.get_cmap('tab20')
    fig, axes = plt.subplots(1, 2, figsize=(30, 14))
    patient_timeline_plot_yearly(original_df_5, axes[0], cmap, unique_patients)
    patient_timeline_plot_relative(original_df_5, axes[1], cmap, unique_patients)
    
        
    unique_patients = original_df_6['pasient'].unique()
    cmap = plt.get_cmap('tab20')
    fig, axes = plt.subplots(1, 2, figsize=(30, 14))
    patient_timeline_plot_yearly(original_df_6, axes[0], cmap, unique_patients)
    patient_timeline_plot_relative(original_df_6, axes[1], cmap, unique_patients)
    
    plt.tight_layout()
    plt.show()
    