# $R^3$-NL2GQL

<p align="center">
📍Looking our article at <a href="https://arxiv.org/abs/2311.01862">$R^3$-NL2GQL</a> 
</p>

![image](https://github.com/zhiqix/NL2GQL/blob/main/image/fig1.png)

## Basic Introduction

To address the recent challenges of integrating knowledge graphs with LLMs, we propose an approach based on graph database query language. In previous Knowledge Base Question Answering (KBQA) projects, most of them relied on fixed templates and slot-filling techniques to generate Graph Query Language (GQL). Meanwhile, Natural Language to Structured Query Language (NL2SQL) tasks have achieved high accuracy, but their methods cannot be directly applied to NL2GQL tasks. Leveraging the capabilities of LLMs, we introduce the $R^3$-NL2GQL method, which combines both large and small models to tackle NL2GQL tasks. We also present a new dataset to evaluate its effectiveness.

The process can be referred to in the paper. In simple terms, it involves using a fine-tuned smaller white-box Foundation Model as a reranker, which can identify the required CRUD functions, clauses, and patterns from the input. Another smaller white-box Foundation Model acts as a rewriter, aligning the query with the internal database key-value storage to mitigate ambiguities. Finally, a larger black-box Foundation Model is used for its generalization and generation capabilities to produce more accurate GQL.

![image](https://github.com/zhiqix/NL2GQL/blob/main/image/fig4.png)

## File Introduction
[]

## Data Introduction
The data construction process involves matching data from different Knowledge Graphs to the NebulaGraph format, as well as generating training and testing data. This process can be code-intensive, and making substantial code modifications is necessary when dealing with different datasets. The data generation pipeline is represented in the following diagram:

![image](https://github.com/zhiqix/NL2GQL/blob/main/image/fig7.png)

In this pipeline, you would typically have various steps, such as data extraction, transformation, and loading (ETL) to convert data from different Knowledge Graphs into the NebulaGraph format. Then, you would proceed with the data generation for training and testing. This may involve further steps like data augmentation, splitting data into training and testing sets, and possibly other data preprocessing tasks.

### training data
Each JSON in the train data contains 4 pieces of information: prompt represents a natural language query, content represents a standard nGQL , reason represents the inference part that needs to be output by the reranker, and schema represents the code structure schema corresponding to this sentence.

```json

{
	"prompt": "Hello, please help me find the entities and relationships related to 'Tim Duncan' at a distance of 2 to 3.",
	"content": "MATCH (n)-[e:serve|like*2..3]->(v)\nWHERE id(n) == \"Tim Duncan\"\nRETURN e, v",
	"reason": "#the request CRUD function : ['QUERY()']\n#the request clauses : ['WHERE()']\n#the request class : ['like()', 'serve()']\n",
	"schema": "# this is the schema of this graph\n# Nodes\nclass Tag():\n    def __init__(self,tag_name):\n        self.tag_name=tag_name\n\nclass player(Tag):\n    def __init__(self,vid,name:str,age:int):\n        self.vid=vid\n        self.name=name\n        self.age=age\n\nclass team(Tag):\n    def __init__(self,vid,name:str):\n        self.vid=vid\n        self.name=name\n\nclass bachelor(Tag):\n    def __init__(self,vid,name:str,speciality:str):\n        self.vid=vid\n        self.name=name\n        self.speciality=speciality\n\n# Edge\nclass Edge():\n    def __init__(self,edge_type_name):\n        self.edge_type_name=edge_type_name\n\nclass like(Edge):\n    def __init__(self,src_vid,dst_vid,likeness:int):\n        self.src_vid=src_vid\n        self.dst_vid=dst_vid\n        self.likeness=likeness\n\nclass serve(Edge):\n    def __init__(self,src_vid,dst_vid,start_year:int,end_year:int):\n        self.src_vid=src_vid\n        self.dst_vid=dst_vid\n        self.start_year=start_year\n        self.end_year = end_year\n\nclass teammate(Edge):\n    def __init__(self,src_vid,dst_vid,start_year:int,end_year:int):\n        self.src_vid=src_vid\n        self.dst_vid=dst_vid\n        self.start_year=start_year\n        self.end_year = end_year"
}

```
### testing data
Each JSON in the test data contains 6 pieces of information, prompt represents natural language query, content represents gold nGQL , text_schema is used for the vanilla experiment, schema represents the code structure schema corresponding to this sentence, class represents which graph database space this sentence corresponds to, and result represents the results obtained using gold nGQL.

```json

{
	"prompt": " 请问您能帮我找出年龄大于等于29.5岁的球员吗？我需要他们的ID和年龄信息。",
	"content": "LOOKUP ON player WHERE player.age >= 29.5 YIELD id(vertex) as name, player.age AS Age",
	"text_schema": "the node type:[{'player':[name,age],'team':[name],'bachelor':[name,speciality]}],the edge type:[{'like':[likeness],'serve':[start_year,end_year],'teammate':[start_year]}]",
	"schema": "# this is the schema of this graph\n# Nodes\nclass Tag():\n    def __init__(self,tag_name):\n        self.tag_name=tag_name\n\nclass player(Tag):\n    def __init__(self,vid,name:str,age:int):\n        self.vid=vid\n        self.name=name\n        self.age=age\n\nclass team(Tag):\n    def __init__(self,vid,name:str):\n        self.vid=vid\n        self.name=name\n\nclass bachelor(Tag):\n    def __init__(self,vid,name:str,speciality:str):\n        self.vid=vid\n        self.name=name\n        self.speciality=speciality\n\n# Edge\nclass Edge():\n    def __init__(self,edge_type_name):\n        self.edge_type_name=edge_type_name\n\nclass like(Edge):\n    def __init__(self,src_vid,dst_vid,likeness:int):\n        self.src_vid=src_vid\n        self.dst_vid=dst_vid\n        self.likeness=likeness\n\nclass serve(Edge):\n    def __init__(self,src_vid,dst_vid,start_year:int,end_year:int):\n        self.src_vid=src_vid\n        self.dst_vid=dst_vid\n        self.start_year=start_year\n        self.end_year = end_year\n\nclass teammate(Edge):\n    def __init__(self,src_vid,dst_vid,start_year:int,end_year:int):\n        self.src_vid=src_vid\n        self.dst_vid=dst_vid\n        self.start_year=start_year\n        self.end_year = end_year",
	"class": "nba",
	"result": ["[\"Dirk Nowitzki\", 40]", "[\"Kevin Durant\", 30]", "[\"Tracy McGrady\", 39]", "[\"Russell Westbrook\", 30]", "[\"Stephen Curry\", 31]", "[\"LaMarcus Aldridge\", 33]", "[\"Carmelo Anthony\", 34]", "[\"Tiago Splitter\", 34]", "[\"Tim Duncan\", 42]", "[\"Ray Allen\", 43]", "[\"LeBron James\", 34]", "[\"Amar'e Stoudemire\", 36]", "[\"Tony Parker\", 36]", "[\"David West\", 38]", "[\"Paul Gasol\", 38]", "[\"Vince Carter\", 42]", "[\"Jason Kidd\", 45]", "[\"Danny Green\", 31]", "[\"Rajon Rondo\", 33]", "[\"Marc Gasol\", 34]", "[\"Manu Ginobili\", 41]", "[\"Grant Hill\", 46]", "[\"Blake Griffin\", 30]", "[\"Chris Paul\", 33]", "[\"Kobe Bryant\", 40]", "[\"Shaquille O'Neal\", 47]", "[\"DeAndre Jordan\", 30]", "[\"JaVale McGee\", 31]", "[\"Aron Baynes\", 32]", "[\"Dwight Howard\", 33]", "[\"Boris Diaw\", 36]", "[\"Dwyane Wade\", 37]", "[\"Steve Nash\", 45]", "[\"Rudy Gay\", 32]", "[\"Marco Belinelli\", 32]", "[\"Yao Ming\", 38]"]
}

```



## Citation
If you are using $R^3$-NL2GQL for your work, please cite our paper with:

@misc{zhou2023r3nl2gql,
      title={$R^3$-NL2GQL: A Hybrid Models Approach for for Accuracy Enhancing and Hallucinations Mitigation}, 
      author={Yuhang Zhou and Yu He and Siyu Tian and Dan Chen and Liuzhi Zhou and Xinlin Yu and Chuanjun Ji and Sen Liu and Guangnan Ye and Hongfeng Chai},
      year={2023},
      eprint={2311.01862},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
