from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import requests, json, psycopg2
from dynamic_entities.views import create_dynamic_model
from django.db import DatabaseError
from helpers.tables import get_db_connection
from dynamic_entities.views import DynamicModelListView
from rest_framework.test import APIRequestFactory



def convert_flow(flow):
    fields = []
    try:
        print("Received flow: ", flow)
        node_blocks = flow['nodes']
        edges = flow['edges']

        nodes = []
        adjList = []
        id = 0
        for node_block in node_blocks:
            if node_block['type'] == "start":
                print("TEST")
                continue;
            if node_block['type'] == 'askQuestion':
                print("QUESTION")
                data = node_block['data']
                node = {
                    "oldIndex": node_block["id"],
                    "id": id,
                    "body": data['question']
                }
                delay = data.get('delay')
                if delay:
                    node['delay'] = delay
                if data['variable'] and data['dataType']: 
                    fields.append({
                        'field_name': data['variable'],
                        'field_type': data['dataType']
                    })
                    node['variable'] = data['variable']
                    node['variableType'] = data['variable']

                if data['optionType'] == 'Buttons':
                    node["type"] = "Button"
                    if data.get('med_id'):
                        node["mediaID"] = data['med_id']
                    nodes.append(node)
                    list_id = id
                    id += 1
                    adjList.append([])
                    for option in data['options']:
                        node = {
                            "id": id,
                            "body": option,
                            "type": "button_element"
                        }
                        nodes.append(node)
                        adjList.append([])
                        adjList[list_id].append(id)
                        id += 1
                elif data['optionType'] == 'Text':
                    
                    node["type"] = "Text"
                    nodes.append(node)
                    adjList.append([])
                    id += 1

                elif data['optionType'] == 'Lists':
                    node["type"] = "List"
                    nodes.append(node)
                    list_id = id
                    id += 1
                    adjList.append([])
                    for option in data['options']:
                        node = {
                            "id": id,
                            "body": option,
                            "type": "list_element"
                        }
                        nodes.append(node)
                        adjList.append([])
                        adjList[list_id].append(id)
                        id += 1

            elif node_block['type'] == 'sendMessage':
                print("MESSAGE")
                data = node_block['data']
                node = {
                    "oldIndex": node_block["id"],
                    "id": id,
                }
                delay = data.get('delay')
                if delay:
                    node['delay'] = delay
                content = data['fields']['content']
                type = data["fields"]['type']
                if type == "text":
                    node["type"] = "string"
                    node["body"] = content['text']
                elif type == "Image":
                    node["body"] = {"caption" :content["caption"], "id" : content["med_id"]} #"forget menu, would you like to eat this cute chameleon? its very tasty. trust me. you will forget other menu items once you taste our chamaleon delicacy." 
                    node["type"] = "image"
                    # node["body"]["id"] content["med_id"] #"https://letsenhance.io/static/8f5e523ee6b2479e26ecc91b9c25261e/1015f/MainAfter.jpg" #
                    # node["body"]["url"] = content["url"]
                elif type == "Location":
                    node["type"] = "location"
                    node["body"] = {
                        "latitude": content["latitude"],
                        "longitude": content["longitude"],
                        "name": content["loc_name"],
                        "address": content["address"]
                    }
                elif type == "Audio":
                    node["type"] = "audio"
                    node["body"] = {"audioID" : content["audioID"]}

                elif type == "Video":
                    node["type"] = "video"
                    node["body"] = {"videoID" : content["videoID"]}
                
                nodes.append(node)
                adjList.append([])
                id += 1

            elif node_block['type'] == 'setCondition':
                print("CONDITION")
                data = node_block['data']
                node = {
                    "oldIndex": node_block["id"],
                    "id": id,
                    "body": data['condition'],
                    "type": "Button"
                }
                delay = data.get('delay')
                if delay:
                    node['delay'] = delay
                nodes.append(node)
                adjList.append([])
                list_id = id
                id += 1
                node = {
                    "id": id,
                    "body": "Yes",
                    "type": "button_element"
                }
                nodes.append(node)
                adjList.append([])
                adjList[list_id].append(id)
                id += 1
                node = {
                    "id": id,
                    "body": "No",
                    "type": "button_element"
                }
                nodes.append(node)
                adjList.append([])
                adjList[list_id].append(id)
                id += 1

            elif node_block['type'] == 'ai':
                print("AI Mode")
                data = node_block['data']
                node = {
                    "oldIndex": node_block["id"],
                    "id": id,
                    "type": "AI",
                    "body": data['label']
                }
                delay = data.get('delay')
                if delay:
                    node['delay'] = delay
                nodes.append(node)
                adjList.append([])
                id += 1

        print("NODES: ", nodes)
        startNode = None
        for edge in edges:
            if edge['source'] == "start":
                startNodeIndex = int(edge['target'])
                print("start node index: ", startNodeIndex)
                for node in nodes:
                    if 'oldIndex' in node:
                        if int(node['oldIndex']) == startNodeIndex:
                            startNode = int(node['id'])
                print("updated start node: ", startNode)
            else:
                source = int(edge['source'])
                target = int(edge['target'])
                suffix = 0
                sourcehandle = edge['sourceHandle']
                if sourcehandle not in [None, "text"]:
                    if sourcehandle == "true":
                        suffix += 1
                    elif sourcehandle == "false":
                        suffix += 2
                    else:
                        suffix += int(sourcehandle[-1]) + 1
                
                for node in nodes:
                    if 'oldIndex' in node:
                        if int(node['oldIndex']) == source:
                            print("source")
                            n_source = int(node['id']) + suffix
                        if int(node['oldIndex']) == target:
                            print("target")
                            n_target = int(node['id'])
                print(f"source: {n_source}, target: {n_target}")
                adjList[n_source].append(n_target)
                

        for node in nodes:
            node.pop('oldIndex', None)
        print(f"fields: {fields}, start: {startNode}")
        return nodes, adjList, startNode, fields

    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None

