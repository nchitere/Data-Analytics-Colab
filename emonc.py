

# Load Python **packages**
"""

# @title
# Import Python packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy
from tabulate import tabulate
from scipy.stats import ttest_rel

"""# Set up
## set options for df display
## set connection to google drive and google sheets
"""

# @title
# set options for data dispaly
pd.set_option('display.max_rows',None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# @title
# Connect to G-Drive
from google.colab import drive
drive.mount('/content/gdrive/')

# @title
# Connect to G-Sheets
from google.colab import auth
auth.authenticate_user()

import gspread
from google.auth import default
creds, _ = default()

gc = gspread.authorize(creds)

"""# Read and process EmONC Knowledge Data"""

# @title
# Provide url of the G-Sheet where data is
# googlesheet ID truncated for data protection purposes
sheet_url = 'https://docs.google.com/spreadsheets/d/.....'

# @title
# Read in moh curriculum baseline data from google drive
spreadsheet = gc.open_by_url(sheet_url)

# List all worksheets
spreadsheet.worksheets()

# @title
# Access EmONC Knowledge worksheet and convert it to a data frame
EmONC_Knowledge = spreadsheet.worksheet('Knowledge')
EmONC_Knowledge = pd.DataFrame(EmONC_Knowledge.get_all_records())
EmONC_Knowledge.sample(3)

"""Specific County Selector

"""

EmONC_Knowledge.columns

# @title
# Select columns of interest
EmONC_Knowledge_df=EmONC_Knowledge[['county','Facility','Survey',\
                     'signs_obstructed_labor', 'risks_factor_obs_labor', 'medications_hip',\
                     'pre_eclampsia_risk_factors', 'shoulder_dystocia_management', \
                    'shoulder_dystocia_maneuvers', 'definitive_cord_prolapse_mx', \
                    'cord_prolapse_dx', 'inhibitors_of_rmc', 'categories_of_disrespect', \
                    'second_stage_labor', 'newborn_care', 'secondary_pph', 'maternal_cpr', \
                    'antepartum_hemorrhage', 'complication_hypovolemic_shock', 'ipc_handling_sharps',\
                    'ipc_waste_segregation', 'neonatal_resusc_reassessemnts', 'chest_compression_nnr',\
                    'labor_monitoring_2nd_stage', 'fetal_compromise', 'fetal_compromise_monitoring', \
                    'mpdsr','Score']]

EmONC_Knowledge_df = EmONC_Knowledge_df[EmONC_Knowledge_df['county']=='Muranga']
EmONC_Knowledge_df = EmONC_Knowledge_df[EmONC_Knowledge_df['Survey']=='Endline']
EmONC_Knowledge_df.sample(4)

# @title
# rename columns
column_mapper = {'county': 'County',
                 'medications_hip': 'hip_medications'}

EmONC_Knowledge_df.rename(columns=column_mapper, inplace=True)

"""# EmONC Knowledge Analysis"""

# @title
# Convert % Score to a float
EmONC_Knowledge_df['Score'] = EmONC_Knowledge_df['Score'].str.rstrip('%').astype(float)
# Check data types of columns
EmONC_Knowledge_df.dtypes

# @title
# Select only facilities that have closed data collection

EmONC_Knowledge_df.Facility.unique()

# @title
#summary of Score
EmONC_Knowledge_df['Score']\
.describe()\
.round(1)

# @title
#
#EmONC Knowledge Score by Facilit

# Calculate overall summary
overall_summary = EmONC_Knowledge_df['Score'].agg(['mean', 'std', 'count']).round(1).to_frame().T
overall_summary.columns = ['Mean Score','Std', 'Count']
overall_summary.index = ['Overall']
# Calculate mean, standard deviation, and count by county
mean_score_by_facility = EmONC_Knowledge_df[['Facility', 'Score']] \
                .groupby('Facility') \
                .agg({'Score': ['mean', 'std', 'count']}) \
                .round(1) \
                .sort_values(('Score', 'mean'), ascending=True)

