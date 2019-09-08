'''
Created on Mon Aug 12 21:38 2019

@author: collinbrown
'''
import os
import sys
import json
import sqlite3

from flask import Flask, jsonify, request

import pandas as pd

from config import CONFIG
from search import (search_contacts,
                    search_org_chart, 
                    search_org_name)
from response_templates import (LANGUAGE_ERROR, 
                               NO_TEAM_NAME_ERROR, 
                               NO_LANG_ERROR,
                               NO_PERSON_NAME_ERROR)
from utils import normalize_team_name, normalize_person_name
# Load org chart dict into memory
with open(CONFIG["org-chart-path"], 'r') as f:
    org_chart = json.load(f)[0]  # The JSON is a list of 1 object

app = Flask(__name__)

@app.route('/test')
def test():
    return "hello world!"

@app.route('/search-org-chart', methods=["GET"])
def get_org_chart():
    '''
    Recursively searches the tree containing the organizational chart;
    if the business unit is found, then returns the path to the business unit.

    Args:
        org_chart:
            A dict-like object that contains a searchable organizational chart.
        org_name:
            A string containing the name of the business unit the user is
            searching for.
    Returns:
        path:
    '''
    # Open sqlite db connection
    conn = sqlite3.connect(CONFIG["db-path"])
    cursor = conn.cursor()
    # If the lang parameter was not specified, return error to the client
    if request.args.get("lang") is None:
        return jsonify(NO_LANG_ERROR)
    else:
        lang = str(request.args.get("lang"))
    
    # If there was no search term return error to the client
    if request.args.get("team_name") is None:
        return jsonify(NO_TEAM_NAME_ERROR)
    else:
        # Normalize the requested team_name in case it contains 
        # irregular characters/casing/etc.
        team_name = str(request.args.get("team_name"))
        team_name = normalize_team_name(team_name)
        var = (team_name,)
    if lang == "en":
        # First, lookup `Organization Name (EN)` from OrgNameCleanEN
        query_string = """SELECT `Organization Name (EN)`
                       FROM contacts WHERE OrgNameCleanEN = ?"""
        org_name_clean = search_org_name(cursor, var, query_string)
        print("ORG NAME IS ", org_name_clean)
        print(type(org_name_clean))
        sys.stdout.flush()
        # TODO: Might want to make this return something more standard
        # for downstream API calls. For now just return cleaned name.
        return jsonify(org_name_clean)
    elif lang == "fr":
        # TODO: add this feature in French
        raise NotImplementedError
    else:
        # Return response code 400 + message
        return jsonify(LANGUAGE_ERROR)

@app.route('/search-person', methods=["GET"])
def get_person():
    '''
    Searches the GEDS contacts table for a specific person.

    Args:
        df:
            A pandas dataframe containing the table of GEDS contact information
        person_name:
            A string containing the name of a person in the format "first-name last-name"
            (i.e. first name followed by one space followed by last name). Future versions
            should handle approximate (fuzzy) matching, but currently the search is exact
            match only.
        language:
            A string that is either "en" for english or "fr" for french. The returned
            results will be in the specified language.
    
    Returns:
        If a match is found, will return a JSON object for each match formatted 
        as follows:
        {
            "Surname": "Doe",
            "GivenName": "John",
            "Title (EN)": "Some Position Title",  // This will be (FR) if language == 'fr'
            "Telephone Number": "999-999-9999",
            "Email": "john.doe@canada.gc.ca",
            "Street Address (EN)": "123 Fake St.",
            "Postal Code": "A1A A1A",
            "Province (EN)": "Quebec",
            "Department Name (EN)": "Some Department",
            "Organization Name (EN)": "Business Management Division"
        }
        If no match is found, returned result will be empty.
    '''
    # Open sqlite db connection
    conn = sqlite3.connect(CONFIG["db-path"])
    cursor = conn.cursor()
    print("Got here")
    sys.stdout.flush()
    # If the lang parameter was not specified, return error to the client
    if request.args.get("lang") is None:
        return jsonify(NO_LANG_ERROR)
    else:
        lang = str(request.args.get("lang"))
    
    # If there was no search term return error to the client
    if request.args.get("person_name") is None:
        return jsonify(NO_PERSON_NAME_ERROR)
    else:
        # Normalize the requested person_name in case it contains 
        # irregular characters/casing/etc.
        person_name = str(request.args.get("person_name"))
        person_name = normalize_person_name(person_name)
        var = (person_name,)
        print(var)
        sys.stdout.flush()
    if lang == "en":
        query_string = """SELECT Surname, GivenName, `Title (EN)`, 
                       `Telephone Number`, Email, `Street Address (EN)`, 
                       `Country (EN)`, `Province (EN)`, `Postal Code`,
                       `Organization Name (EN)` FROM contacts WHERE fullName 
                       = ?"""
        return jsonify(search_contacts(cursor, var, query_string))
    elif lang == "fr":
        # TODO: add this feature in French
        raise NotImplementedError
    else:
        # Return response code 400 + message
        return jsonify(LANGUAGE_ERROR)

@app.route('/search-team', methods=["GET"])
def get_team():
    '''
    Searches for all of the members who belong to a particular organizational
    unit.

    Args:
        language:
            A string containing "en" or "fr" to respectively retrieve the
            content in either english or french.
        team_name:
            A string containing the name of the unit that we want to retrieve
            the contact info for.
    
    Returns:
        team_json:
            A list of dicts that contain the team's contact information.
    '''
    # Open sqlite db connection
    conn = sqlite3.connect(CONFIG["db-path"])
    cursor = conn.cursor()
    # If the lang parameter was not specified, return error to the client
    if request.args.get("lang") is None:
        return jsonify(NO_LANG_ERROR)
    else:
        lang = str(request.args.get("lang"))
    
    # If there was no search term return error to the client
    if request.args.get("team_name") is None:
        return jsonify(NO_TEAM_NAME_ERROR)
    else:
        # Normalize the requested team_name in case it contains 
        # irregular characters/casing/etc.
        team_name = str(request.args.get("team_name"))
        #team_name = normalize_team_name(team_name)
        var = (team_name,)
    if lang == "en":
        query_string = """SELECT Surname, GivenName, `Title (EN)`, 
                       `Telephone Number`, Email, `Street Address (EN)`, 
                       `Country (EN)`, `Province (EN)`, `Postal Code`, `Organization Name (EN)` 
                       FROM contacts WHERE `Organization Name (EN)` 
                       = ?"""
        return jsonify(search_contacts(cursor, var, query_string))
    elif lang == "fr":
        # TODO: add this feature in French
        raise NotImplementedError
    else:
        # Return response code 400 + message
        return jsonify(LANGUAGE_ERROR)
        
if __name__ == "__main__":
    app.run()