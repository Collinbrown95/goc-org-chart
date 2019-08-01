# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 11:06:33 2019

@author: collin.brown
"""

# slim_result is the output of processing of the geds data
root = slim_result[0]
#==============================================================================
# Searching the json for specific path
#==============================================================================
def get_path_to_node(val, root_node):
    '''
    Gets path to specific node from root.

    Args:
        val:
            TODO
        root_node:
            TODO

    Returns:
        stack:
            TODO
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


path_to_node = get_path_to_node("Planification Services ", root)

def access_node(path_to_node, root_node):
    '''

    '''
    current_node = root_node
    parent_node = root_node
    for i in path_to_node:
        if "_children" in current_node.keys():
            parent_node = current_node
            current_node = current_node["_children"][i]
    
    return current_node, parent_node