# Rename columns for clarity
mean_score_by_facility.columns = ['Mean Score', 'Std', 'Count']

# Reset index to make 'county' a regular column
mean_score_by_facility.reset_index(inplace=True)

# Concatenate overall and county-wise summaries
mean_score_by_facility = pd.concat([mean_score_by_facility, overall_summary])
table = tabulate(mean_score_by_facility, headers='keys')

# # Split the table into lines
# table_lines = table.split('\n')

# # Add alternating colors to table lines
# for i in range(2, len(table_lines), 2):
#     table_lines[i] = '\033[47m' + table_lines[i] + '\033[0m'

# # Combine table lines back into a string
# table = '\n'.join(table_lines)

# Display the table
print(table)

mean_score_by_facility

# @title

# Calculate the mean score by county, round it to one decimal place, and sort by score in ascending order
mean_score_by_facility = mean_score_by_facility[mean_score_by_facility['Mean Score']!=87.6]

# # Create the bar chart with sorted data
plt.figure(figsize=(10, 6))
sns.barplot(x='Facility',
            y='Mean Score',
            data=mean_score_by_facility,
            palette='viridis')

# # Add labels to the bars
for index, value in enumerate(mean_score_by_facility['Mean Score']):
    plt.text(index, value + 0.5, str(value), ha='center', va='bottom', fontsize=10)

# Add horizontal line at the target value of 80
plt.axhline(y=80, color='red', linestyle='--', label='KPI Target (80) vs mean(87.6)')

plt.title('Mean Knowledge Score by Facility (Ascending Order)')
plt.xlabel('Facility')
plt.ylabel('Mean Knowledge Score')
plt.xticks(rotation=45, ha='right')
plt.ylim(0,100)

# Show the legend
plt.legend()

plt.tight_layout()

# Show the chart
plt.show()

# Concatenate overall and county-wise summaries
mean_score_by_facility = pd.concat([mean_score_by_facility])
table = tabulate(mean_score_by_facility, headers='keys')

# Split the table into lines
table_lines = table.split('\n')

# Add alternating colors to table lines
for i in range(2, len(table_lines), 2):
    table_lines[i] = '\033[47m' + table_lines[i] + '\033[0m'

# Combine table lines back into a string
table = '\n'.join(table_lines)

# Display the table
print(table)

# @title
# Overall distribution of scores

# Distribution of scores
plt.figure(figsize=(10, 6))
sns.histplot(
    EmONC_Knowledge_df['Score'],
    kde= True

)

plt.title('EmONC Knowledge Score Distribution')
plt.ylabel('Frequency')
plt.xlabel('Knowledge Score')
plt.xticks(rotation=45, ha='right')
plt.ylim(0,15)
plt.xlim(50,100)

# Show the legend
plt.legend()
plt.tight_layout()

# Show the chart
plt.show()

# @title
# Distribution of scores by Facility
plt.figure(figsize=(10, 6))
sns.boxplot(x='Facility',
            y='Score',
            data=EmONC_Knowledge_df,
            palette='viridis')

# Add horizontal line at the target value of 80
plt.axhline(y=80, color='red', linestyle='--', label='KPI Target (80)')

plt.title('EmONC Knowledge Score Distribution')
plt.xlabel('Facility')
plt.ylabel('Knowledge Score')
plt.xticks(rotation=45, ha='right')
plt.ylim(60,105)

# Show the legend
plt.legend()
plt.tight_layout()

# Show the chart
plt.show()

# # @title
# def classify_question(question):
#     if question in new_questions:
#         return 'new_topic'
#     else:
#         return 'old_topic'

