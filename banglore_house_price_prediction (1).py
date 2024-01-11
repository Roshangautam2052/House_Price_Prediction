# -*- coding: utf-8 -*-
"""Banglore_House_Price_Prediction.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1EfPur2E78GhK8q7FblNbFsF9GGpJe7pY
"""

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# %matplotlib inline
import seaborn as sns
sns.set_style('darkgrid')
palette=sns.color_palette('rocket_r')
from scipy.stats import chi2_contingency
sns.set(rc={'figure.figsize':(11.7,8.27)})
##Display all of the columns of the dataframe
pd.pandas.set_option('display.max_columns', None)

# Data Analysis Phase to understand more about the data
'''Customize visualization
Seaborn and matplotlib visualization.'''

plt.style.use('bmh')
sns.set_style({'axes.grid':False})
'''Plotly visualization .'''
import plotly.offline as py
from plotly.offline import iplot, init_notebook_mode
import plotly.graph_objs as go
pd.pandas.set_option('display.max_columns', None)
'''Display markdown formatted output like bold, italic bold etc.'''
from IPython.display import Markdown
def bold(string):
    display(Markdown(string))

path="https://raw.githubusercontent.com/Roshangautam2052/Bengaluru_House_Price_Prediction-/main/Bengaluru_House_Data.csv"
dataset=pd.read_csv(path)

dataset.shape

dataset.sample(5)

dataset.info()

## Checking missing values
dataset.isnull().sum()

## Checking Duplicate values
dataset.duplicated().sum()

dataset.loc[dataset.duplicated(),:]

##Dropping Duplicate values
dataset= dataset.drop_duplicates(keep='first')

dataset.duplicated().sum()

#Since the missing values in 'size' and 'location' is very less as compared to the whole dataset so the null values of this column is dropped
dataset=dataset.dropna(subset=['location','size'])

dataset['size'].unique()

dataset['BHK']= dataset['size'].apply(lambda x: int(x.split(' ')[0]))

dataset.head()

dataset=dataset.drop(['size'],axis=1)

dataset['Area_type']= dataset['area_type'].apply(lambda x: str(x.split('-')[0]))

dataset=dataset.drop(['area_type'],axis=1)

dataset.head()

dataset["total_sqft"].unique()

def is_float(x):
    try:
        float(x)
    except:
        return False
    return True

dataset[~dataset['total_sqft'].apply(is_float)].head(10)

def conversion_sqft_num(x):
    list=x.split('-')
    if len(list)==2:
        return (float(list[0])+float(list[1]))//2
    try:
        return float(x)

    except:
        return None

ds= dataset.copy()
ds['total_sqft']=dataset['total_sqft'].apply(conversion_sqft_num)
ds.head(10)

"""# Exploratory Data Analysis

Exploratory Data Analysis for Categorical Variables
"""

#Creating a list of Categoircal Variables within the dataset
categorical_features=[feature for feature in ds.columns if ds[feature].dtypes=='O']
categorical_features

ds[categorical_features].head()

#Checking the cardinality of each of the categories
for feature in categorical_features:
    print('The feature is {} and number of categories are {}'.format(feature,len(dataset[feature].unique())))

ds[categorical_features].isnull().sum()

ds1=ds.copy()

## Since the cardinality of categorical variables 'availability', 'location' and 'society' is very high due to which there is difficulity in visualization for bivariate and univariate analysis
##  To overcome this problem the  society is filled with label 'Missing' for its missing values  and the categories with less than 1% of existence are labelled as'Rare_var'
## This eases the visualization

## creating a list with the categorical features having NaN value
features_nan=[feature for feature in ds1.columns if ds1[feature].isnull().sum()>1 and ds1[feature].dtypes=='O']

for feature in features_nan:
    print("{}: {}% missing values".format(feature,np.round(ds1[feature].isnull().mean(),4)))

## Replacing  missing value of society with a new label
def replace_cat_feature(ds1,features_nan):
    ds2=ds1.copy()
    ds2[features_nan]=ds2[features_nan].fillna('Missing')
    return ds2

ds1=replace_cat_feature(ds1,features_nan)

ds1[features_nan].isnull().sum()

## Creating a list with a categorical features in ds1
categorical_attributes=['availability','location','society']
for feature in categorical_attributes:
    temp=ds1.groupby(feature)['price'].count()/len(ds1)
    temp_df=temp[temp>0.01].index
    ds1[feature]=np.where(ds1[feature].isin(temp_df),ds1[feature],'Rare_var')
ds1.head()

ds1['society'].sample(100)

# Generating box plot
for i in categorical_attributes:
  ax=sns.countplot(x=ds1[i])
  ax.set_xticklabels(ax.get_xticklabels(),rotation=50)
  plt.show()

ax1=sns.countplot(x=ds1['Area_type'])
ax1.set_xticklabels(ax1.get_xticklabels(),rotation=50)
plt.show()

## Plotting stip plot and box plot in between categorical variable and price
sns.set_style('white')
for i in categorical_attributes:
  ct_plot=sns.catplot(x=i, y='price', kind='box',height=9, aspect=1.5, data=ds1, palette=palette)
  ct_plot.set_xticklabels(rotation=45)

