# NL2GQL

## :spiral_notepad: 开源清单

### 模型

- [**NL2GQLv0.1**]基于从官方示例中抽取的数据，构造出7000条未经筛选的数据进行训练，共四个模型：NL2GQL_MOSS_v0.1、NL2GQL_ChatGLM_v0.1、NL2GQL_BLOOM_v0.1、NL2GQL_Flant5_v0.1，将会逐步开源。
- [**NL2GQLv0.2**]基于从官方示例中抽取的数据，添加部分以检索作In-context Learning的数据进行训练，共1w2条。共四个模型：NL2GQL_MOSS_v0.2、NL2GQL_ChatGLM_v0.2、NL2GQL_BLOOM_v0.2、NL2GQL_Flant5_v0.2，将会逐步开源。
- [**NL2GQLv1.0**]基于从官方说明文档中抽取的800条数据，经过人工筛选及数据生成后，共3k余条数据进行训练。利用LLM的code生成能力，结合上In-context Learning以及Chain of Thought思路对ChatGLM2以及浦语-7B模型进行微调，已开源NL2GQL_ChatGLM2_v1.0，近期将开源NL2GQL_Puyu_v1.0。
- [**NL2GQLv1.1**]基于从官方说明文档中抽取的4k条数据，经过人工筛选及数据生成后，共1w6条数据进行训练，并保证训练数据schema的多样性，训练完成后模型及数据一并开源。
- [**NL2GQLv1.2**]基于NL2GQLv1.1搭建ChatGraph，并在此基础上叠加上人类及数据库反馈数据进行训练。

### 数据

- [**ngql_pdf_v1.jsonl**]基于从官方说明文档中抽取的800条数据，经GPT-3.5生成1k6条数据，已开源。
- [**ngql_pdf_v2.jsonl**]基于从官方说明文档中抽取的800条数据，经过人工筛选及数据生成后，共3k余条数据,已开源。
- [**ngql_pdf_v3.jsonl**]在ngql_pdf_v2数据的基础上补充Chain of Thought推理数据，已开源。
- [**ngql_pdf_v4.jsonl**]共1w6条训练数据，将在近期开源。

## :spiral_notepad: 开源计划

- 2023.7.15 开源NL2GQL_ChatGLM2_v1.1。
- 2023.7.20 利用Langchain以及LLaMA_Index搭建pipeline，开源ChatGraph项目初步结果。
- 2023.7.25 开源NL2GQL_Puyu_v1.0及NL2GQL_Puyu_v1.1。

## :fountain_pen: 介绍

NL2GQL（Natrual Language to Graph Query Language）是一组利用大模型的代码生成能力将自然语言转化为图数据库查询语言的模型，不同于Text2SQL问题，GQL语言分为多种（nGQL、Cypher、Germlin等），公开数据集极少，且更重视图数据的表达，生成任务较为困难。本项目尝试利用此方案解决知识图谱作为本地知识库的检索问题，后续将结合ChatGraph项目，将检索出的子图信息进行prompt生成，将动态知识图谱与大模型进行结合。

**局限性**：
①由于模型参数量较小、训练数据较少和且任务难度较大，目前版本在训练数据的schema上表现较好，当更换schema后，泛化能力较弱。后续版本将增大训练数据schema的多样性提升泛化能力及复杂GQL生成能力。
②目前版本仅实现nGQL语句生成任务，但此方法同样适用于其余GQL，可进行拓展试验。

**注**：
①本系列模型使用2 x A800-80G进行训练
②目前开源版本中，Lora_rank=8的效果好于Lora_rank=16

**NL2GQL用例**：

<details><summary><b>查询实体</b></summary>