# new_questions = ['signs_obstructed_labor', 'risks_factor_obs_labor', 'definitive_cord_prolapse_mx',
#                  'cord_prolapse_dx',  'maternal_cpr',
#                  'antepartum_hemorrhage',  'fetal_compromise', 'fetal_compromise_monitoring',
#                  'mpdsr']
# old_questions = ['hip_medications', 'inhibitors_of_rmc', 'categories_of_disrespect',
#                  'second_stage_labor', 'newborn_care', 'secondary_pph',
#                  'pre_eclampsia_risk_factors', 'shoulder_dystocia_management',
#                  'shoulder_dystocia_maneuvers', 'complication_hypovolemic_shock',
#                  'ipc_handling_sharps',
#                  'ipc_waste_segregation', 'neonatal_resusc_reassessemnts', 'chest_compression_nnr',
#                  'labor_monitoring_2nd_stage']

# @title
# Select data for Knowledge Item analysis
EmONC_Knowledge_Item_df = EmONC_Knowledge_df[['signs_obstructed_labor', 'risks_factor_obs_labor', 'hip_medications',\
                     'pre_eclampsia_risk_factors', 'shoulder_dystocia_management', \
                    'shoulder_dystocia_maneuvers', 'definitive_cord_prolapse_mx', \
                    'cord_prolapse_dx', 'inhibitors_of_rmc', 'categories_of_disrespect', \
                    'second_stage_labor', 'newborn_care', 'secondary_pph', 'maternal_cpr', \
                    'antepartum_hemorrhage', 'complication_hypovolemic_shock', 'ipc_handling_sharps',\
                    'ipc_waste_segregation', 'neonatal_resusc_reassessemnts', 'chest_compression_nnr',\
                    'labor_monitoring_2nd_stage', 'fetal_compromise', 'fetal_compromise_monitoring', \
                    'mpdsr']]



# Convert EmONC_Knowledge_Item_df to a data frame
df1 = pd.DataFrame(EmONC_Knowledge_Item_df)

# Function to calculate percentage correct and count of correct responses
def calculate_percentage_correct(column):
    total_responses = len(column)
    correct_responses = (column == 'Correct').sum()
    percentage_correct = (correct_responses / total_responses) * 100
    return percentage_correct, correct_responses

# Apply the function to each column
result = df1.apply(calculate_percentage_correct)

result = result.T
result.columns = ['Pass rate(%)', 'Count ']
result.index.name = 'Item'


# result['Category'] = result.index.map(classify_question)

result = result\
        .sort_values('Pass rate(%)', ascending=True)\
        .round(1)


# Create the bar chart with sorted data
plt.figure(figsize=(10, 6))
sns.barplot(x='Item',
            y='Pass rate(%)',
            data=result,
            palette='viridis')

# # Add labels to the bars
for index, value in enumerate(result['Pass rate(%)']):
     plt.text(index, value + 0.5, str(value), ha='center', va='bottom', fontsize=8)

plt.title('Pass rate by question')
plt.xlabel('Knowledge Item')
plt.ylabel('Pass rate(%)')
plt.xticks(rotation=45, ha='right')
plt.ylim(0,110)

plt.show()

# @title
# Read previous EmONC Knowledge data
# Access worksheet and convert it to a data frame
Pre_Knowledge = spreadsheet.worksheet('Knowledge Pre')
Pre_Knowledge_df = pd.DataFrame(Pre_Knowledge.get_all_records())
Pre_Knowledge_df = Pre_Knowledge_df[Pre_Knowledge_df['mentee_id'] != 721274871]
Pre_Knowledge_df = Pre_Knowledge_df[['Facility','Score']]
Current_EmONC_Knowledge_df = EmONC_Knowledge_df[['Facility','Score']]
# print(Pre_Knowledge_df.sample(3))
# print(Current_EmONC_Knowledge_df.sample(3))

# Add a 'previous' label to Pre_Knowledge_df
Pre_Knowledge_df_labeled = Pre_Knowledge_df.copy()
Pre_Knowledge_df_labeled['Label'] = 'Baseline'


# Add a 'current' label to Current_EmONC_Knowledge_df
Current_EmONC_Knowledge_df_labeled = Current_EmONC_Knowledge_df.copy()
Current_EmONC_Knowledge_df_labeled['Label'] = 'Endline'