sns.catplot(x='Area_type', y='price', kind='box',height=9, aspect=1.5, data=ds1)
plt.show()

## Plotting stip plot and box plot in between categorical variable and price
sns.set_style('white')
for i in categorical_attributes:
  swan=sns.catplot(x=i, y='price', kind='strip',height=9, aspect=1.5, data=ds1, palette=palette)
  swan.set_xticklabels(rotation=45)

swan1=sns.catplot(x='Area_type', y='price', kind='strip',height=9, aspect=1.5, data=ds1, palette=palette)
swan1.set_xticklabels(rotation=45)

## Plotting stip plot and box plot in between categorical variable and price
sns.set_style('white')
for i in categorical_attributes:
 vlp=sns.violinplot(x=i, y='price',data=ds1, palette=palette)
 vlp.set_xticklabels(vlp.get_xticklabels(),rotation=45)
 plt.show()

vlp=sns.violinplot(x=ds1['Area_type'], y='price',data=ds1, palette=palette)
vlp.set_xticklabels(vlp.get_xticklabels(),rotation=45)
plt.show()

## creating a categorical list with all features of the  origional data
categories=ds[['availability', 'location', 'society', 'Area_type']]
categories.head()

"""Implementing Cramer's V to find the correlation in between the categorical variables"""

## Building the Cramer's V function
def cramers_V(var1,var2) :
  crosstab =np.array(pd.crosstab(var1,var2, rownames=None, colnames=None)) # Cross table building
  stat = chi2_contingency(crosstab)[0] # Keeping of the test statistic of the Chi2 test
  obs = np.sum(crosstab) # Number of observations
  mini = min(crosstab.shape)-1 # Take the minimum value between the columns and the rows of the cross table
  return (stat/(obs*mini))

## Building the matrix
rows= []

for var1 in categories:
  col = []
  for var2 in categories :
    cramers =cramers_V(categories[var1], categories[var2]) # Cramer's V test
    col.append(round(cramers,2)) # Keeping of the rounded value of the Cramer's V
  rows.append(col)

cramers_results = np.array(rows)
df = pd.DataFrame(cramers_results, columns = categories.columns, index =categories.columns)

df

# generating 2-D 10x10 matrix of random numbers
# from 1 to 100
data = np.random.randint(low=1,
                         high=100,
                         size=(10, 10))

# setting the parameter values
annot = True

# plotting the heatmap
hm = sns.heatmap(data=df,
                annot=annot)

# displaying the plotted heatmap
plt.show()

"""Exploratory Data Analysis for Numerical features"""

## Checking Numerical Features
numerical_features=[feature for feature in ds.columns if ds[feature].dtypes!='O']
print('Number of numerical variables:', len(numerical_features))
##Visualizing the numerical features
ds[numerical_features].head()

"""Carrying out Multivariate  Analysis on all numerical variables

"""

ds.hist(bins=50, figsize=(20,15))

"""Finding out discrete Variables and Carrying out Univariate and Bivariate analysis on discrete data"""

#Finding the discrete variables
discrete_feature=[feature for feature in numerical_features if len(ds[feature].unique())<25]
print("Discrete variables Count:{}".format(len(discrete_feature)))

# Generating box plot
for feature in discrete_feature:
    data= ds.copy()
    sns.boxplot(x=data[feature])
    plt.xlabel(feature)
    plt.show()

#Finding out the distribution of discrete variables
for feature in discrete_feature:
    data= ds.copy()
    sns.displot(x=data[feature], kind='kde',height=8.27, aspect=9/8.27)
    plt.xlabel(feature)
    plt.show()

ds[discrete_feature].describe()

#Evaluation of Kurtosis and Skewness of discrete variables
for feature in discrete_feature:
    data=ds.copy()
    print( " Skewness of {} is {}".format(feature,data[feature].skew()))
    print( " Kurtosis  of {} is {}".format(feature,data[feature].kurt()))

"""Bivariate analysis of discrete variables"""

#finding  the relationship in between discrete attribute and price using boxplot
for feature in discrete_feature:
    data= ds.copy()
    sns.boxplot(x=data[feature],y=ds['price'])
    plt.xlabel(feature)
    plt.ylabel('price')
    plt.title(feature)
    plt.show()

#finding  the relationship in between discrete attribute and price using lineplot
for feature in discrete_feature:
    data= ds.copy()
    sns.lineplot(x=data[feature],y=ds['price'])
    plt.xlabel(feature)
    plt.ylabel('price')
    plt.title(feature)
    plt.show()

#finding  the relationship in between discrete attribute and price using boxplot
for feature in discrete_feature:
    data= ds.copy()
    sns.regplot(x=ds['price'],y=ds[feature])
    plt.xlabel(feature)
    plt.ylabel('price')
    plt.show()

#Finding out the continous variable in the numerical data
continious_feature=[feature for feature in numerical_features if feature not in discrete_feature]
print("Continious variables Count:{}".format(len(continious_feature)))

"""Univariate Analysis of continious variables"""

