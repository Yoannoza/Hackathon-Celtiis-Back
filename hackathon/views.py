from django.shortcuts import render
# from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from django.contrib.auth import authenticate
from django.db.models import Sum, F, ExpressionWrapper, FloatField, Count, Case, When
from .models import Vote, Project
from .serializers import VoteSerializer, ProjectSerializer

from .models import Jury  # Importer le modèle Jury

class JuryRegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        # Vérification des champs requis
        if not username or not password:
            return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Vérifie si un jury existe déjà avec cet username
        if Jury.objects.filter(name=username).exists():
            return Response({'error': 'A jury member with this username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        # Créer un jury
        jury = Jury.objects.create(name=username)
        jury.set_password(password)  # Définit le mot de passe sécurisé
        jury.save()

        # Générer un token pour ce jury
        # Génération du JWT
        refresh = RefreshToken.for_user(jury)
        access_token = refresh.access_token

        return Response({
            'message': 'Inscription réussie.',
            'access_token': str(access_token),
            'refresh_token': str(refresh),
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request):
        name = request.data.get('username')
        password = request.data.get('password')

        if not name or not password:
            return Response({'error': 'Name and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(name=name, password=password)

        if user is not None:
            # Génération du JWT
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            # Retourner les tokens générés
            return Response({
                'access_token': str(access_token),
                'refresh_token': str(refresh)
            })
        else:
            return Response({'error': 'Invalid name or password.'}, status=status.HTTP_401_UNAUTHORIZED)

class ProjectViewSet(ModelViewSet):
    permission_classes = [AllowAny]  # Permet un accès public
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer



class VoteViewSet(ModelViewSet):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = [IsAuthenticated]  # Seulement les utilisateurs authentifiés peuvent voter

    
    def get_queryset(self):
        jury = self._get_jury_from_token()
        """
        Filtrer les votes pour afficher uniquement ceux du jury connecté.
        """
        return Vote.objects.filter(jury=jury)

    def perform_create(self, serializer):
        user = self.request.user

        # Vérification de l'utilisateur
        if not user.is_authenticated:
            raise ValidationError({"detail": "Vous devez être connecté pour voter."})

        try:
            jury = Jury.objects.get(pk=user.pk)
        except Jury.DoesNotExist:
            raise AuthenticationFailed({"detail": "Seuls les jurys sont autorisés à voter."})

        # Vérifier si le vote existe déjà pour ce projet
        project = serializer.validated_data.get('project')
        if Vote.objects.filter(jury=jury, project=project).exists():
            raise ValidationError({"detail": "Vous avez déjà voté pour ce projet."})

        # Valider les scores
        self.validate_scores(serializer.validated_data)

        # Enregistrer le vote
        serializer.save(jury=jury)
        
        # Retourner une réponse de succès
        return Response({"detail": "Vote enregistré avec succès."}, status=status.HTTP_201_CREATED)
        
        
    def validate_scores(self, data):
        """
        Valider que toutes les notes sont dans les limites autorisées.
        """
        score_limits = {
            'fonctionnalite': 10,
            'outils_specifiques': 10,
            'ux_ui': 10,
            'originalite': 5,
            'faisabilite_technique': 5,
            'potentiel_impact': 5,
            'presentation': 5,
        }
        for field, max_score in score_limits.items():
            if data.get(field, 0) > max_score:
                raise ValidationError({"detail": {field: f"Le score maximum est {max_score}."}})
        

class LeaderboardView(APIView):
    permission_classes = [AllowAny]  # Accessible à tous

    def get(self, request):
        # Nombre total de jurys
        total_jurys = Jury.objects.count()  # Assurez-vous d'avoir un modèle Jury

        projects = Project.objects.annotate(
            total_score=Sum(
                F('vote__fonctionnalite') +
                F('vote__outils_specifiques') +
                F('vote__ux_ui') +
                F('vote__originalite') +
                F('vote__faisabilite_technique') +
                F('vote__potentiel_impact') +
                F('vote__presentation'),
                output_field=FloatField()
            ),
            total_votes=Count('vote'),  # Nombre total de votes reçus
            all_jurys_voted=Case(
                When(total_votes=total_jurys, then=True),  # Tous les jurys ont voté
                default=False,
                output_field=FloatField()
            )
        ).order_by('-total_score')

        leaderboard = [
            {
                'team': project.team,
                'project': project.name,
                'total_score': project.total_score,
                'all_jurys_voted': project.all_jurys_voted,
            }
            for project in projects
        ]

        return Response(leaderboard)