# Concatenate the two dataframes
concatenated_df = pd.concat([Pre_Knowledge_df_labeled, Current_EmONC_Knowledge_df_labeled])

concatenated_df.sample(5)

# Plot previous versus current score distribution

sns.boxplot(y='Score',
            x= 'Label',
            data = concatenated_df,
            hue = 'Label'
            )
plt.title('Baseline vs Endline Knowledge Score Distribution')
plt.ylabel('Knowledge Score')
plt.xlabel('Baseline vs Endline')
plt.show()

Pre_Knowledge_df_labeled.describe()

Current_EmONC_Knowledge_df_labeled.describe()

# Perform paired T-test
t_statistic, p_value = ttest_rel(Pre_Knowledge_df_labeled['Score'], Current_EmONC_Knowledge_df_labeled['Score'])

# Output the results
print("Paired T-test Results:")
print("T-statistic:", t_statistic)
print("P-value:", p_value)

# Interpret the results
alpha = 0.05  # You can set your desired significance level here
if p_value < alpha:
    print("Reject the null hypothesis: There is a significant difference between previous and current knowledge scores.")
else:
    print("Fail to reject the null hypothesis: There is no significant difference between previous and current knowledge scores.")

# # @title
# Curriculum_Completion.dtypes

# # @title
# plt.figure(figsize=(10, 6))
# lm=sns.lmplot(x='cme_topic',
#            y='Knowledge_score',
#            data=Curriculum_Completion)
# plt.title('Curriculum Completion vs. EmONC Knowledge Score')

"""# Analysis on Neonatal Resuscitation Skills Score for a specific county"""

# @title
# Access worksheet and convert it to a data frame
NNR_Skills = spreadsheet.worksheet('NNR')
NNR_Skills = pd.DataFrame(NNR_Skills.get_all_records())
NNR_Skills = NNR_Skills[NNR_Skills['Survey']=='Endline']
NNR_Skills.sample(2)

NNR_Skills.columns

# @title
NNR_Skills_df = NNR_Skills[['Mentee', 'mentee_id', 'County', 'Facility', \
                            'Equipment_check', 'Dry_and_stimulate', 'ABC_assessment', 'Firm_seal', '40_60th_breaths', 'Chest_rise', \
                            'Reassessment', 'Ratio_Vent_Compression', 'Oxygen', 'Message_to_mother', 'Score']]


NNR_Skills_df.sample(3)

# @title
print(NNR_Skills.shape) # row count ,column count
print(NNR_Skills.isna().sum().sum()) # Check missingness

# @title

NNR_Skills_df = NNR_Skills_df[NNR_Skills_df['Score']>0]
NNR_Skills_df.Facility.unique()

# @title
NNR_Skills_df['Score']\
.describe()\
.round(1)

#NNR Skills Score by county
# Calculate nnr overall summary
nnr_overall_summary = NNR_Skills_df['Score'].agg(['mean', 'std', 'count']).round(1).to_frame().T
nnr_overall_summary.columns = ['Mean', 'Std', 'Count']
nnr_overall_summary.index = ['Overall']

# Calculate mean, standard deviation, and count by county
mean_nnr_score_by_facility = NNR_Skills_df[['Facility', 'Score']] \
                .groupby('Facility') \
                .agg({'Score': ['mean', 'std', 'count']}) \
                .round(1) \
                .sort_values(('Score', 'mean'), ascending=True)

# Rename columns for clarity
mean_nnr_score_by_facility.columns = ['Mean', 'Std', 'Count']

# Reset index to make 'county' a regular column
mean_nnr_score_by_facility.reset_index(inplace=True)
mean_nnr_score_by_county = pd.concat([mean_nnr_score_by_facility, nnr_overall_summary])
# print(mean_score_by_county)

table2 = tabulate(mean_nnr_score_by_county, headers='keys')