# Generating box plot
for feature in continious_feature:
    data= ds.copy()
    sns.boxplot(x=data[feature])
    plt.xlabel(feature)
    plt.show()

sns.distplot(data['price'], hist = True)

sns.distplot(data['total_sqft'], hist = True)

#Evaluation of Kurtosis and Skewness of continious_feature
for feature in continious_feature:
    data=ds.copy()
    print( " Skewness of {} is {}".format(feature,data[feature].skew()))
    print( " Kurtosis  of {} is {}".format(feature,data[feature].kurt()))

"""Carrying out Bivariate Analysis of continous variable"""

#finding  the relationship in between total_sqft and price
sns.scatterplot(x=ds['total_sqft'],y=ds['price'])
plt.xlabel('total_sqft')
plt.ylabel('price')
plt.show()

sns.regplot(x=ds['price'],y=ds['total_sqft'])

""" Carrying out Multivariate Analysis in numerical variables"""

sns.pairplot(ds)

sns.pairplot(ds, hue="price")

##Finding out correlation in between the numerical variables
sns.set(rc = {'figure.figsize':(16,8)})
sns.heatmap(ds.corr(), annot = True, fmt='.2g',cmap= 'coolwarm')

"""Feature_Engineering

Checking null values in the dataset
"""

## Here the percantage of NaN values present in each of the feature is being  checked
## The list of features which have missing values is being done
features_with_na=[features for features in ds.columns if ds[features].isnull().sum()>1]
# Printing the name of feature and percentage of the missing values

for feature in features_with_na:
    print(feature,np.round(ds[feature].isnull().mean()*100,3),"% missing values")
ds.isnull().sum()

plt.figure(figsize=(10,6))
sns.heatmap(ds.isna())
plt.show()

"""Analysing the type of missing value of Balcony based upon Numerical Attributes"""

#Handling Missing values of numerical features
##Checking the type of missing values in numerical features
##Diagnosing the type of missing values of balcony based upon numerical attributes
df=ds1.copy()
from scipy.stats import ttest_ind
def Diagnose_MV_Numerical(df,str_att_name,BM_MV):
    MV_labels = {True:'With Missing Values',False:'Without Missing Values'}

    labels=[]
    box_sr = pd.Series('',index = BM_MV.unique())
    for poss in BM_MV.unique():
        BM = BM_MV == poss
        box_sr[poss] = df[BM][str_att_name].dropna()
        labels.append(MV_labels[poss])

    plt.boxplot(box_sr,vert=False)
    plt.yticks([1,2],labels)
    plt.xlabel(str_att_name)
    plt.show()

    plt.figure(figsize=(10,4))

    att_range = (df[str_att_name].min(),df[str_att_name].max())

    for i,poss in enumerate(BM_MV.unique()):
        plt.subplot(1,2,i+1)
        BM = BM_MV == poss
        df[BM][str_att_name].hist()
        plt.xlim = att_range
        plt.xlabel(str_att_name)
        plt.title(MV_labels[poss])

    plt.show()

    group_1_data = df[BM_MV][str_att_name].dropna()
    group_2_data = df[~BM_MV][str_att_name].dropna()

    p_value = ttest_ind(group_1_data,group_2_data).pvalue

    print('p-value of t-test: {}'.format(p_value))

numerical_attributes1 = ['price','BHK','total_sqft','bath']


BM_MV = ds1.balcony.isna()
for att in numerical_attributes1:
    print('Diagnosis Analysis of Missing Values for {}:'.format(att))
    Diagnose_MV_Numerical(df,att,BM_MV)
    print('- - - - - - - - - - - - divider - - - - - - - - - - - ')

"""Analsying the type of missing value of Balcony based upon Categorical Attribute"""

from scipy.stats import chi2_contingency
def Diagnose_MV_Categorical(df,str_att_name,BM_MV):
    MV_labels = {True:'With Missing Values',False:'Without Missing Values'}

    plt.figure(figsize=(10,4))
    for i,poss in enumerate(BM_MV.unique()):
        plt.subplot(1,2,i+1)
        BM = BM_MV == poss
        df[BM][str_att_name].value_counts().plot.bar()
        plt.title(MV_labels[poss])
    plt.show()

    contigency_table = pd.crosstab(BM_MV,df[str_att_name])
    p_value = chi2_contingency(contigency_table)[1]

    print('p-value of Chi_squared test: {}'.format(p_value))

categorical_attributes1 = ['availability','location','Area_type']

BM_MV = df.balcony.isna()
for att in categorical_attributes1:
    print('Diagnosis Analysis of Missing Values for {}:'.format(att))
    Diagnose_MV_Categorical(df,att,BM_MV)
    print('- - - - - - - - - - - - divider - - - - - - - - - - - ')

"""Analysing the missing value of total_sqft based upon numerical attributes"""

numerical_attributes2 = ['price','BHK','balcony','bath']
BM_MV = df.total_sqft.isna()
for att in numerical_attributes2:
    print('Diagnosis Analysis of Missing Values for {}:'.format(att))
    Diagnose_MV_Numerical(df,att,BM_MV)
    print('- - - - - - - - - - - - divider - - - - - - - - - - - ')

