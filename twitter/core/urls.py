from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView, LoginView, LogoutView, MeView,
    UserViewSet, TweetViewSet, HashtagViewSet,
    BookmarkViewSet, NotificationViewSet, MessageViewSet,
    SearchView,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'tweets', TweetViewSet, basename='tweet')
router.register(r'hashtags', HashtagViewSet, basename='hashtag')
router.register(r'bookmarks', BookmarkViewSet, basename='bookmark')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = [
    # Auth
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', MeView.as_view(), name='me'),

    # Search
    path('search/', SearchView.as_view(), name='search'),

    # Router-generated endpoints
    path('', include(router.urls)),
]