@csrf_exempt
def saveFlow(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
            flow_data = data.get('node_data')
            phone_number = data.get('phoneNumber', '917906511071')
            print("Request body:", request.body)

            if flow_data is None:
                return HttpResponseBadRequest('Flow data is missing')
            

            # Optional: Uncomment this block to fetch the contact directly via Django ORM
            # try:
            #     contact = Contact.objects.get(phone=phone_number)
            #     print("CONTACTS: ", contact)
            # except Contact.DoesNotExist:
            #     error_message = f"No contact found with phone number: {phone_number}"
            #     print("Error:", error_message)
            #     return JsonResponse({'error': error_message}, status=404)

            # Convert the flow data into nodes and adjacency list

            nodes, adjList, start, dynamicModelFields = convert_flow(flow_data)
            currNode = 0
            ai_mode = False
            print("Flow converted")
            print("Adjacency list:", adjList)
            print("Nodes:", nodes)
            print("Start: ", start)

            nodes_json = json.dumps(nodes)
            adjList_json = json.dumps(adjList)

            connection = get_db_connection()
            # Fetch the contact ID from the database using the phone number
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id FROM contacts_contact WHERE phone = %s;
                """, (phone_number,))
                contact_row = cursor.fetchone()

            if contact_row:
                contact_id = contact_row[0]
                print("Contact ID found:", contact_id)
                insert_query = """
                    INSERT INTO node_temps_flow (nodes, adj_list, contact_id, curr_node, ai_mode, start_node)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id;
                """
                with connection.cursor() as cursor:
                    cursor.execute(insert_query, (nodes_json, adjList_json, contact_id, currNode, ai_mode, start))
                    flow_id = cursor.fetchone()[0]
                    print("Data inserted successfully with Flow ID:", flow_id)
                    connection.commit()
            else:
                print("No contact found")
                return JsonResponse({'error': 'No contact found for the provided phone number'}, status=404)
            dynamicModelFields.append({
                            'field_name': 'phone_no',
                            'field_type': 'bigint'
                        })
            dynamicModelPayload = {
                'model_name': 'ModelName',
                'fields': dynamicModelFields
            }
            #get flow name from frontend, set model name to tenantID_flowName
            url = 'backenreal-hgg2d7a0d9fzctgj.eastus-01.azurewebsites.net/create-dynamic-model/'
            headers = {
                'Content-Type': 'application/json',
                'X-Tenant-Id': 'll'
            }
            response = requests.post(url, json=dynamicModelPayload, headers=headers)
            if response.status_code == 201:
                print("dynamic model created succesfully")
            else:
                print("Error occurred while creating the dynamic model")
                print(f"Status Code: {response.status_code}")
                print(f"Response: {response.json()}")

            print("Flow saved successfully")
            return JsonResponse({'message': "Flow saved successfully"})

        except json.JSONDecodeError as json_err:
            print("JSONDecodeError:", json_err)
            return HttpResponseBadRequest('Invalid JSON data')
        except Exception as e:
            print("Exception:", str(e))
            return JsonResponse({'error': str(e)}, status=500)
    else:
        print("Invalid request method:", request.method)
        return HttpResponseBadRequest('ONLY POST REQUEST ALLOWED')

@csrf_exempt
def get_flow(request):
    try:
        print("getflow")
        data = json.loads(request.body)
        phoneNumber = str(data.get('phone_number'))

        if not phoneNumber:
            return JsonResponse({'error': 'phone_number is required'}, status=400)
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT ntf.nodes, ntf.adj_list, ntf.curr_node, ntf.ai_mode
                FROM node_temps_flow ntf
                INNER JOIN contacts_contact c ON ntf.contact_id = c.id
                WHERE c.phone = %s;
            """, (phoneNumber,))
            row = cursor.fetchone()

        if row:
            nodes, adj_list, curr_node, ai_mode = row
            return JsonResponse({
                'nodes': nodes,
                'adj_list': adj_list,
                'curr_node': curr_node,
                'ai_mode': ai_mode
            })
        else:
            return JsonResponse({'error': 'No data found for the given phone number'}, status=404)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return JsonResponse({'error': 'An unexpected error occurred'}, status=500)
    finally:
        if connection:
            connection.close()
    
