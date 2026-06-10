from django.contrib import admin
from .models import Document, QuestionAnswer
from .services.llm_service import generate_answer

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    readonly_fields = ('full_text', 'created_at')
    
    def has_change_permission(self, request, obj=None):
        return True

@admin.register(QuestionAnswer)
class QuestionAnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'created_at', 'short_answer')
    readonly_fields = ('answer', 'created_at')
    fields = ('question', 'answer', 'created_at')

    def short_answer(self, obj):
        return obj.answer[:100] + "..." if obj.answer else ""

    def save_model(self, request, obj, form, change):
        if change:
            orig_obj = QuestionAnswer.objects.get(pk=obj.pk)
            if orig_obj.question != obj.question:
                try:
                    obj.answer = generate_answer(obj.question)
                except Exception as e:
                    obj.answer = f"Error generating answer: {str(e)}"
        else:
            try:
                obj.answer = generate_answer(obj.question)
            except Exception as e:
                obj.answer = f"Error generating answer: {str(e)}"

        super().save_model(request, obj, form, change)
