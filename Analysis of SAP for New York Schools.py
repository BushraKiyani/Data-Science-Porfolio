#!/usr/bin/env python
# coding: utf-8

# # Scenario
# 
# We’ll look at the SAT scores of high schoolers, along with various demographic and other information about them. The SAT, or Scholastic Aptitude Test, is a test that high schoolers take in the US before applying to college. Colleges take the test scores into account when making admissions decisions, so it’s fairly important to do well on. The test is divided into 3 sections, each of which is scored out of 800 points. The total score is out of 2400 (although this has changed back and forth a few times, the scores in this dataset are out of 2400). High schools are often ranked by their average SAT scores, and high SAT scores are considered a sign of how good a school district is.
# 
# There have been allegations about the SAT being unfair to certain racial groups in the US, so doing this analysis on New York City data will help shed some light on the fairness of the SAT.
# 
# We have a dataset of SAT scores, and a dataset that contains information on each high school here. These will form the base of our project, but we’ll need to add more information to create compelling analysis.

# In[86]:


import pandas
import numpy as np
files = ["ap_2010.csv", "class_size.csv", "demographics.csv", "graduation.csv", "hs_directory.csv", "math_test_results.csv", "sat_results.csv"]
data = {}
for f in files:
    d = pandas.read_csv("D:/python/schools/{0}".format(f))
    data[f.replace(".csv", "")] = d


# In[87]:


# Print first 5 lines of each dataset
for k,v in data.items():
        print("\n" + k + "\n")
        print(v.head())


# We can start to see some useful patterns in the datasets:
# 
# 1. Most of the datasets contain a DBN column
# 2. Some fields look interesting for mapping, particularly Location 1, which contains coordinates inside a larger string.
# 3. Some of the datasets appear to contain multiple rows for each school (repeated DBN values), which means we’ll have to do some preprocessing.
# 
# # Unifying the data
# 
# In order to work with the data more easily, we’ll need to unify all the individual datasets into a single one. This will enable us to quickly compare columns across datasets. In order to do this, we’ll first need to find a common column to unify them on. Looking at the output above, it appears that DBN might be that common column, as it appears in multiple datasets.
# 
# If we google DBN New York City Schools, it explains that the DBN is a unique code for each school. When exploring datasets, particularly government ones, it’s often necessary to do some detective work to figure out what each column means, or even what each dataset is.
# 
# The problem now is that two of the datasets, class_size, and hs_directory, don’t have a DBN field. In the hs_directory data, it’s just named dbn, so we can just rename the column, or copy it over into a new column called DBN. In the class_size data, we’ll need to try a different approach.
# 

# In[23]:


data["demographics"]["DBN"].head()


# In[24]:


data["class_size"].head()


# As you can see above, it looks like the DBN is actually a combination of CSD, BOROUGH, and SCHOOL CODE. For those unfamiliar with New York City, it is composed of 5 boroughs. Each borough is an organizational unit, and is about the same size as a fairly large US City. DBN stands for District Borough Number. It looks like CSD is the District, BOROUGH is the borough, and when combined with the SCHOOL CODE, forms the DBN. There’s no systematized way to find insights like this in data, and it requires some exploration and playing around to figure out.
# 
# Now that we know how to construct the DBN, we can add it into the class_size and hs_directory datasets:

# In[88]:


data["class_size"]["DBN"] = data["class_size"].apply(lambda x: "{0:02d}{1}".format(x["CSD"], x["SCHOOL CODE"]), axis=1)
data["hs_directory"]["DBN"] = data["hs_directory"]["dbn"]


# In[170]:


data["class_size"]["DBN"].head()


# In[29]:


data["hs_directory"]["DBN"].head()


