from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Document
from .services.document_parser import extract_text_from_docx
from .services.vector_store import add_document_to_store, remove_document_from_store
import logging


logger = logging.getLogger(__name__)

@receiver(post_save, sender=Document)
def process_new_document(sender, instance, created, **kwargs):
    if not created:
        remove_document_from_store(instance.id)

    file_path = instance.file.path if instance.file else None
    if file_path and file_path.endswith('.docx'):
        extracted_text = extract_text_from_docx(file_path)
        
        Document.objects.filter(id=instance.id).update(full_text=extracted_text)
        
        add_document_to_store(extracted_text, metadata={"doc_id": instance.id, "title": instance.title})



@receiver(post_delete, sender=Document)
def clean_up_deleted_document(sender, instance, **kwargs):
    try:
        remove_document_from_store(instance.id)
        logger.info(f"Successfully removed vectors for deleted document ID: {instance.id}")
        
    except Exception as e:
        logger.error(f"Failed to delete vectors for document {instance.id}: {str(e)}")