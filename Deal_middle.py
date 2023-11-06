import re
import json
"""
After the reranker generates the results, it is necessary to filter the three step inference it generates
Reorganize the Schema and Skeleton
"""


def extract_classes_from_skeleton(content):
    """Split the original skeleton into a list of cruds and a list of clauses"""
    class_pattern = re.compile(r"(def \w+\(.*?\):(?:\n    .+)+)", re.MULTILINE)

    map_crud = {}
    map_clause = {}

    for match in class_pattern.finditer(content):
        function_def = match.group(1)
        function_name = re.match(r"def (\w+)", function_def).group(1)
        if "CREATE_SPACE" in function_name or 'CREATE_Tag_Edge' in function_name or 'INSERT' in function_name or 'QUERY' in function_name or 'UPDATE' in function_name \
                or 'UPSERT' in function_name or 'DELETE' in function_name or 'OTHER' in function_name or 'GET_SUBGRPAH' in function_name or 'FIND_PATH' in function_name:
            map_crud[function_name.lower()] = "    " + function_def
        elif "GROUP_BY" in function_name or "LIMIT" in function_name or "SKIP" in function_name or "SAMPLE" in function_name or "ORDER_BY" in function_name or "WHERE" in function_name \
                or "WITH" in function_name or "UNWIND" in function_name:
            map_clause[function_name.lower()] = "    " + function_def
    return map_crud, map_clause

def extract_classes_from_schema(content):
    # Convert Node and Edge classes into a dictionary format

    # Regular expression to match class blocks
    class_pattern = re.compile(r"(class \w+\(.*?\):(?:\n    .+)+)", re.MULTILINE)

    map_node = {}
    map_edge = {}

    for match in class_pattern.finditer(content):
        class_def = match.group(1)
        class_name = re.match(r"class (\w+)", class_def).group(1)
        if "Tag" in class_def or 'Node' in class_def:
            map_node[class_name.lower()] = class_def
        elif "Edge" in class_def:
            map_edge[class_name.lower()] = class_def

    return map_node, map_edge

def extract_skeleton_from_reason(text):
    """Extract the required Skeleton from the first two steps of reasoning"""
    crud_list = []
    clause_list = []

    # Extract the necessary schema from inference
    crud_text_list = text.split("#")[1]
    print('crud_text_list', crud_text_list)
    clause_text_list = text.split("#")[2]

    require_crud = re.findall(r"'(.*?)'", crud_text_list)
    require_clause = re.findall(r"'(.*?)'", clause_text_list)
    print("require_crud", require_crud)

    for class_i in require_crud:
        class_i = class_i.strip()
        match_obj = re.match(r'(\w+)', class_i).group(1)
        if match_obj:
            crud_list.append(match_obj)
    for class_i in require_clause:
        class_i = class_i.strip()
        match_obj = re.match(r'(\w+)', class_i).group(1)
        if match_obj:
            clause_list.append(match_obj)
    return crud_list, clause_list

def extract_schema_from_reason(text):
    """Extract the required node or edge classes from the first two steps of reasoning"""

    schema_list = []

    # Extract the necessary schema from inference
    text_list = text.split("#")[-1]
    require_classes = re.findall(r"'(.*?)'", text_list)

    for class_i in require_classes:
        class_i = class_i.strip()
        match_obj = re.match(r'(\w+)', class_i).group(1)
        if match_obj:
            schema_list.append(match_obj)

    return schema_list

def skeleton_list_map(crud_list, clause_list, map_crud, map_clause):
    # Filter and concatenate from the map

    new_skeleton = "# The request CRUD function\n"
    new_skeleton += 'class CRUD():\n'
    total_crud = 0
    total_clause = 0

    for i in crud_list:
        i = str(i).lower()
        if i in map_crud:
            new_skeleton += map_crud[i] + "\n"
            total_crud += 1
    new_skeleton += '# The request subfunction\n'
    new_skeleton += 'class SUBFUNCTION():\n'

    for i in clause_list:
        i = str(i).lower()
        if i in map_clause:
            new_skeleton += map_clause[i] + "\n"
            total_clause += 1

    if total_crud < len(crud_list) or total_clause < len(clause_list):
        # There are incorrect classes in the list
        return None

    return new_skeleton

def schema_list_map(schema_list, map_node, map_edge):
    # Filter and concatenate from the map

    new_schema = "# This is the partial schema of the graph\n"
    new_schema += '# Nodes\n'
    total_node = 0
    total_edge = 0

    for i in schema_list:
        i = str(i).lower()
        if i in map_node:
            new_schema += map_node[i] + "\n"
            total_node += 1
    new_schema += '# Edges\n'
    for i in schema_list:
        i = str(i).lower()
        if i in map_edge:
            new_schema += map_edge[i] + "\n"
            total_edge += 1

    if total_node + total_edge < len(schema_list) or (total_node == 0 or total_node == 0):
        # There are incorrect classes in the list
        return None

    return new_schema

def deal_schema_skeleton(sllm_out, schema, skeleton):
    # Complete schema and skeleton filtering and assembly

    schema_new = ''
    skeleton_new = ''

    schema_list = extract_schema_from_reason(sllm_out)
    crud_list, clause_list = extract_skeleton_from_reason(sllm_out)
    print(crud_list)
    map_node, map_edge = extract_classes_from_schema(schema)
    map_crud, map_clause = extract_classes_from_skeleton(skeleton)

    if schema_list == None or len(schema_list) < 2:
        schema_new = schema
    else:
        schema_new = schema_list_map(schema_list, map_node, map_edge)
        if schema_new == None:
            schema_new = schema
    if crud_list == None or crud_list == []:
        skeleton_new = skeleton
    else:
        skeleton_new = skeleton_list_map(crud_list, clause_list, map_crud, map_clause)
        if skeleton_new == None:
            skeleton_new = skeleton

    return schema_new, skeleton_new
