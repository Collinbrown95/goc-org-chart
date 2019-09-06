'''
Created on Mon Aug 12 21:40 2019

@author: collinbrown
'''
from response_templates import NO_RESULTS_FOUND

def search_contacts(cursor, var, query_string):
    '''
    Searches a database pointed to by `cursor` for `query_string`.
    
    Args:
        cursor:
            An instance of <class 'sqlite3.Cursor'> that is connected to
            acronyms.db
        var:
            A tuple of length 1 that contains the team name to be searched.
            E.g. ('Chief Data Office',)
        query_string:
            A string that represents a valid SQL query to either the
            acronyms_en or acronyms_fr tables of the acronyms database.
    
    Returns:
        json_response:
            A list of dicts that contain the results that matched for a given
            acronym. If there were no matches then the NO_RESULTS_FOUND
            response is returned.
    '''
    json_response = []
    for row in cursor.execute(query_string, var):
        print(row)
        json_response.append(
            {
                "Surname": row[0],
                "GivenName": row[1],
                "Title (EN)": row[2],
                "Telephone Number": row[3],
                "Email": row[4],
                "Street Address (EN)": row[5],
                "Country (EN)": row[6],
                "Province (EN)": row[7],
                "Postal Code": row[8],
                "Org Name": row[9]
            }
        )
    # If response is empty, return the NO_RESULTS_FOUND response;
    # otherwise return the results
    if len(json_response) == 0:
        return NO_RESULTS_FOUND
    else:
        return json_response

def search_org_chart(org_chart, org_name):
    '''
    Searches a JSON (loaded in memory as a python dict) for a specific
    business unit.

    Args:
        org_chart:
            A dict containing the loaded org chart from a JSON file.
        org_name:
            Name of the business unit that is to be searched for.

    Returns:
        path_to_org:
            A list containing the path to the given business unit in
            the org chart.
    '''
    return get_path_to_node(org_name, org_chart)
    

def get_path_to_node(val, root_node):
    '''
    Gets path to specific node from root
    '''
    node_found = False
    stack = []
    def get_path_rec(node):
        '''
        '''
        # Important: python defaults to the innermost scope; need to explicitly
        # declare non-local variables as such
        nonlocal node_found
        #print(node_found)
        if node_found:
            pass
        if "_children" in node.keys():
            for i in range(0, len(node["_children"])):
                if not node_found:
                    stack.append(i)
                    get_path_rec(node["_children"][i])
        
        if node["name"] == val and not node_found:
            print("Found it!")
            node_found = True
            pass
        elif not node_found:
            stack.pop()
        
    get_path_rec(root_node)
    print(stack)
    return stack