![image](https://github.com/zhiqix/NL2GQL/blob/main/image/image1.png)

</details>

<details><summary><b>查询关系</b></summary>

![image](https://github.com/zhiqix/NL2GQL/blob/main/image/image2.png)

</details>

<details><summary><b>添加限制</b></summary>

![image](https://github.com/zhiqix/NL2GQL/blob/main/image/image3.png)

<details><summary><b>创建关系</b></summary>

![image](https://github.com/zhiqix/NL2GQL/blob/main/image/image4.png)

</details>

## :page_with_curl: 训练数据构造说明

本项目创建数据的过程如下图所示，目前仅开源微调数据。对Nebula Graph官方示例以及说明文档进行nGQL抽取，并利用GPT-3.5翻译成对应的中文自然文本（此任务相较于将自然文本翻译为nGQL更为简单,但GPT效果并不好），并为模拟人类对话语言、保证自然文本，提高temperature进行两次数据生成，将数据量翻倍。在此基础上进行长时间的人工筛选及语言重新组织工作，并利用GPT对一些人工整理后的文本再次进行翻倍，生成更礼貌更口语的提问形式，如“查找节点a”-->“您好，我想要查找节点a，您能帮我返回它的信息吗？”，得到v2版本数据。此后根据人类思考方式将数据添加上COT数据，即面对这个问题需要考虑的三点问题：①这个是CRUD问题还是一些其他问题（对大方向进行判断）；②需要用到哪些子句进行限制（如LIMIT、WHERE等）；③对所需要的节点及边类型进行判断。
![image](https://github.com/zhiqix/NL2GQL/blob/main/image/data_build.png)
最后，在训练数据中插入对应的schema，如果是一些图空间或是点边类型的操作，则添加最简单的schema；如果是CRUD操作，则添加上图结构。schema主要分为两个部分，第一部分利用面向对象的class类进行图模式的表达，第二部分对CRUD方法及子句方法进行代码表征，并在其中放入nGQL的表达范式以及一些例子做In-context Learning，如下二图所示。
![image](https://github.com/zhiqix/NL2GQL/blob/main/image/schema1.png)
![image](https://github.com/zhiqix/NL2GQL/blob/main/image/schema2.png)

## :page_with_curl: 开源协议

本项目开源协议依照基座模型的开源协议

## :people: 小组成员

Yuhang Zhou、Yu He、Siyu Tian、Dan Chen from FDU

## :heart: 致谢

- [VESOFT](https://github.com/vesoft-inc): 数据支持
- [ChatGLM2](https://github.com/THUDM/ChatGLM2-6B): 基座模型
- [MOSS](https://github.com/OpenLMLab/MOSS): 基座模型
- [Financial Technology Research Institute,Fudan University](https://cs.fudan.edu.cn/): 算力支持

## 写在最后

本项目于五月底与悦数科技公司讨论产生思路，一开始小组低估了项目难度，认为此种类似于text2sql的任务较为简单，通过少量数据进行简单微调后即可完成。
六月初由于期末学业繁重，项目进度缓慢，爬取了大概三千条ngql语句后，利用gpt-3.5进行ngql2text的任务，将ngql语句翻译为中文语句（并为了保证生成语句的多样性，对同一句ngql进行多次生成任务，但生成的多样性效果并不好），利用中文的点、边、三元组来表示schema，之后就利用pair（自然语言，ngql）数据对MOSS、ChatGLM、BLOOM、Flan-T5模型进行微调，得到了v0.1版本的模型。第四种模型在微调完均能够生成语法看似正确，但细节差距较大的ngql语句。
于是便开始了v0.2版本的训练，v0.1的版本由于训练数据完全由pair对构成，微调后丧失了in-context生成的能力。于是构造数据，将v0.1的训练数据当做知识库，利用embedding相似性去寻找与当前自然语言最相似的例子，在训练数据中扩充了一部分具有example的数据，但最后的效果也不尽人意。当时已产生v0.3的思路，但并没有继续训练。(v0系列pipeline如下图所示)
![image](https://github.com/zhiqix/NL2GQL/blob/main/image/v0_pipeline.png)
六月中旬，受到代码生成任务启发，想到使用代码生成的范式来做此项任务。一方面每次向大家介绍知识图谱时，都会把schema比做面向对象中的class；另一方面MOSS的基座模型是Codegen，代码理解能力理应高于中文理解能力的。于是便利用code来表示schema以及ngql的范式，并在code中加入example来做in-context learning。但schema数据经常能达到4k的token，复杂的甚至能达到6k token，所以需要加入推理来进行schema的拆解，即第一步只生成三步推理，第二步再获取推理中展示的部分schema，减小上下文长度，将schema数据缩小到1k内。
六月底，清华发布ChatGLM2，将上下文长度增长到32k，并能够很好的处理8k内的输入，选择此模型进行微调。对之前的训练数据进行人工校验筛选（大概花费70h的时间），利用精简的3k条数据（由800条原始数据生成）训练出了v1.0版本，能够完美解决与训练数据相同schema的绝大部分问题，并在更改schema后具有一些泛化能力，于是希望其能在参杂极少量新数据后，提高泛化能力，便得到了v1.1版本。后续会使用更大量的数据进行训练，尝试增强能力，并在此基础上融入数据库及人类反馈的方法。
我们希望的目标不是训练出一个权重供大家使用，而是每个场景都可以结合这些开源的数据，通过标注极少的特定ngql数据，达到对自身项目的适配，让每个图空间都拥有一个很小的lora权重，完成对图数据库的操作，以便知识图谱能够更好地结合进大模型中。
