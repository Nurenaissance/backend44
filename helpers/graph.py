from dotenv import load_dotenv
import os
from neo4j import GraphDatabase


def get_graphConnection(graph):
    try:
        # Retrieve environment variables
        URI = "neo4j+s://363ace08.databases.neo4j.io"
        USERNAME = "neo4j"
        PASSWORD = "pN-boAI3TjfcZD56acBM9THb4_5r5sOGGF7N59VElyg"
        
        if not URI or not USERNAME or not PASSWORD:
            raise ValueError("Missing required environment variables: NEO4J_URI, NEO4J_USERNAME, or NEO4J_PASSWORD.")
        
        # Create a connection to the Neo4j database
        driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))
        
        return driver

    except RuntimeError as e:
        print(f"RuntimeError: {e}")
        return None
    except ValueError as e:
        print(f"ValueError: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred at get graph connection: {e}")
        return None

def get_graph_schema(graph):
    driver = get_graphConnection(graph)
    query = "MATCH(n) MATCH ()-[l]-() RETURN n,l"

    records,summary,keys = driver.execute_query(query, database_="neo4j")
    driver.close()
    nodes={}
    checkset= set()
    relationships=[]
    for record in records:
        for key in keys:
            element = record[key]
            if key =='n':
                label = list(element.labels)[0]
                properties = {k: element[k] for k in element}
                if label not in checkset:
                    checkset.add(label)
                    nodes[label] = properties
            else:
                internal_nodes = element.nodes
                start = list(internal_nodes[0].labels)[0]
                end = list(internal_nodes[1].labels)[0]
                type = element.type
                
                rel = f"(:{start})-[:{type}]->(:{end})"
                if rel not in checkset:
                    relationships.append(rel)
                    checkset.add(rel)
    graph_schema = f"""The nodes are: {nodes}
    The relationships are: {relationships}"""
    return graph_schema

