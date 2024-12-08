from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, VoteViewSet, LeaderboardView, LoginView, JuryRegisterView, UserInfoView

# Router pour les ViewSets
router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'votes', VoteViewSet, basename='vote')

urlpatterns = [
    path('', include(router.urls)),                # Routes pour les projets et les votes
    path('ranking/', LeaderboardView.as_view(), name='leaderboard'),  # Classement global
    path('user-info/', UserInfoView.as_view(), name='user-info'),
    path('auth/login/', LoginView.as_view(), name='login'),   # Connexion
    path('auth/register/', JuryRegisterView.as_view(), name='register'),
]
