'''
Created on Fri Aug 9 20:31 2019

@author: collinbrown

This script runs a scheduled job every 24 hours to fetch the most up-to-date
GEDS data from open.canada.ca/data, preprocess it into (i) a table that maps
names to business units and (ii) a JSON object that contains the organization
chart.
'''

from utils import fetch_geds, get_org_chart, preprocess_geds

from config import CONFIG

def prepare_data(subset=None):
    '''
    This funcion extracts geds data from open.canada.ca/data and processes it
    into (1) a csv file that contains the business unit that each person 
    belongs to and (2) a json file that contains the org chart.

    Args:
        subset:
            A string containing the acronym found in the "Department Acronym"
            field in the geds dataframe (e.g. "ESDC-EDSC") - used to build the
            org chart tool for only a subset of geds.
    Returns:
        (df, org_chart):
            A two-tuple containing the dataframe augmented with the business unit
            that each person belongs to and a dict-like object containing the org
            chart.
    '''
    # Step 1: get a dataframe from the geds url. Note that if one wants to
    # build the org chart tool for only a subset of the data (e.g. ESDC-specific),
    # this is toggled by setting the "subset" parameter below to the acronym found 
    # in the "Department Acronym" field in the geds dataframe (e.g. "ESDC-EDSC")
    df = fetch_geds(CONFIG["geds-url"], subset=subset)

    # Step 2: Pre-process searchable fields - need to do things like lowercase
    # name fields, strip extra whitespaces, etc.
    df = preprocess_geds(df)
    # Step 3: get the org chart for geds
    org_chart = get_org_chart(df, tree_depth=7)
    return df, org_chart

if __name__ == "__main__":
    df, org_chart = prepare_data(subset="ESDC-EDSC")
    # Save each of these files to disk temporarily
    import sqlite3
    # Connect to sqlite3 database
    conn = sqlite3.connect(CONFIG["db-path"])
    # Dump the pandas dataframe into the "contacts" table of the db - if
    # the table already exists, replace it (i.e. drop the table before
    # inserting new rows)
    df.to_sql('contacts', con=conn, if_exists="replace")
    df.to_csv(CONFIG["df-path"])
    # Write the org chart to disk as JSON
    import json
    with open (CONFIG["org-chart-path"], 'w') as f:
        json.dump(org_chart,f)