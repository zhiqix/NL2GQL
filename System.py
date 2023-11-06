import pandas as pd
from Config import *
from Vector_store import *
from Smaller_LLM import *
from Deal_middle import *
from Bigger_LLM import *
from Connect_db import *
from Evaluation import *

# overall system
def deal_embedding(embedding_text):
    cleaned_string = embedding_text.strip('[]').replace("\n", "").split()

    # 将字符串列表转换为浮点数列表
    float_list = [float(x) for x in cleaned_string]
    return float_list

if __name__ == '__main__':

    # input one of test_data
    dict ={"prompt": "Can you help me find the player information with name 'Boris Diaw'?", "content": "MATCH (n:player) WHERE id(n) == \"Boris Diaw\" RETURN n;", "text_schema":"the node type:[{'player':[name,age],'team':[name],'bachelor':[name,speciality]}],the edge type:[{'like':[likeness],'serve':[start_year,end_year],'teammate':[start_year]}]","schema":"# this is the schema of this graph\n# Nodes\nclass Tag():\n    def __init__(self,tag_name):\n        self.tag_name=tag_name\n\nclass player(Tag):\n    def __init__(self,vid,name:str,age:int):\n        self.vid=vid\n        self.name=name\n        self.age=age\n\nclass team(Tag):\n    def __init__(self,vid,name:str):\n        self.vid=vid\n        self.name=name\n\nclass bachelor(Tag):\n    def __init__(self,vid,name:str,speciality:str):\n        self.vid=vid\n        self.name=name\n        self.speciality=speciality\n\n# Edge\nclass Edge():\n    def __init__(self,edge_type_name):\n        self.edge_type_name=edge_type_name\n\nclass like(Edge):\n    def __init__(self,src_vid,dst_vid,likeness:int):\n        self.src_vid=src_vid\n        self.dst_vid=dst_vid\n        self.likeness=likeness\n\nclass serve(Edge):\n    def __init__(self,src_vid,dst_vid,start_year:int,end_year:int):\n        self.src_vid=src_vid\n        self.dst_vid=dst_vid\n        self.start_year=start_year\n        self.end_year = end_year\n\nclass teammate(Edge):\n    def __init__(self,src_vid,dst_vid,start_year:int,end_year:int):\n        self.src_vid=src_vid\n        self.dst_vid=dst_vid\n        self.start_year=start_year\n        self.end_year = end_year","class":"nba","result": ["[(\"Boris Diaw\" :player{age: 36, name: \"Boris Diaw\"})]"]}

    # Database underlying conversion files
    node_csv = pd.read_csv(NODE_CSV_PATH,index_col=False)
    embedding_list=node_csv['embedding'].tolist()
    new_emb_list=[deal_embedding(i) for i in embedding_list]


    # Save to Fassi
    faiss=FAISS(new_emb_list,node_csv)
    faiss.add_all()
    related_embedding=faiss.search(dict['prompt'])
    related_char=faiss.search_with_char(dict['prompt'])

    with open('dataset/skeleton.txt', encoding='UTF-8') as f:
        skeleton=f.read()


    # Recall relevant information, execute reranker and rewriter
    smaller=SMALLER_LLM()
    source_text = "[task]:Please generate the corresponding three-step inference based on the following query, schema and skeleton.\n"
    source_text += '[query]:' + dict['prompt'] + '\n'
    source_text += '[schema]:\n' + dict['schema'] + "\n"
    source_text += '[skeleton]:\n' + skeleton + "\n"
    source_text += '[output]:'

    middle=smaller.chat(dict['prompt'])
    schema_new,skeleton_new= deal_schema_skeleton(middle,dict['schema'],skeleton)


    # Use the result as a prompt to call the refiner
    prompt = """Generate nGQL corresponding to NebulaGraph based on input and schema.Generate only one corresponding nGQL sentence without providing any explanation.
                               [schema]:""" + schema_new + \
             "\n[skeleton]:" + skeleton_new + \
            "\n[related_item]:\n" + str(related_embedding[0])+"\n" +str(related_char)+ \
             "\n[note]:If the key information in the input is in Chinese, such as various entity names, please keep Chinese\n" + "[note]:At the same time, pay attention to the difference between ngql and cypher. When viewing attributes, there is a strong schema and it is necessary to specify the type of point or edge, such as v.player.born rather than v.born\n" + "[output_format]:ngql:\n" + "[input]:" + \
             dict['prompt'] + "\n[output]:"
    llm=OPENAI()
    gpt_gql=llm.completion([{"role": "user", "content": prompt}])
    print(gpt_gql)

    # After generating gql, query the database and calculate metrics
    db_output=execute_db(dict,gpt_gql)
    evaluation(db_output,dict['result'],gpt_gql,dict['content'])