"""Analysing the missing value of total_sqft based upon categorical attributes"""

BM_MV = df.total_sqft.isna()
for att in categorical_attributes1:
    print('Diagnosis Analysis of Missing Values for {}:'.format(att))
    Diagnose_MV_Categorical(df,att,BM_MV)
    print('- - - - - - - - - - - - divider - - - - - - - - - - - ')

"""Analysing the missing value of bath based upon numerical values"""

numerical_attributes3 = ['price','BHK','total_sqft','balcony']
BM_MV = df.bath.isna()
for att in numerical_attributes3:
    print('Diagnosis Analysis of Missing Values for {}:'.format(att))
    Diagnose_MV_Numerical(df,att,BM_MV)
    print('- - - - - - - - - - - - divider - - - - - - - - - - - ')

"""Analysing the missing value of bath based upon categorical attributes"""

BM_MV = df.balcony.isna()
for att in categorical_attributes1:
    print('Diagnosis Analysis of Missing Values for {}:'.format(att))
    Diagnose_MV_Categorical(df,att,BM_MV)
    print('- - - - - - - - - - - - divider - - - - - - - - - - - ')



"""Capturing the NaN features with NaN values for numerical features and replacing NaN values with median

"""

numerical_with_nan=[feature for feature in ds.columns if ds[feature].isnull().sum()>1 and ds[feature].dtypes!='O']
## Replacing the numerical Missing Values

for feature in numerical_with_nan:
    ##  Replacing  by central tendency value(median) for total_sqft which is MCAR and bath and balcony which are MAR, as there are too many outliers
    median_value=ds[feature].median()

    ## create a new feature to capture nan values
    ds[feature+'nan']=np.where(dataset[feature].isnull(),1,0)
    ds[feature].fillna(median_value,inplace=True)

ds[numerical_with_nan].isnull().sum()

## The society column is dropped as the missing values is more than 25% also from Cramer's V test the society column and location are highly correlated so dropping either one column is necessary for
## avoiding multicollinearity
ds=ds.drop('society', axis=1)

ds.head()

plt.figure(figsize=(4,7))
sns.heatmap(ds.isna())
plt.show()

"""Finding the outliers in the numerical data"""

def box_plot(data1):
  numerical_atts = ['total_sqft','bath','balcony','price','BHK']
  plt.figure(figsize=(12,3))
  for i,att in enumerate(numerical_atts):
    plt.subplot(1,len(numerical_atts),i+1)
    sns.boxplot(y=data1[att])
  plt.tight_layout()
  plt.show()

box_plot(ds)

"""Dealing with Multivariate Outliers in BHK,price and bathroom using Domain Knowledge"""

## Creating new column price_per_sqft
ds['price_per_sqft']=ds['price']*100000/ds['total_sqft']
ds.head()

ds[ds.total_sqft/ds.BHK<300].head()
ds.shape

ds= ds[~(ds.total_sqft/ds.BHK<300)]
ds.shape

ds.price_per_sqft.describe()

def remove_pps_outliers(ds):
    df_out=pd.DataFrame()
    for key, subdf in ds.groupby('location'):
        m=np.mean(subdf.price_per_sqft)
        st=np.std(subdf.price_per_sqft)
        reduced_df=subdf[(subdf.price_per_sqft>(m-st))& (subdf.price_per_sqft<=(m+st))]
        df_out=pd.concat([df_out, reduced_df],ignore_index=True)
    return df_out
ds=remove_pps_outliers(ds)
ds.shape

ds.head()

# Commented out IPython magic to ensure Python compatibility.
from matplotlib import pyplot as plt
# %matplotlib inline
import matplotlib
def plot_scatter_chart(ds,location):
    BHK2 = ds[(ds.location==location) & (ds.BHK==2)]
    BHK3 = ds[(ds.location==location) & (ds.BHK==3)]
    matplotlib.rcParams['figure.figsize'] = (15,10)
    plt.scatter(BHK2.total_sqft,BHK2.price,color='blue',label='2 BHK', s=50)
    plt.scatter(BHK3.total_sqft,BHK3.price,marker='+', color='green',label='3 BHK', s=50)
    plt.xlabel("Total Square Feet Area")
    plt.ylabel("Price (Lakh Indian Rupees)")
    plt.title(location)
    plt.legend()

plot_scatter_chart(ds,"Rajaji Nagar")

plot_scatter_chart(ds1,"Hebbal")

def remove_BHK_outliers(ds):
    exclude_indices = np.array([])
    for location, location_ds in ds.groupby('location'):
        BHK_stats = {}
        for BHK, BHK_ds in location_ds.groupby('BHK'):
            BHK_stats[BHK] = {
                'mean': np.mean(BHK_ds.price_per_sqft),
                'std': np.std(BHK_ds.price_per_sqft),
                'count': BHK_ds.shape[0]
            }
        for BHK, BHK_ds in location_ds.groupby('BHK'):
            stats = BHK_stats.get(BHK-1)
            if stats and stats['count']>5:
                exclude_indices = np.append(exclude_indices, BHK_ds[BHK_ds.price_per_sqft<(stats['mean'])].index.values)
    return ds.drop(exclude_indices,axis='index')