# Display the table
print(table2)

# @title
#
# Create the bar chart with sorted data
mean_nnr_score_by_facility = mean_nnr_score_by_facility[mean_nnr_score_by_facility['Count'] != 40]
plt.figure(figsize=(10, 6))
sns.barplot(x='Facility',
            y='Mean',
            data=mean_nnr_score_by_facility,
            palette='viridis')

# Add labels to the bars
for index, value in enumerate(mean_nnr_score_by_facility['Mean']):
    plt.text(index, value - 0.5, str(value), va='bottom', ha='center', fontsize=10)



# Add horizontal line at the target value of 80
plt.axhline(y=90, color='red', linestyle='--', label='KPI Target (90) vs. Mean(95.4)')

plt.title('Mean Score by Facility (Ascending Order)')
plt.xlabel('County')
plt.ylabel('Mean Score')
plt.xticks(rotation=45, ha='right')
plt.ylim(0,120)

# Show the legend
plt.legend()
plt.ylabel("Neonatal Resuscitation Score")
plt.xlabel('Facility')

plt.tight_layout()

# Show the chart
plt.show()

# @title
# Distribution of scores
plt.figure(figsize=(10, 6))
sns.histplot(
    NNR_Skills_df['Score'],
    kde= True

)

plt.title('NNR SKill Score Distribution')

plt.ylabel('Frequency')
plt.xlabel('NNR Skill Score')
plt.xticks(rotation=45, ha='right')
plt.ylim(0,30)
plt.xlim(50,100)
# Show the legend
plt.legend()

plt.tight_layout()

# Show the chart
plt.show()

# @title
# Distribution of scores
plt.figure(figsize=(10, 6))
sns.boxplot(x='Facility',
            y='Score',
            data=NNR_Skills_df,
            palette='viridis')



# Add horizontal line at the target value of 80
plt.axhline(y=90, color='red', linestyle='--', label='KPI Target (90)')

plt.title('NNR SKill Score Distribution by Facility')
plt.xlabel('Facility')
plt.ylabel('NNR Skill Score')
plt.xticks(rotation=45, ha='right', size=8)
plt.ylim(70,100)

# Show the legend
plt.legend()

plt.tight_layout()

# Show the chart
plt.show()

# @title
# Select columns for NNR Skills Item analysis
NNR_Item_df = NNR_Skills_df[[ 'Equipment_check', 'Dry_and_stimulate', 'ABC_assessment', 'Firm_seal', '40_60th_breaths', \
                             'Chest_rise', 'Reassessment', 'Ratio_Vent_Compression', 'Oxygen', 'Message_to_mother']]

type(NNR_Item_df)

# Calculate pass rate and sort values in ascending order
result3 = pd.DataFrame(
    NNR_Item_df
    .apply(lambda x: x.eq('Yes').mean() * 100).round(1)  # Calculate pass rate
    .reset_index()
    .rename(columns={'index': 'Item', 0: 'Pass rate(%)'})
    .sort_values('Pass rate(%)', ascending=True)  # Sort values by 'Pass Rate (%)' in ascending order
)



# Create the bar chart with sorted data
plt.figure(figsize=(10, 6))
sns.barplot(x='Item',
            y='Pass rate(%)',
            data=result3,
            palette='viridis')

# # Add labels to the bars
for index, value in enumerate(result3['Pass rate(%)']):
     plt.text(index, value + 0.5, str(value), ha='center', va='bottom', fontsize=10)

plt.title('NNR Skill Pass Rate by Question')
plt.xlabel('NNR Skill Item')
plt.ylabel('Pass rate(%)')
plt.xticks(rotation=45, ha='right')
plt.ylim(0,110)