# # Adding in the surveys
# One of the most potentially interesting datasets to look at is the dataset on student, parent, and teacher surveys about the quality of schools. These surveys include information about the perceived safety of each school, academic standards, and more. Before we combine our datasets, let’s add in the survey data. In real-world data science projects, you’ll often come across interesting data when you’re midway through your analysis, and will want to incorporate it. Working with a flexible tool like Jupyter notebook will allow you to quickly add some additional code, and re-run your analysis.
# 
# In this case, we’ll add the survey data into our data dictionary, and then combine all the datasets afterwards. The survey data consists of 2 files, one for all schools, and one for school district 75. We’ll need to write some code to combine them. In the below code, we’ll:
# 
# 1. Read in the surveys for all schools using the windows-1252 file encoding.
# 2. Read in the surveys for district 75 schools using the windows-1252 file encoding.
# 3. Add a flag that indicates which school district each dataset is for.
# 4. Combine the datasets into one using the concat method on DataFrames.

# In[89]:


survey1 = pandas.read_csv('D:/python/schools/survey/survey_all.txt', delimiter="\t", encoding='windows-1252')
survey2 = pandas.read_csv('D:/python/schools/survey/survey_d75.txt', delimiter="\t", encoding='windows-1252')
survey1["d75"] = False
survey2["d75"] = True
survey = pandas.concat([survey1, survey2], axis=0)


# In[73]:


survey.head()


# In[90]:


survey['DBN'] = survey['dbn']
survey_fields = ['DBN', 'rr_s', 'rr_t', 'rr_p', 'N_s', 'N_t', 'N_p', 'saf_p_11', 'com_p_11', 'eng_p_11', 'aca_p_11', 'saf_t_11', 'com_t_11',  'aca_t_11', 'saf_s_11', 'com_s_11', 'eng_s_11', 'aca_s_11', 'saf_tot_11', 'com_tot_11', 'eng_tot_11', 'aca_tot_11']
survey = survey.loc[:, survey_fields]
data["survey"] = survey
survey.shape


# # Condensing datasets
# 
# If we take a look at some of the datasets, including class_size, we’ll immediately see a problem:

# In[141]:


data['class_size'].head()


# In[112]:


data['sat_results'].head()


# In order to combine these datasets, we’ll need to find a way to condense datasets like class_size to the point where there’s only a single row per high school. If not, there won’t be a way to compare SAT scores to class size. We can accomplish this by first understanding the data better, then by doing some aggregation. With the class_size dataset, it looks like GRADE and PROGRAM TYPE have multiple values for each school. By restricting each field to a single value, we can filter most of the duplicate rows. In the below code, we:
# 
# 1. Only select values from class_size where the GRADE field is 09-12.
# 2. Only select values from class_size where the PROGRAM TYPE field is GEN ED.
# 3. Group the class_size dataset by DBN, and take the average of each column. Essentially, we’ll find the average class_size values for each school.
# 4. Reset the index, so DBN is added back in as a column.

# In[91]:


class_size = data["class_size"]
class_size = class_size[class_size["GRADE "] == "09-12"]
class_size = class_size[class_size["PROGRAM TYPE"] == "GEN ED"]
class_size = class_size.groupby("DBN").agg(np.mean)
class_size.reset_index(inplace=True)
data["class_size"] = class_size
data["class_size"].head()


# # Condensing other datasets
# Next, we’ll need to condense the demographics dataset. The data was collected for multiple years for the same schools, so there are duplicate rows for each school. We’ll only pick rows where the schoolyear field is the most recent available:

# In[92]:


demographics = data["demographics"]
demographics = demographics[demographics["schoolyear"] == 20112012]
data["demographics"] = demographics


# In[173]:


data["demographics"].head()


# We’ll need to condense the math_test_results dataset. This dataset is segmented by Grade and by Year. We can select only a single grade from a single year:

# In[93]:


data["math_test_results"] = data["math_test_results"][data["math_test_results"]["Year"] == 2011]
data["math_test_results"] = data["math_test_results"][data["math_test_results"]["Grade"] == '8']
data["math_test_results"].head()


# Finally, graduation needs to be condensed:

# In[94]:


data["graduation"] = data["graduation"][data["graduation"]["Cohort"] == "2006"]
data["graduation"] = data["graduation"][data["graduation"]["Demographic"] == "Total Cohort"]
data["graduation"].head()


# Data cleaning and exploration is critical before working on the meat of the project. Having a good, consistent dataset will help you do your analysis more quickly.

