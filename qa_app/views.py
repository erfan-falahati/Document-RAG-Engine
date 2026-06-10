import json
import chromadb
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import Document, QuestionAnswer
from .services.llm_service import generate_answer

@csrf_exempt
def api_upload_document(request):
    """API endpoint to upload a .docx file and vectorize it."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)
    
    title = request.POST.get('title')
    uploaded_file = request.FILES.get('file')
    
    if not title or not uploaded_file:
        return JsonResponse({'error': 'Both "title" and "file" fields are required.'}, status=400)
    
    try:
        doc = Document(title=title, file=uploaded_file)
        doc.save()
        
        return JsonResponse({
            'message': 'Document uploaded and vectorized successfully.',
            'document_id': doc.id,
            'title': doc.title
        }, status=201)
    except Exception as e:
        return JsonResponse({'error': f'Failed to process document: {str(e)}'}, status=500)

@csrf_exempt
def api_update_document(request, pk):
    """API to replace an existing document record. The signal handles re-indexing."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)
    
    doc = get_object_or_404(Document, pk=pk)
    
    new_title = request.POST.get('title')
    new_file = request.FILES.get('file')
    
    if not new_title or not new_file:
        return JsonResponse({'error': 'Both "title" and "file" are required.'}, status=400)
    
    try:
        doc.title = new_title
        doc.file = new_file
        doc.save() 
        
        return JsonResponse({
            'message': 'Document updated and re-indexed successfully.',
            'document_id': doc.id
        }, status=200)
    except Exception as e:
        return JsonResponse({'error': f'Update failed: {str(e)}'}, status=500)
    
@csrf_exempt
def api_delete_document(request, pk):
    """API endpoint to delete a document and purge its text vectors from ChromaDB."""
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Only DELETE requests are allowed.'}, status=405)
        
    try:
        doc = get_object_or_404(Document, pk=pk)
        
        chroma_client = chromadb.PersistentClient(path="/app/chroma_db")
        chroma_collection = chroma_client.get_or_create_collection(name="documents_collection")
        chroma_collection.delete(where={"document_id": doc.id})
        
        doc.delete()
        
        return JsonResponse({
            'message': 'Document record and associated vectors successfully deleted.'
        }, status=200)
    except Exception as e:
        return JsonResponse({'error': f'Failed to delete document: {str(e)}'}, status=500)


@csrf_exempt
def api_ask_question(request):
    """API endpoint to submit a prompt, execute RAG context matching, and return answers."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)
    
    try:
        data = json.loads(request.body)
        question_text = data.get('question')
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'error': 'Invalid JSON format payload.'}, status=400)
        
    if not question_text:
        return JsonResponse({'error': 'The "question" property is required.'}, status=400)
        
    try:
        answer_text = generate_answer(question_text)
        
        qa_log = QuestionAnswer.objects.create(question=question_text, answer=answer_text)
        
        return JsonResponse({
            'qa_id': qa_log.id,
            'question': question_text,
            'answer': answer_text
        }, status=200)
    except Exception as e:
        return JsonResponse({'error': f'RAG pipeline execution failed: {str(e)}'}, status=500)


@csrf_exempt
def api_manage_question(request, pk):
    """API endpoint to modify an existing question (re-running RAG) or delete it from history."""
    qa_log = get_object_or_404(QuestionAnswer, pk=pk)
    
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            new_question = data.get('question')
        except (json.JSONDecodeError, TypeError):
            return JsonResponse({'error': 'Invalid JSON format payload.'}, status=400)
            
        if not new_question:
            return JsonResponse({'error': 'The "question" property is required.'}, status=400)
            
        try:
            new_answer = generate_answer(new_question)
            
            qa_log.question = new_question
            qa_log.answer = new_answer
            qa_log.save()
            
            return JsonResponse({
                'qa_id': qa_log.id,
                'message': 'Question updated and pipeline re-executed successfully.',
                'question': qa_log.question,
                'answer': qa_log.answer
            }, status=200)
        except Exception as e:
            return JsonResponse({'error': f'Pipeline re-execution failed: {str(e)}'}, status=500)
            
    elif request.method == 'DELETE':
        try:
            qa_log.delete()
            return JsonResponse({
                'message': 'Question history record permanently removed.'
            }, status=200)
        except Exception as e:
            return JsonResponse({'error': f'Failed to remove record: {str(e)}'}, status=500)
            
    else:
        return JsonResponse({'error': 'Only PUT and DELETE requests are allowed.'}, status=405)