# @title
# Read previous EmONC Knowledge data
# Access worksheet and convert it to a data frame
Pre_NNR = spreadsheet.worksheet('NNR Pre')
Pre_NNR_df = pd.DataFrame(Pre_NNR.get_all_records())
Pre_NNR_df = Pre_NNR_df[['Facility','Score']]
Current_NNR_df = NNR_Skills_df[['Facility','Score']]
# print(Pre_Knowledge_df.sample(3))
# print(Current_EmONC_Knowledge_df.sample(3))

# Add a 'previous' label to Pre_Knowledge_df
Pre_NNR_df_labeled = Pre_NNR_df.copy()
Pre_NNR_df_labeled['Label'] = 'Baseline'

# Add a 'current' label to Current_EmONC_Knowledge_df
Current_NNR_df_labeled = Current_NNR_df.copy()
Current_NNR_df_labeled['Label'] = 'Endline'

# Concatenate the two dataframes
concatenated_df1 = pd.concat([Pre_NNR_df_labeled, Current_NNR_df_labeled])
concatenated_df1.sample(5)



# @title
# Plot previous versus current score distribution

sns.boxplot(y='Score',
            x= 'Label',
            data = concatenated_df1,
            hue = 'Label'
            )
plt.title('Baseline vs Endline NNR Score Distribution')
plt.ylabel('NNR Skill Score')
plt.xlabel('Baseline vs Endline')
plt.show()

Pre_NNR_df_labeled.describe()

"""# Provider Confidence Analysis by County"""

# @title
# Access worksheet and convert it to a data frame
Provider_Confidence = spreadsheet.worksheet('Provider Confidence')
Provider_Confidence_df = pd.DataFrame(Provider_Confidence.get_all_records())
Provider_Confidence_df = Provider_Confidence_df[Provider_Confidence_df['Survey']=='Endline']
Provider_Confidence_df.sample(3)

# @title
Provider_Confidence_df.columns

# @title
Provider_Confidence_df = Provider_Confidence_df[['County', 'Facility','Postpartum_hemorrhage',\
                                                 'Hypertension_in_pregnancy', 'Shoulder_dystocia',\
                                                 'Birth_Asphyxia','Antepartum_hemorrhage', 'Score']]

Provider_Confidence_df.sample(3)

Provider_Confidence_df.columns

Provider_Confidence_df.dtypes

Provider_Confidence_df['Postpartum_hemorrhage']=Provider_Confidence_df['Postpartum_hemorrhage'].astype('int')
Provider_Confidence_df['Hypertension_in_pregnancy']=Provider_Confidence_df['Hypertension_in_pregnancy'].astype('float')
Provider_Confidence_df['Shoulder_dystocia']=Provider_Confidence_df['Shoulder_dystocia'].astype('int')
Provider_Confidence_df['Birth_Asphyxia']=Provider_Confidence_df['Birth_Asphyxia'].astype('int')
Provider_Confidence_df['Antepartum_hemorrhage']=Provider_Confidence_df['Antepartum_hemorrhage'].astype('int')

# @title
# Convert the score into a float
Provider_Confidence_df['Score'] = Provider_Confidence_df['Score'].str.rstrip('%').astype('float')
Provider_Confidence_df.columns

Provider_Confidence_df.Score.describe().round(1)

# @title
# Calculate the mean score by county, round it to one decimal place, and sort by score in ascending order
mean_provider_confidence_Score_by_county = Provider_Confidence_df[['Facility', 'Score']] \
                            .groupby('Facility') \
                            .mean() \
                            .round(1) \
                            .sort_values(by='Score', ascending=True)

# Create the bar chart with sorted data
plt.figure(figsize=(10, 6))
sns.barplot(x=mean_provider_confidence_Score_by_county.index,
            y='Score',
            data=mean_provider_confidence_Score_by_county,
            palette='viridis')

# Add labels to the bars
for index, value in enumerate(mean_provider_confidence_Score_by_county['Score']):
    plt.text(index, value + 0.5, str(value), ha='center', va='bottom', fontsize=8)

# Add horizontal line at the target value of 80
plt.axhline(y=80, color='red', linestyle='--', label='KPI Target (80)')

