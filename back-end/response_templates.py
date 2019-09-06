# Error for if the user tries to pass a value other than 'en' or 'fr' to the lang parameter.
LANGUAGE_ERROR = {
    "status": 400,
    "message": "Only 'en' and 'fr' are accepted values of the parameter lang."
}

# Response for if the user did not include the lang parameter
NO_LANG_ERROR = {
    "status": 400,
    "message": "A value for the 'lang' parameter must be specified. Valid values of 'lang' are 'en' and 'fr'."
}

# Error for if the user tries to submit a request without entering a team_name parameter.
NO_TEAM_NAME_ERROR = {
    "status": 400,
    "message": "A value must be specified for the 'team_name' parameter."
}

# Error for if the user tries to submit a request without entering a team_name parameter.
NO_PERSON_NAME_ERROR = {
    "status": 400,
    "message": "A value must be specified for the 'person_name' parameter."
}

# Response for if the user submits a successful request but no results were found.
NO_RESULTS_FOUND = {
    "status": 404,
    "message": "No results were found that match the request."
}