ds = remove_BHK_outliers(ds)
ds.shape

plot_scatter_chart(ds,"Rajaji Nagar")

plot_scatter_chart(ds,"Hebbal")

ds.bath.unique()

ds[ds.bath>10]

plt.hist(ds.bath,rwidth=0.5)
plt.xlabel("Number of bathrooms")
plt.ylabel("Count")

ds=ds[ds.bath<ds.BHK+2]
ds.shape

data1=ds.copy()

box_plot(data1)

data1.shape

num_features=['total_sqft','bath','price','BHK']

for feature in num_features:
    data1[feature]=np.log(data1[feature])

data1=data1.drop(['bathnan','balconynan','price_per_sqft','total_sqftnan' ], axis=1)

numerical_features=[feature for feature in data1.columns if data1[feature].dtypes!='O']
for feature in numerical_features:
    print( " Skewness of {} is {}".format(feature,data1[feature].skew()))
    print( " Kurtosis  of {} is {}".format(feature,data1[feature].kurt()))

data1.head()

for feature in numerical_features:
  sns.distplot(data1[feature], hist=True)
  plt.show()

"""# Handling Rare Categorical Values"""

categorical_features3=[feature for feature in data1.columns if data1[feature].dtype=='O']
categorical_features3

for feature in categorical_features3:
    temp=data1.groupby(feature)['price'].count()/len(data1)
    temp_df=temp[temp>0.01].index
    data1[feature]=np.where(data1[feature].isin(temp_df),data1[feature],'Rare_var')

for feature in categorical_features3:
    data1.groupby(feature)['price'].median().plot.bar()
    plt.xlabel(feature)
    plt.ylabel('price')
    plt.title(feature)
    plt.show()

ds2 = data1.drop(['bath','price','balcony','total_sqft','BHK'],axis='columns')
ds2.head(3)

dummy=pd.get_dummies(ds2, drop_first="True")
dummy

ds7=pd.concat([data1, dummy], axis='columns')
ds7

ds8=ds7.drop(['availability','location','Area_type'], axis=1)
ds8.head()

feature_scale=[feature for feature in ds8.columns if feature not in ['price']]

from sklearn.preprocessing import MinMaxScaler
scaler=MinMaxScaler()
scaler.fit(ds8[feature_scale])

ds9 = pd.concat([ds7[['price']].reset_index(drop=True),
                    pd.DataFrame(scaler.transform(ds8[feature_scale]), columns=feature_scale)],
                    axis=1)

ds9

## Train Test Split
from sklearn.model_selection import train_test_split
X_train, X_test,y_train,y_test= train_test_split(ds9, ds9['price'], test_size=0.2, random_state=0)

X_train1=X_train.drop(['price'], axis=1)

X_train1

import seaborn as sns
#Using Pearson Correlation
plt.figure(figsize=(30,30))
cor = X_train1.corr()
sns.heatmap(cor, annot=True, cmap=plt.cm.CMRmap_r)
plt.show()

# with the following function we can select highly correlated features
# it will remove the first feature that is correlated with anything other feature

def correlation(dataset, threshold):
    col_corr = set()  # Set of all the names of correlated columns
    corr_matrix = dataset.corr()
    for i in range(len(corr_matrix.columns)):
        for j in range(i):
            if (corr_matrix.iloc[i, j]) > threshold: # we are interested in absolute coeff value
                colname = corr_matrix.columns[i]  # getting the name of column
                col_corr.add(colname)
    return col_corr

corr_features = correlation(X_train1, 0.8)
len(set(corr_features))

corr_features

X_train3=X_train1.drop(['bath'], axis=1)
X_train3

from sklearn.feature_selection import mutual_info_regression
# determine the mutual information
mutual_info = mutual_info_regression(X_train3.fillna(0), y_train)
mutual_info

mutual_info = pd.Series(mutual_info)
mutual_info.index = X_train3.columns
mutual_info.sort_values(ascending=False)

mutual_info.sort_values(ascending=False).plot.bar(figsize=(15,5))

from sklearn.feature_selection import SelectPercentile

## Selecting the top 30 percentile
selected_top_columns = SelectPercentile(mutual_info_regression, percentile=30)
selected_top_columns.fit(X_train3.fillna(0), y_train)

X_train3.columns[selected_top_columns.get_support()]

selected_features=['total_sqft', 'balcony', 'BHK', 'availability_Rare_var',
       'availability_Ready To Move', 'location_Raja Rajeshwari Nagar',
       'location_Rare_var', 'Area_type_Plot  Area', 'Area_type_Super built']
df_train_final=X_train3[selected_features].copy()
df_train_final

""" Modelling  """

X_test1=  X_test.drop('price', axis=1)
df_test_final=X_test1[selected_features].copy()
df_test_final.shape

def scatter_plot(x, y, title, xaxis, yaxis, size, c_scale):
    trace = go.Scatter(
    x = x,
    y = y,
    mode = 'markers',
    marker = dict(color = y, size = size, showscale = True, colorscale = c_scale))
    layout = go.Layout(hovermode= 'closest', title = title, xaxis = dict(title = xaxis), yaxis = dict(title = yaxis))
    fig = go.Figure(data = [trace], layout = layout)
    return iplot(fig)

