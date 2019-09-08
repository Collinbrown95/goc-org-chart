import csv
from io import BytesIO
from collections import defaultdict

import pandas as pd
from urllib.request import urlopen
from zipfile import ZipFile

from config import CONFIG


def fetch_geds(url, subset=None):
    '''
    Fetches the web-scraped geds dataset from open.canada.ca/data

    Args:
        url:
            A string containing the url to the open.canada.ca/data web page
            that downloads a zipped csv containing the geds dataset.
        subset:
            A string containing the acronym found in the "Department Acronym"
            field in the geds dataframe (e.g. "ESDC-EDSC") - used to build the
            org chart tool for only a subset of geds.
    
    Returns:
        df:
            A pandas dataframe containing the original contents of the zipped
            csv file.
    '''
    # Fetch the response from the geds url
    resp = urlopen(CONFIG["geds-url"])
    # Extract the file from the bytes object returned by urlopen
    zipped_file = ZipFile(BytesIO(resp.read()))
    # Extract the csv contents line-by-line
    lines = []
    # Note that zipped_file.namelist() returns ['gedsOpenData.csv'], so
    # zipped_file.namelist()[0] returns the file name
    for idx, line in enumerate(zipped_file.open(zipped_file.namelist()[0]).readlines()):
        # Need to use the csv module to read the string returned by line.decode()
        # Reason is csv module contains the logic to parse commas that are
        # contained within double quotes.
        decoded = [str(line.decode('ISO-8859-1'))]
        line = [item for item in csv.reader(decoded)][0]
        # There are a few observations (~90) that are not parsed correctly - this
        # needs to be investigated further.
        if len(line) == 44:
            lines.append(line)
    # Convert to pandas dataframe
    df = pd.DataFrame(lines[1:], columns=lines[0])
    # Select a subset of the dataframe (if any)
    if subset is not None:
        df = df[df["Department Acronym"] == subset]
    return df

def preprocess_geds(df):
    '''
    Applies a few regular expressions to the fields that will be used in
    downstream table lookup operations. Creates new searchable fields that
    will be more robust to variations in characters, casing, etc.
    
    Specifically, the organization name:
        1. all characters are converted to lowercase
        2. replace ,.- characters with a blank space
        3. replace the & character with 'and'
        4. any occurence of two spaces should be replaced with a single space
        5. the text should be stripped of trailing spaces/characters on either side
    
    For peoples' names:
        1. convert to lowercase
        2. create three searchable fields - firstName, lastName, fullName
        3. strip trailing characters on either side of the name
    Args:
        df:
            A pandas dataframe containing the original contents of the zipped
            csv file.
    
    Returns:
        df:
            The same pandas dataframe that was input, but augmented with
            normalized column values.
    '''
    # `Organization Name (EN)`
    df["OrgNameCleanEN"] = df["Organization Name (EN)"].str.lower()
    df["OrgNameCleanEN"] = df["OrgNameCleanEN"].str.replace(',', ' ')
    df["OrgNameCleanEN"] = df["OrgNameCleanEN"].str.replace('/', ' ')
    df["OrgNameCleanEN"] = df["OrgNameCleanEN"].str.replace('.', ' ')
    df["OrgNameCleanEN"] = df["OrgNameCleanEN"].str.replace('-', ' ')
    df["OrgNameCleanEN"] = df["OrgNameCleanEN"].str.replace('&', ' and ')
    df["OrgNameCleanEN"] = df["OrgNameCleanEN"].str.replace(' +', ' ')
    df["OrgNameCleanEN"] = df["OrgNameCleanEN"].str.strip()

    # `Organization Name (FR)`
    df["OrgNameCleanFR"] = df["Organization Name (FR)"].str.lower()
    df["OrgNameCleanFR"] = df["OrgNameCleanFR"].str.replace(',', ' ')
    df["OrgNameCleanFR"] = df["OrgNameCleanFR"].str.replace('/', ' ')
    df["OrgNameCleanFR"] = df["OrgNameCleanFR"].str.replace('.', ' ')
    df["OrgNameCleanFR"] = df["OrgNameCleanFR"].str.replace('-', ' ')
    df["OrgNameCleanFR"] = df["OrgNameCleanFR"].str.replace('&', ' et ')
    df["OrgNameCleanFR"] = df["OrgNameCleanFR"].str.replace(' +', ' ')
    df["OrgNameCleanFR"] = df["OrgNameCleanFR"].str.strip()

    # Create three normalized columns: firstName, lastName, fullName
    df["firstName"] = df["GivenName"].str.lower()
    df["firstName"] = df["firstName"].str.strip()
    df["lastName"] = df["Surname"].str.lower()
    df["lastName"] = df["lastName"].str.strip()
    df["fullName"] = df["firstName"] + " " + df["lastName"]
    return df

