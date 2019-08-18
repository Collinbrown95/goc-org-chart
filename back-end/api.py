'''
Created on Mon Aug 12 21:38 2019

@author: collinbrown
'''
import json

from flask import Flask, jsonify
import pandas as pd

from config import CONFIG
from search import search_contacts, search_org_chart

app = Flask(__name__)

@app.route('/test')
def test():
    return "hello world!"

@app.route('/search-org-chart', methods=["GET"])
def search_org_chart(org_chart, org_name):
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
    raise NotImplementedError

@app.route('/search-person', methods=["GET"])
def search_person(df, person_name, language):
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
    raise NotImplementedError

@app.route('/search-team', methods=["GET"])
def search_team(language):
    '''
    Searches for all of the members who belong to a particular organizational
    unit.

    Args:
        language:
            A string containing "en" or "fr" to respectively retrieve the
            content in either english or french.
    
    Returns:
        team_json:
            A list of dicts that contain the team's contact information.
    '''
    raise NotImplementedError

if __name__ == "__main__":
    app.run()