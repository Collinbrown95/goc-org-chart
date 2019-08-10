'''
Created on Fri Aug 9 20:31 2019

@author: collinbrown

This script runs a scheduled job every 24 hours to fetch the most up-to-date
GEDS data from open.canada.ca/data, preprocess it into (i) a table that maps
names to business units and (ii) a JSON object that contains the organization
chart.
'''

from utils import fetch_geds, get_business_unit

from config import CONFIG

# Step 1: get a dataframe from the pandas url. Note that if one wants to
# build the org chart tool for only a subset of the data (e.g. ESDC-specific),
# this is toggled by setting the "subset" parameter below to the acronym found 
# in the "Department Acronym" field in the geds dataframe (e.g. "ESDC-EDSC")
df = fetch_geds(CONFIG["geds-url"], subset=None)

# Step 2: for each person in geds, get the business unit they belong to
df = get_business_unit(df)

# Step 3: get the org chart for geds
org_chart = get_org_chart(df, tree_depth=7)