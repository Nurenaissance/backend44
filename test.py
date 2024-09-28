from django.views.decorators.csrf import csrf_exempt
import fitz, json
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from helpers.vectorize import make_openai_call
from django.http import JsonResponse

@csrf_exempt
def test(request):
    if request.method == 'POST':
        try:
            query = request.POST.get("query")
            query_tags = request.POST.get("query_tags")

            uploaded_file = request.FILES.get('file')
            if not uploaded_file:
                print("No file uploaded.")
                return JsonResponse({'error': 'No file uploaded'}, status=400)
            
            pdf_file = uploaded_file.read()
            full_text = ""

            document = fitz.open(stream=pdf_file, filetype="pdf")
            print(f"Number of pages in PDF: {len(document)}")

            for page_num in range(len(document)):
                page = document.load_page(page_num)
                page_text = page.get_text()
                full_text += page_text
                print(f"Extracted text from page {page_num}: {page_text[:100]}")  # Log a snippet

            if not full_text:
                print("Failed to extract any text from the PDF.")
                return JsonResponse({'error': 'No text extracted from PDF'}, status=400)

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=200,
                chunk_overlap=20,
                length_function=len,
            )
            docs = text_splitter.split_text(full_text)
            print(f"Text split into {len(docs)} chunks.")

            

            doc_objects = [Document(page_content=chunk) for chunk in docs]
            
            embedding = OpenAIEmbeddings()
            print("Embeddings created.")

            library = FAISS.from_documents(doc_objects, embedding)
            print("FAISS library created.")

            answer = library.similarity_search(query_tags)
            print(f"Answer retrieved: {answer}")

            if answer:
                
                combined_query = " ".join([doc.page_content for doc in answer])

                openai_response = make_openai_call(combined_query, query)
                print(openai_response)
                return JsonResponse({"status": 200, "message": openai_response})
            else:
                print("No relevant answers found.")
                return JsonResponse({'answer': 'No relevant answers found.'})

        except Exception as e:
            print(f"An error occurred: {e}")
            return JsonResponse({'error': str(e)}, status=500)
