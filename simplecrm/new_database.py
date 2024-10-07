import json
from helpers.graph import get_graphConnection
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

def create(graph_entities, entity):
    graph_path = r"simplecrm/Neo4j-363ace08-Created-2024-08-05.txt"
    
    try:
        # Establish the connection to the Neo4j database
        driver = get_graphConnection(graph_path)
        if not driver:
            raise RuntimeError("Failed to connect to the Neo4j database. Check your environment variables and connection settings.")
        
        with driver.session() as session:
            try:
                with session.begin_transaction() as tx:
                    for command in graph_entities:
                        try:
                            tx.run(command)
                            print(f"{entity} created successfully!")
                        except Exception as e:
                            print(f"Failed to execute command: {command}\nError: {e}")
                           
            except Exception as e:
                print(f"Failed to begin or commit the transaction.\nError: {e}")
                # Optional: Rollback or handle transaction-specific errors
                
    except RuntimeError as e:
        print(f"RuntimeError: {e}")
        # Optional: Log or handle connection issues as needed
    except Exception as e:
        print(f"An unexpected error occurred at create: {e}")
        # Optional: Log or handle unexpected errors

    finally:
        # Ensure driver is closed properly
        if driver:
            driver.close()

@csrf_exempt
def process_nodes(request):
    with open('nodes_list.json', 'r') as file:
        nodes = json.load(file)

    create(nodes, "node")
    return JsonResponse({"message" : "done"} , status = 200)
    # print("NODES RCVD: " ,nodes)
    # with open('connections_list.json', 'r') as file:
    #     edges = json.load(file)
    # create(edges, "edge")