'''Set a seed value of 43'''
seed = 43

'''Initialize all the selected regression models.'''
from sklearn.linear_model import  Ridge, Lasso, ElasticNet
from sklearn.kernel_ridge import KernelRidge
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor

'''We are interested in the following 7 regression models.
All initialized with default parameters except random_state and n_jobs.'''
lasso = Lasso(random_state = seed)
ridge = Ridge(random_state = seed)
kr = KernelRidge()
elnt = ElasticNet(random_state = seed)
xgb = XGBRegressor(random_state = seed, n_jobs = -1)
lgb = LGBMRegressor(random_state = seed, n_jobs = -1)

'''Training accuracy of our regression models. By default score method returns coefficient of determination (r_squared).'''
def train_r2(model):
    model.fit(df_train_final, y_train)
    return model.score(df_train_final, y_train)

'''Calculate and plot the training accuracy.'''
models = [lasso, ridge, kr, elnt, xgb, lgb]
training_score = []
for model in models:
    training_score.append(train_r2(model))

'''Plot dataframe of training accuracy.'''
train_score = pd.DataFrame(data = training_score, columns = ['Training_R2'])
train_score.index = [ 'LSO', 'RIDGE', 'KR', 'ELNT', 'XGB', 'LGB']
train_score = (train_score*100).round(4)
scatter_plot(train_score.index, train_score['Training_R2'], 'Training Score (R_Squared)', 'Models','% Training Score', 30, 'Rainbow')

'''Evaluate models on the holdout set(say on 30%).'''
def train_test_split_score(model):
    from sklearn.metrics import mean_squared_error
    from sklearn.model_selection import train_test_split
    X_train, X_test, Y_train, Y_test = train_test_split(df_train_final, y_train, test_size = 0.3, random_state = seed)
    model.fit(X_train, Y_train)
    prediction = model.predict(X_test)
    mse = mean_squared_error(prediction, Y_test)
    rmse = np.sqrt(mse)
    return rmse

'''Calculate train_test_split score of differnt models and plot them.'''
models = [lasso, ridge, kr, elnt, xgb, lgb]
train_test_split_rmse = []
for model in models:
    train_test_split_rmse.append(train_test_split_score(model))

'''Plot data frame of train test rmse'''
train_test_score = pd.DataFrame(data = train_test_split_rmse, columns = ['Train_Test_RMSE'])
train_test_score.index = ['LSO', 'RIDGE', 'KR', 'ELNT', 'XGB', 'LGB']
train_test_score = train_test_score.round(5)
x = train_test_score.index
y = train_test_score['Train_Test_RMSE']
title = "Models' Test Score (RMSE) on Holdout(30%) Set"
scatter_plot(x, y, title, 'Models','RMSE', 30, 'RdBu')

'''Function to compute cross validation scores.'''
def cross_validate(model):
    from sklearn.model_selection import cross_val_score
    neg_x_val_score = cross_val_score(model, df_train_final, y_train, cv = 10, n_jobs = -1, scoring = 'neg_mean_squared_error')
    x_val_score = np.round(np.sqrt(-1*neg_x_val_score), 5)
    return x_val_score.mean()

'''Calculate cross validation score of differnt models and plot them.'''
models = [lasso, ridge, kr, elnt, xgb, lgb]
cross_val_scores = []
for model in models:
    cross_val_scores.append(cross_validate(model))

'''Plot data frame of cross validation scores.'''
x_val_score = pd.DataFrame(data = cross_val_scores, columns = ['Cross Validation Scores (RMSE)'])
x_val_score.index = ['LSO', 'RIDGE', 'KR', 'ELNT', 'XGB', 'LGB']
x_val_score = x_val_score.round(5)
x = x_val_score.index
y = x_val_score['Cross Validation Scores (RMSE)']
title = "Models' 10-fold Cross Validation Scores (RMSE)"
scatter_plot(x, y, title, 'Models','RMSE', 30, 'Viridis')

"""Optimizing Hyperparameters"""

def grid_search_cv(model, params):
    global best_params, best_score
    from sklearn.model_selection import GridSearchCV
    grid_search = GridSearchCV(estimator = model, param_grid = params, cv = 10, verbose = 1,
                            scoring = 'neg_mean_squared_error', n_jobs = -1)
    grid_search.fit(df_train_final, y_train)
    best_params = grid_search.best_params_
    best_score = np.sqrt(-1*(np.round(grid_search.best_score_, 5)))
    return best_params, best_score

"""Optimize Lasso"""

''''Define hyperparameters of lasso.'''
alpha = [0.0001, 0.0002, 0.00025, 0.0003, 0.00031, 0.00032, 0.00033, 0.00034, 0.00035, 0.00036, 0.00037, 0.00038,
         0.0004, 0.00045, 0.0005, 0.00055, 0.0006, 0.0008,  0.001, 0.002, 0.005, 0.007, 0.008, 0.01]

lasso_params = {'alpha': alpha,
               'random_state':[seed]}

