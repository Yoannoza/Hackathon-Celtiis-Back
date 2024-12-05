from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Jury, Project, Vote

class JurySerializer(serializers.ModelSerializer):
    class Meta:
        model = Jury
        fields = ['id', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'team', 'name', 'description']

class VoteSerializer(serializers.ModelSerializer):
    total_score = serializers.ReadOnlyField()  # Champ calculé, lecture seule

    class Meta:
        model = Vote
        fields = [
            'id', 
            'jury', 
            'project', 
            'fonctionnalite', 
            'outils_specifiques', 
            'ux_ui', 
            'originalite', 
            'faisabilite_technique', 
            'potentiel_impact', 
            'presentation', 
            'total_score'
        ]
        read_only_fields = ['jury']  # Champ jury sera automatiquement renseigné
        