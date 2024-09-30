from .graph import get_graph_schema
from .tables import get_tables_schema

graph_path = r"simplecrm/Neo4j-a71a08f7-Created-2024-07-25.txt"
graph_schema = get_graph_schema(graph=graph_path)
table_schema = get_tables_schema()


SYS_PROMPT_QD = f"""
Given the Graph Schema : {graph_schema}
And the Table Schema : {table_schema}
Determine the question being asked would be most suitable answered by which document, table, graph or none of these.
Return your response in single word stating 'Graph', 'Table' or 'None'.
DO NOT INCLUDE ANY APOLOGIES OR SUGGESTIONS. JUST RETURN THE NAME OF THE CLASSIFIED CATEGORY.
"""

SYS_PROMPT_1_psyq = """
You will be given a graph schema which tells about the nodes, their properties and possible relationships between them. Understand the schema.
You will also be given a question. based on what is being asked, reformulate the question for the graph.

Instructions: Return the reformed question only. Do not return anything else.

Examples-
#1 what product should be suggested to lead 8?
response:- Return all the products. Return characterestics of lead id 8. Also return if theres any relationship present.
"""


SYS_PROMPT_2_psyq = f"""
Generate Cypher statement to query a graph database.
Instructions:
Do not use any other relationship types or properties that are not provided.

Note: Do not include any explanations or apologies in your responses.
Do not include two return statements.
Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
Do not include any text except the generated Cypher statement.
Do not include node properties.

instead of [:r1|:r2|:r3] format, prefer use of [:r1|r2|r3] format

PROMOTE USE OF OPTIONAL MATCH

return all the nodes and relationships between nodes

#example: MATCH (c:Node1) 
OPTIONAL MATCH (a:Node2)-[f:Relationship1]->(c)
RETURN c, a, f
"""

SYS_PROMPT_3 = f"""
Correct the query for neo4j graph database.
include relationships in return statement.

RETURN ONLY ONE QUERY. NOT ANYTHING ELSE.
Make sure the query is fit to run on neo4j workspace.
The query should contain only one return statement
"""

SYS_PROMPT_ETL = f"""
You are someone who analyzes human characterestics from a piece of conversation and you are very good at your work.
You will be given a conversation between a person and a salesman. Identify the person's psychographic data based on the snippet.
You can group your findings under following labels: 
personality_characterestics, lifestyle, social_class, habits, interests, etc.
You can add your own labels, or remove these if necessary. 

RULES: DO NOT GROUP DATA BASED ON THE INTERNET. THE CONVERSATION PROVIDED TO YOU IS AUTHORATIVE AND ANALYSIS SHOULD BE DONE SOLELY ON THE CONVERSATION ITSELF.
RETURN THE RESPONSE IN A KEY-VALUE PAIR JSON SUITABLE WAY.
KEEP YOUR RESPONSE SHORT, CONCISE AND TO THE POINT.
DONT WRITE ANYTHING ELSE IN THE RESPONSE.
AVOID NESTING
"""
def whatsapp_prompts(required_fields, type):

    PROMPT_FOR_IMAGE = f"""
    identiy the fields: {required_fields} from the following image.
    return the answer in json format. if any of the field is missing, return null in its place

    if you dont know the answer, return an empty json object. dont include any apologies or any other statements in your response

    """

    PROMPT_FOR_DOC = f"""
    identiy the fields: {required_fields} from the following text.
    return the answer in json format. if any of the field is missing, return null in its place

    if you dont know the answer, return an empty json object. dont include any apologies or any other statements in your response

    """

    if type is "image":
        return PROMPT_FOR_IMAGE
    elif type is "doc":
        return PROMPT_FOR_DOC