grid_search_cv(lasso, lasso_params)
lasso_best_params, lasso_best_score = best_params, best_score
print('Lasso best params:{} & best_score:{:0.5f}' .format(lasso_best_params, lasso_best_score))

"""Optimize Ridge"""

''''Define hyperparameters of ridge.'''
ridge_params = {'alpha':[ 9, 9.2, 9.4, 9.5, 9.52, 9.54, 9.56, 9.58, 9.6, 9.62, 9.64, 9.66, 9.68, 9.7,  9.8],
               'random_state':[seed]}

grid_search_cv(ridge, ridge_params)
ridge_best_params, ridge_best_score = best_params, best_score
print('Ridge best params:{} & best_score:{:0.5f}' .format(ridge_best_params, ridge_best_score))

"""Optimize Kernel Ridge"""

'''Define hyperparameters of kernel ridge'''
kernel_params = {'alpha':[0.27, 0.28, 0.29, 0.3],
                'kernel':['polynomial', 'linear'],
                'degree':[2, 3],
                'coef0':[3.5, 4, 4.2]}
grid_search_cv(kr, kernel_params)
kernel_best_params, kernel_best_score = best_params, best_score
print('Kernel Ridge best params:{} & best_score:{:0.5f}' .format(kernel_best_params, kernel_best_score))

"""Optimize Elastic Net|"""

'''Define hyperparameters of Elastic net.'''
elastic_params = {'alpha': [ 0.0003, 0.00035, 0.00045, 0.0005],
                 'l1_ratio': [0.80, 0.85, 0.9, 0.95],
                 'random_state':[seed]}
grid_search_cv(elnt, elastic_params)
elastic_best_params, elastic_best_score = best_params, best_score
print('Elastic Net best params:{} & best_score:{:0.5f}' .format(elastic_best_params, elastic_best_score))

"""Optimize XGB and LGB"""

'''Hyperparameters of xgb'''
xgb_opt = XGBRegressor(colsample_bytree = 0.4603, gamma = 0.0468,
                             learning_rate = 0.04, max_depth = 3,
                             min_child_weight = 1.7817, n_estimators = 2500,
                             reg_alpha = 0.4640, reg_lambda = 0.8571,
                             subsample = 0.5213, silent = 1,
                             nthread = -1, random_state = 7)

"""Let's plot the models' rmse after optimization."""
optimized_scores = pd.DataFrame({'Optimized Scores':np.round([lasso_best_score, ridge_best_score, kernel_best_score,
                  elastic_best_score,  xgb_best_score, lgb_best_score], 5)})
optimized_scores.index = ['Lasso', 'Ridge', 'Kernel_ridge', 'E_net','XGB', 'LGB']
optimized_scores.sort_values(by = 'Optimized Scores')
scatter_plot(optimized_scores.index, optimized_scores['Optimized Scores'], "Models' Scores after Optimization", 'Models','Optimized Scores', 40, 'Rainbow')

def plot_learning_curve(model):
    from sklearn.model_selection import learning_curve

    # df_train_final is training matrix and y_train is target matrix.
    # Create CV training and test scores for various training set sizes
    train_sizes, train_scores, test_scores = learning_curve(model, df_train_final, y_train,
                                            train_sizes = np.linspace(0.01, 1.0, 20), cv = 10, scoring = 'neg_mean_squared_error',
                                            n_jobs = -1, random_state = seed)


    # Create means and standard deviations of training set scores
    train_mean = np.mean(train_scores, axis = 1)
    train_std = np.std(train_scores, axis = 1)

    # Create means and standard deviations of test set scores
    test_mean = np.mean(test_scores, axis = 1)
    test_std = np.std(test_scores, axis = 1)

    # Draw lines
    plt.plot(train_sizes, train_mean, 'o-', color = 'red',  label = 'Training score')
    plt.plot(train_sizes, test_mean, 'o-', color = 'green', label = 'Cross-validation score')

    # Draw bands
    plt.fill_between(train_sizes, train_mean - train_std, train_mean + train_std, alpha = 0.1, color = 'r') # Alpha controls band transparency.
    plt.fill_between(train_sizes, test_mean - test_std, test_mean + test_std, alpha = 0.1, color = 'g')

    # Create plot
    font_size = 12
    plt.xlabel('Training Set Size', fontsize = font_size)
    plt.ylabel('Accuracy Score', fontsize = font_size)
    plt.xticks(fontsize = font_size)
    plt.yticks(fontsize = font_size)
    plt.legend(loc = 'best')
    plt.grid()

#Now plot learning curves of the optimized models in subplots.
plt.figure(figsize = (16,14))
lc_models = [lasso_opt, kernel_ridge_opt, elastic_net_opt, xgb_opt,lgb_opt]
lc_labels = ['Lasso', 'Kernel Ridge', 'Elastic Net','XGB','LGB' ]

for ax, models, labels in zip (range(1,6), lc_models, lc_labels):
    plt.subplot(3,2,ax)
    plot_learning_curve(models)
    plt.title(labels, fontsize = 15)
