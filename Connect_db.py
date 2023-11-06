import json
import os

from nebula3.gclient.net import ConnectionPool
from nebula3.Config import Config
from Config import *

# Import necessary modules and packages

# Configuration
config = Config()
config.max_connection_pool_size = MAX_CONNECTION_POOL_SIZE

# Establish a connection pool
connection_pool = ConnectionPool()
ok = connection_pool.init([('127.0.0.1', 9669)], config)
session = connection_pool.get_session(USERNAME, PASSWORD)



# Define a function to process database tests
def process_db_test(graph_name, content, result):
    # Set the active graph
    use_graph = f'USE {graph_name}'
    session.execute(use_graph)
    error = ''
    gpt_result_list = []

    # Execute the query
    gpt_result = session.execute(content)

    # Check if the query execution succeeded
    if gpt_result.is_succeeded() == False:
        gpt_result = "语法错误"
    else:
        n = gpt_result.row_size()
        for i in range(n):
            gpt_result_list.append(str(gpt_result.row_values(i)))
        if len(gpt_result_list) == 0 and len(result) != 0:
            gpt_result = "语法错误"
        elif len(gpt_result_list) != 0 and gpt_result_list[0] == "[__NULL__]" and len(result) != 0:
            gpt_result= "语法错误"
        else:
            gpt_result = gpt_result_list
    return gpt_result



# Define a function to execute database tests
def execute_db(test_data, gpt_output):
    graph_name = ''

    # Determine the graph based on the test data class
    if test_data.get('class') == "disease":
        graph_name = "disease"
    elif test_data.get('class') == "potter":
        graph_name = "harrypotter_new"
    elif test_data.get('class') == "nba":
        graph_name = "nba"

    # Execute the test and return the result
    return process_db_test(graph_name, gpt_output, test_data['result'])