@csrf_exempt
def set_flow(request):
    try:
        data = json.loads(request.body)
        phoneNumber = str(data.get('phone_number'))
        curr_node = data.get('curr_node')
        ai_mode = data.get('ai_mode')
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
            SELECT id FROM contacts_contact WHERE phone = %s;
        """, (phoneNumber,))
        contact_row = cursor.fetchone()

        if contact_row:
            contact_id = contact_row[0]
            print("Contact ID found:", contact_id)

            update_query = """
                UPDATE node_temps_flow
                SET curr_node = %s, ai_mode = %s
                WHERE contact_id = %s
            """
            cursor.execute(update_query, (curr_node, ai_mode, contact_id))
            
            connection.commit()
            print("data updated")
            return JsonResponse({"message": "Data updated successfully"})

        else:
            return JsonResponse({"error": "No contact found"}, status=404)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)

    except Exception as e:
        return JsonResponse({"error": f"An unexpected error occurred at set flow: {str(e)}"}, status=500)

    finally:
        if connection:
            connection.close()

@csrf_exempt
def create_whatsapp_tenant_table(request):
    query = '''
    CREATE TABLE IF NOT EXISTS whatsapp_tenant_data (
        business_phone_number_id VARCHAR(255) PRIMARY KEY,
        flow_data JSONB,
        adj_list JSONB,
        access_token VARCHAR(255),
        created_at TIMESTAMPTZ DEFAULT NOW()
    )
    '''
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute(query)
    
    return JsonResponse({'message': 'Table created successfully'})

@csrf_exempt
def insert_whatsapp_tenant_data(request):
    try:
        # Parse JSON data from the request body
        data = json.loads(request.body.decode('utf-8'))
        print("Received data at insert data: ", data)
        tenant_id = request.headers.get('X-Tenant-Id')
        if not tenant_id:
            return JsonResponse({'status': 'error', 'mesage': 'no tenant id found in headers'}, status = 400)
        business_phone_number_id = data.get('business_phone_number_id')
        access_token = data.get('access_token')
        account_id = data.get('accountID')
        firstInsertFlag = data.get('firstInsert', False)  # flag to mark the insert of bpid, access token, account id
        
        node_data = data.get('node_data', None)
        flow_name = data.get('name')

        connection = get_db_connection()

        if firstInsertFlag:
            try:
                print("First insert")
                if not all([business_phone_number_id, access_token, account_id]):
                    return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)

                query = '''
                INSERT INTO whatsapp_tenant_data (business_phone_number_id, access_token, account_id, tenant_id)
                VALUES (%s, %s, %s, %s)
                '''
                #insert fallback msg and count
                
                cursor = connection.cursor()
                print("Executing query:", query, business_phone_number_id, access_token, account_id, tenant_id)
                cursor.execute(query, [business_phone_number_id, access_token, account_id, tenant_id])
                connection.commit()  # Commit the transaction
                print("Query executed successfully")
                return JsonResponse({'message': 'Data inserted successfully'})
                
            except Exception as e:
                print(f"An error occurred during first insert: {e}")
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

        else:
            if node_data is not None:
                try:
                    
                    print("Node Data: ", node_data)
                    fallback_message = node_data.get('fallback_message'),
                    fallback_count = node_data.get('fallback_count')
                    flow_data, adj_list, start, dynamicModelFields = convert_flow(node_data)
                    
                    dynamicModelFields.append({
                                    'field_name': 'phone_no',
                                    'field_type': 'bigint'
                                })
                    flow_name = DynamicModelListView.sanitize_model_name(model_name=flow_name)
                    print("new flow name: ", flow_name)
                    model_name= flow_name
                    fields= dynamicModelFields
                    print("model name: ", model_name, fields)
                    create_dynamic_model(model_name=model_name, fields=fields)

                    #updating whatsapp_tenant_flow with flow_data and adj_list
                    query = '''
                    UPDATE whatsapp_tenant_data
                    SET flow_data = %s, adj_list = %s, start = %s, fallback_message = %s, fallback_count = %s, flow_name = %s
                    WHERE business_phone_number_id = %s
                    '''
                    print("adj listt: ", adj_list, flow_data, start)
                    with connection.cursor() as cursor:
                        print("Executing query:", query, json.dumps(flow_data), json.dumps(adj_list), start, fallback_message, fallback_count, flow_name ,business_phone_number_id)
                        cursor.execute(query, [json.dumps(flow_data), json.dumps(adj_list), start, fallback_message, fallback_count, flow_name ,business_phone_number_id])
                        connection.commit()  # Commit the transaction
                    print("Query executed successfully")
                    return JsonResponse({'message': 'Data updated successfully'})
                except Exception as e:
                    print(f"An error occurred during update: {e}")
                    return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
            else:
                return JsonResponse({'message': 'No Node Data Present'}, status=400)
        
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"An unexpected error occurred at insert whatsapptenant data: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)    

@csrf_exempt
def get_whatsapp_tenant_data(request):
    try:
        business_phone_number_id = request.GET.get('business_phone_id')
        print("BPNID", business_phone_number_id)
        if not business_phone_number_id:
            return JsonResponse({'error': 'business_phone_id query parameter is required'}, status=400)

        query = '''
        SELECT business_phone_number_id, flow_data, adj_list, access_token, account_id, start, flow_name, fallback_message, fallback_count
        FROM whatsapp_tenant_data
        WHERE business_phone_number_id = %s
        '''
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, [business_phone_number_id])
            row = cursor.fetchone()
        if not row:
            return JsonResponse({'error': 'No data found for the given business_phone_number_id'}, status=404)
        data = {
            'business_phone_number_id': row[0],
            'flow_data': row[1],
            'adj_list': row[2],
            'access_token': row[3],
            'account_id' : row[4],
            'start' : row[5],
            'flow_name' : row[6],
            'fallback_msg': row[7],
            'fallback_count': row[8]
        }
        return JsonResponse(data)

    except DatabaseError as e:
        return JsonResponse({'error': 'Database error occurred', 'details': str(e)}, status=500)

    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred', 'details': str(e)}, status=500)

@csrf_exempt
def update_message_status(request):
    try:
        # Print the raw request body for debugging
        # print("Received request:", request)
        # print("Request body:", request.body.decode('utf-8'))
        
        # Parse JSON data from the request body
        data = json.loads(request.body)
        
        # Extract data from the JSON object
        business_phone_number_id = data.get('business_phone_number_id')
        isFailed = data.get('is_failed')
        isReplied = data.get('is_replied')
        isRead = data.get('is_read')
        isDelivered = data.get('is_delivered')
        isSent = data.get('is_sent')
        phone_number = data.get('user_phone')
        messageID = data.get('message_id')
        broadcastGroup_id = data.get('bg_id')

        
        connection = get_db_connection()
        cursor = connection.cursor()
        if broadcastGroup_id != None:
            query = "UPDATE whatsapp_message_id SET broadcast_group = %s WHERE message_id = %s"
            cursor.execute(query, [broadcastGroup_id, messageID])
            connection.commit()
        else:
            query = """
                INSERT INTO whatsapp_message_id (message_id, business_phone_number_id, sent, delivered, read, replied, failed, user_phone_number, broadcast_group)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (message_id)
                DO UPDATE SET
                    sent = EXCLUDED.sent,
                    delivered = EXCLUDED.delivered,
                    read = EXCLUDED.read,
                    failed = EXCLUDED.failed,
                    replied = EXCLUDED.replied;
            """

            cursor.execute(query, [messageID, business_phone_number_id, isSent, isDelivered, isRead, isReplied, isFailed, phone_number, broadcastGroup_id])
            connection.commit()
            print("updated status for message id: ", messageID)
            print(f"isSent: {isSent}, isDeli: {isDelivered}, isRead: {isRead}, isReplied: {isReplied} ", )

        return JsonResponse({'message': 'Data inserted successfully'})
    except psycopg2.Error as e:
        print("Database error:", e)
        return JsonResponse({'error': str(e)}, status=500)
    except json.JSONDecodeError as e:
        print("JSON decode error:", e)
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    except Exception as e:
        print("Exception:", e)
        return JsonResponse({'error': str(e)}, status=500)
    finally:
        if connection:
            connection.close()

@csrf_exempt
def get_status(request):
    if request.method == 'GET':
        query = """
            SELECT *
            FROM whatsapp_message_id;
        """
        try:
            connection = get_db_connection()
            with connection.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()

            message_statuses = [
                {
                    "business_phone_number_id": row[0],
                    "is_sent": row[1],
                    "is_delivered": row[2],
                    "is_read": row[3],
                    "user_phone_number": row[4],
                    "message_id": row[5],
                    "broadcast_group": row[6],
                    "is_replied": row[7],
                    "is_failed": row[8]
                }
                for row in rows
            ]

            return JsonResponse({"message_statuses": message_statuses})

        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

from contacts.views import ContactByTenantAPIView

@csrf_exempt
def get_bpid(request):
    try:
        tenant = request.headers.get("X-Tenant-Id")
        
        if not tenant:
            return JsonResponse({"error": "X-Tenant-Id header is missing"}, status=400)
        
        query = "SELECT business_phone_number_id, account_id from whatsapp_tenant_data WHERE tenant_id = %s"

        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute(query, [tenant])
        res = cursor.fetchone()  
        
        if res is None:
            return JsonResponse({"error": f"No business phone number found for tenant {tenant}"}, status=404)
        
        return JsonResponse({
            "tenant": tenant,
            "business_phone_number_id": res[0],
            "account_id": res[1]
        })
    except Exception as e:
        print("error: ", e)
        return JsonResponse({"error": "An error occurred while processing the request", "details": str(e)}, status=500)

    finally:
        try:
            connection.close()
        except:
            pass

@csrf_exempt
def get_tenant(request):
    print("rcvd req: ", request.body)
    try:
        if not request.body:
            return JsonResponse({"error": "Empty request body"}, status=400)

        body = json.loads(request.body)

        bpid = body.get('bpid')

        if not bpid:
            return JsonResponse({"error": "Missing 'bpid' parameter"}, status=400)
        print(bpid)
        query = "SELECT tenant_id FROM whatsapp_tenant_data WHERE business_phone_number_id = %s"
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(query, [bpid])
        res = cursor.fetchone()
        print(res)
        if res is None:
            return JsonResponse({"error": f"No tenant found for bpid {bpid}"}, status=404)
        
        return JsonResponse({
            "tenant" : res[0]
        })
    
    except Exception as e:
        print("Error in get_tenant: ", e)
        return JsonResponse({"error": "An error occurred while retrieving tenant", "details": str(e)}, status=500)

    finally:
        try:
            connection.close()
        except Exception as e:
            print("Error closing connection: ", e)