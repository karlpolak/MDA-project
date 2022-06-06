import pandas as pd
import plotly.express as px

dataset = pd.read_csv('https://mda-project-poland.s3.eu-west-3.amazonaws.com/VAR+results.csv')
dataset = dataset.query("Year <= 2032")

countries = dataset['Country'].unique()

Asia = ['China', 'Uzbekistan', 'Tajikistan', 'Japan', 'Republic of Korea', 'India' 'Pakistan', 'Azerbaijan', 'Iraq', 'Israel', 'Indonesia', 'Malaysia', 'Viet Nam']
Europe = ['Finland', 'Denmark', 'France', 'Italy', 'Poland', 'Ukraine']
Africa = ['Morocco', 'Tunisia', 'Central African Republic', 'Gabon', 'South Africa', 'Zimbabwe']
Americas = ['Argentina', 'Brazil', 'Bolivia', 'Suriname', 'El Salvador', 'Haiti', 'Canada', 'United States of America', 'Mexico']
Oceania = ['Australia', 'new zealand']

alpha_list = {'China': 'CHN',
              'Uzbekistan': 'UZB',
              'Tajikistan': 'TJK',
              'Japan': 'JPN',
              'Republic of Korea': 'KOR',
              'India': 'IND',
              'Pakistan': 'PAK',
              'Azerbaijan': 'AZE',
              'Iraq': 'IRQ',
              'Israel': 'ISR',
              'Indonesia': 'IDN',
              'Malaysia': 'MYS',
              'Viet Nam': 'VNM',
              'Finland': 'FIN',
              'Denmark': 'DNK',
              'France': 'FRA',
              'Italy': 'ITA',
              'Poland': 'POL',
              'Ukraine': 'UKR',
              'Morocco': 'MAR',
              'Tunisia': 'TUN',
              'Central African Republic': 'CAF',
              'Gabon': 'GAB',
              'South Africa': 'ZAF',
              'Zimbabwe': 'ZWE',
              'Argentina': 'ARG',
              'Brazil': 'BRA',
              'Bolivia': 'BOL',
              'Suriname': 'SUR',
              'El Salvador': 'SLV',
              'Haiti': 'HTI',
              'Canada': 'CAN',
              'United States of America': 'USA',
              'Mexico': 'MEX',
              'Australia': 'AUS',
              'new zealand': 'NZL',
              }

dataset['Continent'] = ''
dataset['iso_alpha'] = ''

continent = []
for country in countries:
    dataset.loc[dataset['Country'] == country, 'iso_alpha'] = alpha_list[country]
    
    if country in Asia:
        dataset.loc[dataset['Country'] == country, 'Continent'] = 'Asia'
    if country in Africa:
        dataset.loc[dataset['Country'] == country, 'Continent'] = 'Africa'
    if country in Europe:
        dataset.loc[dataset['Country'] == country, 'Continent'] = 'Europe'
    if country in Americas:
        dataset.loc[dataset['Country'] == country, 'Continent'] = 'Americas'
    if country in Oceania:
        dataset.loc[dataset['Country'] == country, 'Continent'] = 'Oceania'

# our bubble cannot handle negative values => negative water stress is essentially no water stress (zero) after all
dataset.loc[dataset['Water stress']<0,'Water stress'] = 0