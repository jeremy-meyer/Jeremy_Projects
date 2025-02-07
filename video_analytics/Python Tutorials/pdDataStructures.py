#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 21 07:45:14 2018

@author: jeremy.meyer
"""

import pandas as pd

#Series. s.index are row names. Can mix variabule types
s = pd.Series([1,2,3,4,5,6])
s.index = ['label1', 'l2', 'l3', 'l4', 'l5', 'l6']
print(s)

#Subsetting
s[1]
s[:2] #First 2 elements
s[1:4] 
s[-2:] #Last two elements
s[[0,2]] #First and third elements
s['label1'] #Also dictionary-like

#Will subset according to boolean T/Fs
s[[True, False, True, True, False, False]]
s[[1,4,2,3]] #And subset out of order
s[s > s.mean()] #Elements greater than the mean
sum(s > 2) #Number of elements greater than 2

#Vector Math. Adds according to labels
s*3
s == 3
s + s*s
s[1:] + s[:-1]

#Data Frames
d = {'one' : pd.Series([1., 2., 3.], index=['a', 'b', 'c']), \
     'two' : pd.Series([1., 2., 3., 4.], index=['a', 'b', 'c', 'd'])}

d = pd.DataFrame(d)

d.index #Row Names
d.columns #Column Names

#Change row names
d.index = range(1,5)
#Rename last column
d.rename(columns={d.columns[-1]: '2'}, inplace=True)

#dfs always rbind
df = pd.DataFrame([('A', 'B', 'C'), (1,2,3), ('THis', 'is', 'aTest')], columns = ['Vectors', 'are_stored', 'as_rows'])

df2 = pd.DataFrame([pd.Series([10,20,30]), pd.Series([4,5,6])]) #From Series

#Join (cbind). Outer join -> axis=0
df3 = pd.concat([df, df2], axis=1)

# This is by column name, not position
df3[0] = [0, 10, 100]

sleep = pd.read_csv('sleep.csv', header=None, index_col=0)
sleep.columns           #Column names
sleep.index             #Row Names
sleep[8]                #Subsetting by column
sleep[sleep[8] > 8]     #Only rows with sleep quality > 8


