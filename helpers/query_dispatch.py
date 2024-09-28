from .psy_query import query, get_graph_schema
from .vectorize import query as faiss_query
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json, os
from openai import OpenAI
from .tables import get_tables_schema
from analytics.views import ExecuteQueryView
from .prompts import SYS_PROMPT_QD as SYS_PROMPT
from .vectors_views import HandleQueryView

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

graph_path = ""
graph_schema = get_graph_schema(graph=graph_path)

table_schema = get_tables_schema()

def classify(question):
    client = OpenAI(api_key=OPENAI_API_KEY)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYS_PROMPT},
            {"role": "user", "content": f" Question: {question}"}
        ]
    )
    response = response.choices[0].message.content
    print(response)
    return response

@csrf_exempt
def dispatch(request):
    if request.method == "POST":
        try:
            # Parse the incoming request
            data = json.loads(request.body)
            question = data.get("prompt")

            print("rcvd question = " ,question)
            
            if not question:
                return HttpResponse(
                    "Error: Question is required",
                    status=400
                )
            
            type = classify(question)
            if type == "Table":
                view = ExecuteQueryView.as_view()
                response = view(request)
                result = response.data
                print("table result: " ,result)
            elif type == "Graph":
                result = query(question, graph_path)
                print("graph result: " ,result)
            elif type == "None":
                view = HandleQueryView.as_view()
                response = view(request)
                result = response
                print("vector :",result)
            else:
                result = "Data doesnt belong with us"

            return HttpResponse( result ,status=200)
        except json.JSONDecodeError:
            return HttpResponse(
                "Error: Invalid JSON",
                status=400
            )
        except Exception as e:
            return HttpResponse(
                f"Error: {str(e)}",
                status=500
            )
    else:
        return HttpResponse(
            "Error: Only POST method is allowed",
            status=405
        )
