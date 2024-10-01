from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import pdfplumber,io,os, json
from openai import OpenAI


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@csrf_exempt
def test(request):
    if request.method == 'POST':
        try:
            print("rcvd reeq: " , request)
            files = request.FILES

            if not files:
                data = json.loads(request.body)
                image_buffer = data.get('image_buffer')
                print("rcvd image bufer: ", image_buffer)
                content = [
                    {
                        'type': "text",
                        'text': "identify the destination from the following image"
                    },
                    {
                        'type': 'image_url',
                        'image_url': {
                            'url': f"data:image/webp;base64,{image_buffer}"
                        }
                    }
                ]

            else:
                pdf_file = request.FILES.get('pdf')

                if not pdf_file:
                    return JsonResponse({"error": "No PDF file received."}, status=400)

                pdf_stream = io.BytesIO(pdf_file.read())

                extracted_text = ''
                with pdfplumber.open(pdf_stream) as pdf:
                    for page in pdf.pages:
                        extracted_text += page.extract_text()
                
                content = [
                    {
                        'type': "text",
                        'text': "identiy the amount of sales from the following text"
                    },
                    {
                        'type': 'text',
                        'text': extracted_text
                    }
                ]
            print("CONTENT: ", content)
            payload = {
                'model': "gpt-4o-mini",
                'messages': [
                    {
                        'role': "user",
                        'content': content
                    }
                ]
            }
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages= payload['messages']
            )

            if response.choices:
                answer = response.choices[0].message.content
            else:
                return JsonResponse({"error": "No response from the model."}, status=500)

            return JsonResponse({"success": answer})


        except Exception as e:
            print(e)
            return JsonResponse({"error": "Error processing the PDF file."}, status=500)

    return JsonResponse({"error": "Invalid request method. Use POST."}, status=405)