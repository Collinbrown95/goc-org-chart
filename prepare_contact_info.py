#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 22:16:32 2019

@author: collinbrown

The goal of this script is to attach a business unit to every person in the
GEDs dataset.
"""
import os
import pandas as pd

#from config import CONFIG

data_path = CONFIG["data-path"]

df = pd.read_csv(os.path.join(data_path, 'gedsOpenData.csv'), 
                 error_bad_lines=False, 
                 encoding="latin-1")
# Replace bracket info with blank
df["org-structure-list"] = df["Organization Structure (EN)"].str.replace('\(.*?\)', '')
# Get a list containing business units
df["org-structure-list"] = df["org-structure-list"].str.split(" :", n=-1, expand=False)
# =============================================================================
# We want to get the business unit that each person belongs to, so we need to
# return the last element of each list.
# =============================================================================
df["business-unit"] = df["org-structure-list"].apply(lambda x: x[-1]).str.rstrip()
# separate rows where there is only one person for a business unit - these are
# the heads of those units - for cases where one business unit maps to multiple
# people, this is a team
unique_df = df[~df["business-unit"].duplicated()]
# Duplicated dataframe
dup_df = df[df["business-unit"].duplicated()]