plt.title('Mean Confidence Score by Facility (Ascending Order)')
plt.xlabel('Facility')
plt.ylabel('Mean Provider Confidence Score')
plt.xticks(rotation=45, ha='right', size=10)
plt.ylim(0,110)

# Show the legend
plt.legend()

plt.tight_layout()

# Show the chart
plt.show()

# Calculate mean, standard deviation, and count by county
mean_provider_score_by_facility = Provider_Confidence_df[['Facility', 'Score']] \
                .groupby('Facility') \
                .agg({'Score': ['mean', 'std', 'count']}) \
                .round(1) \
                .sort_values(('Score', 'mean'), ascending=True)

# Rename columns for clarity
mean_provider_score_by_facility.columns = ['Mean', 'Std', 'Count']

# Reset index to make 'county' a regular column
mean_provider_score_by_facility.reset_index(inplace=True)
# print(mean_score_by_county)

table3 = tabulate(mean_provider_score_by_facility, headers='keys')
print(table3)

# @title
# Distribution of provider confidence scores
plt.figure(figsize=(10, 6))
sns.histplot(
    Provider_Confidence_df['Score'],
    kde= True

)

plt.title('Provider Confidence Score Distribution')

plt.ylabel('Frequency')
plt.xlabel('Provider Confidence Score')
plt.xticks(rotation=45, ha='right')
plt.ylim(0,12)
plt.xlim(50,100)

# Show the legend
plt.legend()

plt.tight_layout()

# Show the chart
plt.show()

# @title
# Distribution of provider confidence scores by county
plt.figure(figsize=(10, 6))
sns.boxplot(x='Facility',
            y='Score',
            data=Provider_Confidence_df,
            palette='viridis')

# Add horizontal line at the target value of 80
plt.axhline(y=80, color='red', linestyle='--', label='KPI Target (80)')

plt.title('Provider ConfidenceScore Distribution by Facility')
plt.xlabel('Facility')
plt.ylabel('Provider Confidence Score')
plt.xticks(rotation=45, ha='right')
plt.ylim(50,100)

# Show the legend
plt.legend()

plt.tight_layout()

# Show the chart
plt.show();

# @title
# %%capture
# Select columns for NNR Skills Item analysis
Provider_Confidence_Item_df = Provider_Confidence_df[[ 'Postpartum_hemorrhage','Hypertension_in_pregnancy', \
                             'Shoulder_dystocia','Birth_Asphyxia','Antepartum_hemorrhage']]

# Calculate pass rate and sort values in ascending order
result_pc = pd.DataFrame(
    Provider_Confidence_Item_df
    .apply(lambda x: (x > 3).mean() * 100).round(1)  # Calculate pass rate(At least 4 in confidence rating)
    .reset_index()
    .rename(columns={'index': 'Item', 0: 'Pass rate(%)'})
    .sort_values('Pass rate(%)', ascending=True)  # Sort values by 'Pass Rate (%)' in ascending order
)


# Create the bar chart with sorted data
plt.figure(figsize=(10, 6))
sns.barplot(x='Item',
            y='Pass rate(%)',
            data=result_pc,
            palette='viridis')

# # Add labels to the bars
for index, value in enumerate(result_pc['Pass rate(%)']):
     plt.text(index, value + 0.5, str(value), ha='center', va='bottom', fontsize=10)

plt.title('Provider Confidence Rating >3')
plt.xlabel('Provider Confidence Item')
plt.ylabel('Pass rate(%)')
plt.xticks(rotation=45, ha='right')
plt.ylim(0,100)

plt.show()

# @title
# Read previous EmONC Knowledge data
# Access worksheet and convert it to a data frame
PC_Pre = spreadsheet.worksheet('PC Pre')
PC_Pre_df = pd.DataFrame(PC_Pre.get_all_records())
PC_Pre_df = PC_Pre_df[['Facility','Score']]
Current_PC_df = Provider_Confidence_df[['Facility','Score']]
# print(Pre_Knowledge_df.sample(3))
# print(Current_EmONC_Knowledge_df.sample(3))

