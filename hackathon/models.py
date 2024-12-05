from django.db import models
from django.contrib.auth.models import AbstractUser,  Group, Permission, User
from django.utils.crypto import get_random_string


class Jury(User):
    name = models.CharField(max_length=255)
    
    USERNAME_FIELD = 'name'
    
    def save(self, *args, **kwargs):
        # Générer un username unique si non défini
        if not self.username:
            self.username = get_random_string(length=10)  # Génère un identifiant aléatoire
        super().save(*args, **kwargs)
    
    
    def __str__(self):
        return f"Jury {self.name if self.name else 'No Email'}"



class Project(models.Model):
    team = models.CharField(max_length=100)  # Nom de l'équipe
    name = models.CharField(max_length=100)  # Titre du projet
    description = models.TextField()         # Description
    created_at = models.DateTimeField(auto_now_add=True)


class Vote(models.Model):
    jury = models.ForeignKey('Jury', on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    # Critères de notation
    fonctionnalite = models.IntegerField()       # /10
    outils_specifiques = models.IntegerField()   # /10
    ux_ui = models.IntegerField()                # /10
    originalite = models.IntegerField()          # /5
    faisabilite_technique = models.IntegerField() # /5
    potentiel_impact = models.IntegerField()     # /5
    presentation = models.IntegerField()         # /5

    @property
    def total_score(self):
        return (
            self.fonctionnalite +
            self.outils_specifiques +
            self.ux_ui +
            self.originalite +
            self.faisabilite_technique +
            self.potentiel_impact +
            self.presentation
        )

    class Meta:
        unique_together = ('jury', 'project')  # Un seul vote par jury par projet