# # Computing variables
# Computing variables can help speed up our analysis by enabling us to make comparisons more quickly, and enable us to make comparisons that we otherwise wouldn’t be able to do. The first thing we can do is compute a total SAT score from the individual columns SAT Math Avg. Score, SAT Critical Reading Avg. Score, and SAT Writing Avg. Score. In the below code, we:
# 
# 1. Convert each of the SAT score columns from a string to a number.
# 2. Add together all of the columns to get the sat_score column, which is the total SAT score.

# In[196]:


data["sat_results"].head()


# In[39]:


data["sat_results"]


# In[95]:


cols = ['SAT Math Avg. Score', 'SAT Critical Reading Avg. Score', 'SAT Writing Avg. Score']
data['sat_results'] = data['sat_results'].loc[data['sat_results']['SAT Math Avg. Score'] != 's']
data['sat_results'].head()


# In[96]:


cols = ['SAT Math Avg. Score', 'SAT Critical Reading Avg. Score', 'SAT Writing Avg. Score']
for c in cols:
    data['sat_results'] = data['sat_results'].loc[data['sat_results'][c] != 's'] # selected data without string 's'
    data["sat_results"][c] = data["sat_results"][c].astype(int)
data['sat_results']['sat_score'] = data['sat_results'][cols[0]] + data['sat_results'][cols[1]] + data['sat_results'][cols[2]]
data['sat_results'].head()


# Next, we’ll need to parse out the coordinate locations of each school, so we can make maps. This will enable us to plot the location of each school. In the below code, we:
# 
# 1. Parse latitude and longitude columns from the Location 1 column.
# 2. Convert lat and lon to be numeric.

# In[97]:


data["hs_directory"]['lat'] = data["hs_directory"]['Location 1'].apply(lambda x: x.split("\n")[-1].replace("(", "").replace(")", "").split(", ")[0])
data["hs_directory"]['lon'] = data["hs_directory"]['Location 1'].apply(lambda x: x.split("\n")[-1].replace("(", "").replace(")", "").split(", ")[1])
for c in ['lat', 'lon']:
    data["hs_directory"][c] = data["hs_directory"][c].astype(float)


# Now, we can print out each dataset to see what we have:

# In[98]:


for k,v in data.items():
    print(k)
    print(v.head())


# # Combining the datasets
# Now that we’ve done all the preliminaries, we can combine the datasets together using the DBN column. At the end, we’ll have a dataset with hundreds of columns, from each of the original datasets. When we join them, it’s important to note that some of the datasets are missing high schools that exist in the sat_results dataset. To resolve this, we’ll need to merge the datasets that have missing rows using the outer join strategy, so we don’t lose data. In real-world data analysis, it’s common to have data be missing. Being able to demonstrate the ability to reason about and handle missing data is an important part of building a portfolio.
# 
# You can read about different types of joins here.
# 
# In the below code, we’ll:
# 
# 1. Loop through each of the items in the data dictionary.
# 2. Print the number of non-unique DBNs in the item.
# 3. Decide on a join strategy — inner or outer.
# 4. Join the item to the DataFrame full using the column DBN.

# In[121]:


lat_data_names = [k for k,v in data.items()]
flat_data = [data[k] for k in flat_data_names]
full = flat_data[0]
for i, f in enumerate(flat_data[1:]):
    name = flat_data_names[i+1]
    print(name)
    print(len(f["DBN"])- len(f["DBN"].unique()))
    join_type = "inner"
    if name in ["sat_results", "ap_2010", "graduation"]:
        join_type = "outer"
    if name not in ["math_test_results"]:
        full = full.merge(f, on="DBN", how=join_type)
full.shape


# # Adding in values
# Now that we have our full DataFrame, we have almost all the information we’ll need to do our analysis. There are a few missing pieces, though. We may want to correlate the Advanced Placement exam results with SAT scores, but we’ll need to first convert those columns to numbers, then fill in any missing values:

# In[124]:


cols = ['AP Test Takers ', 'Total Exams Taken', 'Number of Exams with scores 3 4 or 5']
full[cols] = full[cols].fillna(value=0)
for col in cols:
    full[col] = data[f.replace(".csv", "")] = d
    full[col] = pandas.to_numeric(full[col])
full = full.fillna(full.mean())


# In[ ]:




