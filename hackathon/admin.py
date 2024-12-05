from django.contrib import admin
from .models import Project, Jury, Vote

# Générer automatiquement tous les champs pour list_display
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Project._meta.fields]  # Affiche tous les champs

@admin.register(Jury)
class JuryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Jury._meta.fields]  # Affiche tous les champs

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Vote._meta.fields]  # Affiche tous les champs