plt.suptitle('Learning Curves of Optimized Models', fontsize = 20)
plt.tight_layout(rect = [0, 0.03, 1, 0.97])



'''Training accuracy of our regression models. By default score method returns coefficient of determination (r_squared).'''
def train_r2(model):
    model.fit(df_train_final, y_train)
    return model.score(df_train_final, y_train)

'''Calculate and plot the training accuracy.'''
models = [lasso, ridge, kr, elnt, xgb, lgb]
training_score = []
for model in models:
    training_score.append(train_r2(model))

'''Plot dataframe of training accuracy.'''
train_score = pd.DataFrame(data = training_score, columns = ['Training_R2'])
train_score.index = [ 'LSO', 'RIDGE', 'KR', 'ELNT', 'XGB', 'LGB']
train_score = (train_score*100).round(4)
scatter_plot(train_score.index, train_score['Training_R2'], 'Training Score (R_Squared)', 'Models','% Training Score', 30, 'Rainbow')

'''Training accuracy of our regression models. By default score method returns coefficient of determination (r_squared).'''
def train_r3(model,y_pred):
    model.fit(df_train_final, y_train)
    return mean_absolute_error(y_train, y_pred)

'''Calculate and plot the training accuracy.'''
models = [lasso, ridge, kr, elnt, xgb, lgb]
training_score1 = []
for model in models:
    y_pred=model.predict(df_train_final)
    training_score1.append(train_r3(model, y_pred))

train_score1 = pd.DataFrame(data = training_score, columns = ['Training_R2'])
train_score1.index = [ 'LSO', 'RIDGE', 'KR', 'ELNT', 'XGB', 'LGB']
train_score1 = (train_score1).round(4)
scatter_plot(train_score1.index, train_score1['Training_R2'], 'Training Score (MAE)', 'Models','% Training Score', 30, 'Rainbow')

'''Training accuracy of our regression models. By default score method returns coefficient of determination (r_squared).'''
def train_r3(model,y_pred):
    model.fit(df_train_final, y_train)
    return mean_absolute_error(y_train, y_pred)

'''Calculate and plot the training accuracy.'''
models = [lasso, ridge, kr, elnt, xgb, lgb]
training_score1 = []
for model in models:
    y_pred=model.predict(df_train_final)
    training_score1.append(train_r3(model, y_pred))

train_score1 = pd.DataFrame(data = training_score, columns = ['Training_R2'])
train_score1.index = [ 'LSO', 'RIDGE', 'KR', 'ELNT', 'XGB', 'LGB']
train_score1 = (train_score1).round(4)
scatter_plot(train_score1.index, train_score1['Training_R2'], 'Training Score (MAE)', 'Models','MAE', 30, 'Rainbow')

'''Training accuracy of our regression models. By default score method returns coefficient of determination (r_squared).'''
def train_r3(model,y_pred):
    model.fit(df_train_final, y_train)
    return mean_squared_error(y_train, y_pred)

'''Calculate and plot the training accuracy.'''
models = [lasso, ridge, kr, elnt, xgb, lgb]
training_score1 = []
for model in models:
    y_pred=model.predict(df_train_final)
    training_score1.append(train_r3(model, y_pred))

train_score1 = pd.DataFrame(data = training_score1, columns = ['Training_R2'])
train_score1.index = [ 'LSO', 'RIDGE', 'KR', 'ELNT', 'XGB', 'LGB']
train_score1 = (train_score1).round(4)
scatter_plot(train_score1.index, train_score1['Training_R2'], 'Training Score (MSE)', 'Models','MAE', 30, 'Rainbow')

train_score1

for model in models:
    y_pred=model.predict(df_test_final)
    plt.scatter(y_test,y_pred,color="blue",marker="o")
    plt.plot(y_test,y_test,marker='o',
         color='green',markerfacecolor='red',
         markersize=7,linestyle='dashed')
    plt.xlabel('true price_log')
    plt.ylabel('predicted price_log')
    plt.title(model)
    plt.show()
    plt.figure(figsize=(10,6))

'''Function to compute cross validation scores.'''
def cross_validate(model):
    from sklearn.model_selection import cross_val_score
    neg_x_val_score = cross_val_score(model, df_train_final, y_train, cv = 10, n_jobs = -1, scoring = 'neg_mean_squared_error')
    x_val_score = np.round(np.sqrt(-1*neg_x_val_score), 5)
    return x_val_score.mean()

'''Calculate cross validation score of differnt models and plot them.'''
models = [lasso, ridge, kr, elnt, xgb, lgb]
cross_val_scores = []
for model in models:
    cross_val_scores.append(cross_validate(model))

'''Plot data frame of cross validation scores.'''
x_val_score = pd.DataFrame(data = cross_val_scores, columns = ['Cross Validation Scores (RMSE)'])
x_val_score.index = ['LSO', 'RIDGE', 'KR', 'ELNT', 'XGB', 'LGB']
x_val_score = x_val_score.round(5)
x = x_val_score.index
y = x_val_score['Cross Validation Scores (RMSE)']
title = "Models' 10-fold Cross Validation Scores (RMSE)"
scatter_plot(x, y, title, 'Models','RMSE', 30, 'Viridis')