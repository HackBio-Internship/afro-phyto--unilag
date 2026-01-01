from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Contributor, Plant, Phytochemical, ScientificLiterature, ContactMessage, ContributionAudit

@admin.register(Contributor)
class ContributorAdmin(admin.ModelAdmin):
    list_display = ('accession_number', 'scientific_name', 'user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('accession_number', 'scientific_name', 'common_name', 'user__username')
    readonly_fields = ('accession_number', 'user', 'created_at')
    ordering = ('-created_at',)

@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ('scientific_name', 'common_names', 'status', 'image_preview', 'submitted_at')
    search_fields = ('scientific_name', 'common_names')

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" height="100" />')
        return 'No image'
    image_preview.short_description = 'Image Preview'

@admin.register(Phytochemical)
class PhytochemicalAdmin(admin.ModelAdmin):
    list_display = ('compound_name', 'compound_class', 'plant')
    search_fields = ('compound_name', 'compound_class', 'plant__scientific_name')

@admin.register(ScientificLiterature)
class ScientificLiteratureAdmin(admin.ModelAdmin):
    list_display = ('title', 'journal', 'plant')
    search_fields = ('title', 'authors', 'journal')

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('fname', 'lname', 'email', 'subject', 'created_at')
    search_fields = ('email', 'subject')
    ordering = ('-created_at',)

@admin.register(ContributionAudit)
class ContributionAuditAdmin(admin.ModelAdmin):
    list_display = ("contribution", "action", "reviewer", "timestamp")
    list_filter = ("action", "timestamp")
    search_fields = ("contribution__accession_number", "reviewer__username")
    # ordering = ("-timestamp",)
