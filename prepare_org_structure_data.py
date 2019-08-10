# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import os

import pandas as pd

from config import CONFIG

data_path = CONFIG["data-path"]

df = pd.read_csv(os.path.join(data_path, 'gedsOpenData.csv'), 
                 error_bad_lines=False, 
                 encoding="latin-1")

df_esdc = df[df["Department Acronym"] == "ESDC-EDSC"]

org_struc = df_esdc[["Organization Structure (EN)"]]

unique_org = org_struc.drop_duplicates()

# Replace bracket info with blank
temp = unique_org["Organization Structure (EN)"].str.replace('\(.*?\)', '')

# Split into multiple columns 
temp = temp.str.split(" :", n=-1, expand=True)

final_dirs = temp[[1,2,3,4,5,6,7]]
#==============================================================================
# Tidying the dataframe to avoid duplicates
#==============================================================================
# Dataframe to store the unique rows
unique_df = pd.DataFrame(columns=[1,2,3,4,5,6,7])
# Declare initial values
past_Nones = 0
current_Nones = 0
past_row = final_dirs.iloc[0]
#==============================================================================
# Rule: if the number of 'Nones' between two consecutive rows differ by 1, keep
# the row with fewer 'Nones'. If they differ by more than one 'Nones', then 
# keep both because these are two different paths
#==============================================================================
for idx, row in final_dirs.iloc[1:].iterrows():
    # Calculate past nones and present nones
    for cid in range(1,len(row)):
        if past_row[cid] is None:
            past_Nones += 1
        if row[cid] is None:
            current_Nones += 1
    # Check the difference between past nones and current nones
    diff = past_Nones - current_Nones
    # If diff > 0, then move onto the next row to check - Note that diff will
    # always be 1 if diff > 0 because of the tree structure of the data
    if diff > 0:
        pass
    # If diff <= 0, then the past row must be unique - add it to unique_dfs
    else:
        unique_df = unique_df.append(past_row)
    # Update past row to be the current row
    past_row = row
    # Reset the None counts
    past_Nones = 0
    current_Nones = 0


#==============================================================================
# Now create hierarchical file from above flat file
#==============================================================================
from collections import defaultdict


def ctree():
    """ One of the python gems. Making possible to have dynamic tree structure.

    """
    return defaultdict(ctree)


def build_leaf(name, leaf):
    """ 
    Recursive function to build desired custom tree structure.
    """
    res = {"name": name.rstrip(), "size": 1}

    # add children node if the leaf actually has any children
    if len(leaf.keys()) > 0:
        res["_children"] = [build_leaf(k, v) for k, v in leaf.items()]

    return res


def main():
    """ The main thread composed from two parts.

    First it's parsing the csv file and builds a tree hierarchy from it.
    Second it's recursively iterating over the tree and building custom
    json-like structure (via dict).

    And the last part is just printing the result.

    """
    tree = ctree()
    
    for _, row in unique_df.iterrows():
        # usage of python magic to construct dynamic tree structure and
        # basically grouping csv values under their parents
        leaf = tree[row[1]]
        for cid in range(1, len(row)):
            if row[cid] is None:
                break
            leaf = leaf[row[cid]]

    # building a custom tree structure
    res = []
    for name, leaf in tree.items():
        res.append(build_leaf(name, leaf))

    # printing results into the terminal
    import json
    print(json.dumps(res))
    return res


# so let's roll
result = main()

# Reduce result set slightly
slim_result = result[0]["_children"]

# Save result to JSON file on disk
import json
with open (os.path.join(data_path, 'new_org_struc.json'), 'w') as f:
    json.dump(slim_result,f)