def get_org_chart(df, tree_depth=7):
    '''
    Constructs a dict-like object from the geds dataframe that contains the
    organization structure. 

    Args:
        df:
            A pandas dataframe containing the contents of the csv file
            loaded directly from geds.
        tree_depth:
            An int specifying how many levels deep the org chart tree
            should go. One might want to limit the depth so that business
            units below a certain level are aggregated (e.g. everything
            below the "division" level is aggregated). Set to 7 by default.
    
    Returns:
        org_chart:
            A dict-like object (defaultdict) containing the organization
            structure.
    '''
    # Keep only the "Organization Structure (EN)" column of the dataframe;
    # drop duplicates because we only want each entry to appear once;
    # preprocess the text in teh column.
    org_struc = df['Organization Structure (EN)'].str.replace('\(.*?\)', '').drop_duplicates()
    # Split the above series into `tree_depth` different columns
    org_struc = org_struc.str.split(" :", n=-1, expand=True)
    columns = [i for i in range(0, tree_depth + 1, 1)]
    org_struc = org_struc[columns]
    # Need to restructure the org_struc dataframe to avoid duplicates when
    # it is parsed into a dict-like object.
    #==============================================================================
    # Algorithm: if the number of 'Nones' between two consecutive rows differ by 1,
    # keep the row with fewer 'Nones'. If they differ by more than one 'Nones', then 
    # keep both because these are two different paths
    #==============================================================================
    # Dataframe to store the unique rows
    unique_df = pd.DataFrame(columns=[1,2,3,4,5,6,7])
    # Declare initial values
    past_Nones = 0
    current_Nones = 0
    past_row = org_struc.iloc[0]
    # Loop over all rows in org_struc
    for idx, row in org_struc.iloc[1:].iterrows():
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
    # At this point unique_df contains all of the unique rows such that the
    # algorithm that recursively parses it into a tree won't create duplicates.
    # Now we get the dict-like structure containing the org chart.
    org_chart = flat_to_hierarchical(unique_df)
    return org_chart


#==============================================================================
# Functions to convert flat file into hierarchical file - borrowed from this
# (https://stackoverflow.com/questions/43757965/convert-csv-to-json-tree-structure)
# StackExchange post - see link for more detail on how these functions work.
#==============================================================================
def ctree():
    """ 
    One of the python gems. Making possible to have dynamic tree structure.
    """
    return defaultdict(ctree)

def build_leaf(name, leaf):
    """ 
    Recursive function to build desired custom tree structure.

    Args:
        name:
            A string containing the name that is attached to this node
            of the tree.
        leaf:
            A dict-like object.
    """
    res = {"name": name.rstrip()}

    # add children node if the leaf actually has any children
    if len(leaf.keys()) > 0:
        res["_children"] = [build_leaf(k, v) for k, v in leaf.items()]

    return res


def flat_to_hierarchical(df):
    """ 
    The main thread composed from two parts. First it's parsing the csv 
    file and builds a tree hierarchy from it. Second it's recursively iterating
    over the tree and building custom json-like structure (via dict).

    Args:
        df:
            A pandas dataframe that is formatted in such a way that there are
            no duplicates (see the body of get_org_chart() for details on how
            to do this).
    Returns:
        res:
            A dict-like object containing the org structure.
    """
    tree = ctree()
    for _, row in df.iterrows():
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
    return res

#==============================================================================
# Misc. API utility functions
#==============================================================================

def normalize_team_name(team_name):
    '''
    Applies regular expressions to account for common variations that
    someone may use to request a team name.

    Specifically:
        1. all characters are converted to lowercase
        2. replace ,.- characters with a blank space
        3. replace the & character with 'and'
        4. any occurence of two spaces should be replaced with a single space
        5. the text should be stripped of trailing spaces/characters on either side

    Args:
        team_name:
            A string containing the team name that is requested.
    
    Returns:
        team_name:

    '''
    team_name = str(team_name)
    team_name = team_name.lower()
    team_name = team_name.replace(',', ' ')
    team_name = team_name.replace('/', ' ')
    team_name = team_name.replace('.', ' ')
    team_name = team_name.replace('-', ' ')
    team_name = team_name.replace('&', ' and ')
    team_name = team_name.replace(' +', ' ')
    team_name = team_name.strip()
    return team_name

def normalize_person_name(person_name):
    '''
    Applies regular expressions to account for common variations that
    someone may use to request a person's name.

    Specifically:
        1. all characters are converted to lowercase
        2. replace ,.- characters with a blank space
        4. any occurence of two spaces should be replaced with a single space
        5. the text should be stripped of trailing spaces/characters on either side

    Args:
        person_name:
            A string containing the team name that is requested.
    
    Returns:
        person_name:
    '''
    person_name = str(person_name)
    person_name = person_name.lower()
    person_name = person_name.replace(","," ")
    person_name = person_name.replace("."," ")
    person_name = person_name.replace("-"," ")
    # Replace one or more spaces with one space
    person_name = person_name.replace(" +"," ")
    person_name = person_name.strip()
    return person_name