# Add a 'previous' label to Pre_Knowledge_df
PC_Pre_df_labeled = PC_Pre_df.copy()
PC_Pre_df_labeled['Label'] = 'Baseline'

# Add a 'current' label to Current_EmONC_Knowledge_df
Current_PC_df_labeled = Current_PC_df.copy()
Current_PC_df_labeled['Label'] = 'Endline'

# Concatenate the two dataframes
concatenated_df3 = pd.concat([PC_Pre_df_labeled, Current_PC_df_labeled])
concatenated_df3.sample(5)

# @title
# Plot previous versus current score distribution

sns.boxplot(y='Score',
            x= 'Label',
            data = concatenated_df3,
            hue = 'Label'
            )
plt.title('Baseline vs Endline Provider Confidence Score Distribution')
plt.ylabel('Provider Confidence Score')
plt.xlabel('Baseline vs Endline')
plt.show()

# Perform paired T-test
t_statistic, p_value = ttest_rel(PC_Pre_df_labeled['Score'], Current_PC_df_labeled['Score'])

# Output the results
print("Paired T-test Results:")
print("T-statistic:", t_statistic)
print("P-value:", p_value)

# Interpret the results
alpha = 0.05  # You can set your desired significance level here
if p_value < alpha:
    print("Reject the null hypothesis: There is a significant difference between baseline and endline knowledge scores.")
else:
    print("Fail to reject the null hypothesis: There is no significant difference between baseline and endline knowledge scores.")

PC_Pre_df_labeled.describe()

# CME & DRILL Completion
cme_completion = spreadsheet.worksheet('CME Completion')
cme_completion = pd.DataFrame(cme_completion.get_all_records())
cme_completion.sample(3)

cme_completion.columns

# Summarize CME Completion
cme_completion = cme_completion[cme_completion['mentee match'] != 'Not a match']
proportion_complete = (cme_completion['Status'] == 'Complete').mean()
print(f"Proportion of complete: {proportion_complete}")

cme_completion.describe()

num_complete = (cme_completion['Status'] == 'Complete').sum()
total_entries = len(cme_completion)
proportion_complete = num_complete

print(f"Proportion of complete: {proportion_complete}")

drill_completion = spreadsheet.worksheet('Drill Completion')
drill_completion = pd.DataFrame(drill_completion.get_all_records())
drill_completion.sample(3)

# Summarize CME Completion
drill_completion = drill_completion[drill_completion['mentee match'] != 'Not a match']
proportion_complete = (drill_completion['Status'] == 'Complete').mean()
print(f"Proportion of complete: {proportion_complete}")

drill_completion.describe()

# Access combined scores worksheet and convert it to a data frame
combined_scores = spreadsheet.worksheet('Combined scores')
combined_scores = pd.DataFrame(combined_scores.get_all_records())
combined_scores.sample(3)

combined_scores.dtypes

combined_scores['Knowledge Score'] = combined_scores['Knowledge Score'].str.strip('%').astype('float')
combined_scores['Provider  Confidence Score'] = combined_scores['Provider  Confidence Score'].str.strip('%').astype('float')

combined_scores.rename(columns=column_mapper, inplace=True)
combined_scores.sample(5)

combined_scores.columns

corr_matrix = combined_scores[['Knowledge Score', 'NNR Score', 'Provider  Confidence Score']].corr()
corr_matrix

column_mapper = {'Provider  Confidence Score': 'Provider Confidence',
                 }

corr_matrix.rename(columns=column_mapper, inplace=True)

# Set up the matplotlib figure
plt.figure(figsize=(6, 4))

# Draw the heatmap
sns.heatmap(corr_matrix, annot=True, cmap= 'Blues', linewidths=.5, fmt=".2f")

# Adding titles and labels for clarity
plt.title('Correlation Mentee Cohort')
plt.show()
