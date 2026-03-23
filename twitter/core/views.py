from rest_framework import viewsets, status, generics, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404

from .models import User, Tweet, Like, Bookmark, Hashtag, Notification, Message
from .serializers import (
    UserSerializer, UserMiniSerializer, RegisterSerializer, LoginSerializer,
    UpdateProfileSerializer, TweetSerializer, CreateTweetSerializer,
    LikeSerializer, BookmarkSerializer, HashtagSerializer,
    NotificationSerializer, MessageSerializer, CreateMessageSerializer,
)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


# ─── AUTH VIEWS ──────────────────────────────────────────────────────────────

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = get_tokens_for_user(user)
        return Response({
            'user': UserSerializer(user, context={'request': request}).data,
            **tokens,
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        tokens = get_tokens_for_user(user)
        return Response({
            'user': UserSerializer(user, context={'request': request}).data,
            **tokens,
        })


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logged out successfully."})
        except Exception:
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


class MeView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UpdateProfileSerializer
        return UserSerializer


# ─── USER VIEWSET ─────────────────────────────────────────────────────────────

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by('-created_at')
    serializer_class = UserSerializer
    lookup_field = 'username'
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'display_name', 'bio']

    def get_permissions(self):
        if self.action in ['follow', 'unfollow']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_serializer_context(self):
        return {'request': self.request}

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def follow(self, request, username=None):
        target = self.get_object()
        if target == request.user:
            return Response({'detail': 'Cannot follow yourself.'}, status=400)
        if target.followers.filter(id=request.user.id).exists():
            return Response({'detail': 'Already following.'}, status=400)
        target.followers.add(request.user)
        Notification.objects.create(
            recipient=target, sender=request.user, notification_type='follow'
        )
        return Response({'detail': f'Now following @{target.username}.'})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def unfollow(self, request, username=None):
        target = self.get_object()
        if not target.followers.filter(id=request.user.id).exists():
            return Response({'detail': 'Not following.'}, status=400)
        target.followers.remove(request.user)
        return Response({'detail': f'Unfollowed @{target.username}.'})

    @action(detail=True, methods=['get'])
    def followers(self, request, username=None):
        user = self.get_object()
        qs = user.followers.all()
        page = self.paginate_queryset(qs)
        serializer = UserMiniSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['get'])
    def following(self, request, username=None):
        user = self.get_object()
        qs = user.following.all()
        page = self.paginate_queryset(qs)
        serializer = UserMiniSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['get'])
    def tweets(self, request, username=None):
        user = self.get_object()
        qs = Tweet.objects.filter(user=user, is_deleted=False, reply_to=None)
        page = self.paginate_queryset(qs)
        serializer = TweetSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['get'])
    def likes(self, request, username=None):
        user = self.get_object()
        tweet_ids = Like.objects.filter(user=user).values_list('tweet_id', flat=True)
        qs = Tweet.objects.filter(id__in=tweet_ids, is_deleted=False)
        page = self.paginate_queryset(qs)
        serializer = TweetSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def suggestions(self, request):
        """Users to follow - not already following."""
        following_ids = request.user.following.values_list('id', flat=True)
        qs = User.objects.exclude(
            Q(id__in=following_ids) | Q(id=request.user.id)
        ).order_by('?')[:5]
        serializer = UserMiniSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)


# ─── TWEET VIEWSET ────────────────────────────────────────────────────────────

class TweetViewSet(viewsets.ModelViewSet):
    queryset = Tweet.objects.filter(is_deleted=False)
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['content', 'user__username']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CreateTweetSerializer
        return TweetSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, *args, **kwargs):
        tweet = self.get_object()
        if tweet.user != request.user:
            return Response({'detail': 'Not authorized.'}, status=403)
        tweet.is_deleted = True
        tweet.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views_count += 1
        instance.save(update_fields=['views_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def feed(self, request):
        """Home timeline: tweets from followed users + own tweets."""
        following_ids = request.user.following.values_list('id', flat=True)
        qs = Tweet.objects.filter(
            Q(user__in=following_ids) | Q(user=request.user),
            is_deleted=False,
            reply_to=None,
        ).select_related('user', 'reply_to', 'retweet_of').order_by('-created_at')
        page = self.paginate_queryset(qs)
        serializer = TweetSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def explore(self, request):
        """Trending / explore feed."""
        qs = Tweet.objects.filter(is_deleted=False, reply_to=None).annotate(
            engagement=Count('likes') + Count('retweets') + Count('replies')
        ).order_by('-engagement', '-created_at')[:50]
        serializer = TweetSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def thread(self, request, slug=None):
        """Return the tweet + all its direct replies."""
        tweet = self.get_object()
        replies = Tweet.objects.filter(reply_to=tweet, is_deleted=False)
        data = {
            'tweet': TweetSerializer(tweet, context={'request': request}).data,
            'replies': TweetSerializer(replies, many=True, context={'request': request}).data,
        }
        return Response(data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, slug=None):
        tweet = self.get_object()
        like, created = Like.objects.get_or_create(user=request.user, tweet=tweet)
        if not created:
            like.delete()
            return Response({'liked': False, 'likes_count': tweet.likes_count})
        if tweet.user != request.user:
            Notification.objects.create(
                recipient=tweet.user, sender=request.user,
                notification_type='like', tweet=tweet,
            )
        return Response({'liked': True, 'likes_count': tweet.likes_count})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def bookmark(self, request, slug=None):
        tweet = self.get_object()
        bookmark, created = Bookmark.objects.get_or_create(user=request.user, tweet=tweet)
        if not created:
            bookmark.delete()
            return Response({'bookmarked': False})
        return Response({'bookmarked': True})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def retweet(self, request, slug=None):
        original = self.get_object()
        # Toggle: if already retweeted, delete the retweet
        existing = Tweet.objects.filter(
            user=request.user, retweet_of=original, is_deleted=False
        ).first()
        if existing:
            existing.is_deleted = True
            existing.save()
            return Response({'retweeted': False, 'retweets_count': original.retweets_count})
        retweet = Tweet.objects.create(
            user=request.user,
            content=original.content,
            retweet_of=original,
        )
        if original.user != request.user:
            Notification.objects.create(
                recipient=original.user, sender=request.user,
                notification_type='retweet', tweet=original,
            )
        return Response({
            'retweeted': True,
            'retweets_count': original.retweets_count,
            'tweet': TweetSerializer(retweet, context={'request': request}).data,
        })


# ─── HASHTAG VIEWSET ─────────────────────────────────────────────────────────

class HashtagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]

    @action(detail=True, methods=['get'])
    def tweets(self, request, slug=None):
        hashtag = self.get_object()
        qs = hashtag.tweets.filter(is_deleted=False).order_by('-created_at')
        page = self.paginate_queryset(qs)
        serializer = TweetSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'])
    def trending(self, request):
        qs = Hashtag.objects.annotate(count=Count('tweets')).order_by('-count')[:10]
        serializer = HashtagSerializer(qs, many=True)
        return Response(serializer.data)


# ─── BOOKMARK VIEWSET ────────────────────────────────────────────────────────

class BookmarkViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BookmarkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user).select_related('tweet')

    @action(detail=False, methods=['delete'])
    def clear_all(self, request):
        Bookmark.objects.filter(user=request.user).delete()
        return Response({'detail': 'All bookmarks cleared.'})


# ─── NOTIFICATION VIEWSET ────────────────────────────────────────────────────

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).select_related('sender', 'tweet')

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return Response({'detail': 'All notifications marked as read.'})

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notif = self.get_object()
        notif.is_read = True
        notif.save()
        return Response({'detail': 'Marked as read.'})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return Response({'unread_count': count})


# ─── MESSAGE VIEWSET ─────────────────────────────────────────────────────────

class MessageViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateMessageSerializer
        return MessageSerializer

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(
            Q(sender=user) | Q(recipient=user)
        ).select_related('sender', 'recipient')

    def get_serializer_context(self):
        return {'request': self.request}

    @action(detail=False, methods=['get'])
    def conversations(self, request):
        """Return list of unique conversation partners."""
        user = request.user
        sent = Message.objects.filter(sender=user).values_list('recipient_id', flat=True)
        received = Message.objects.filter(recipient=user).values_list('sender_id', flat=True)
        user_ids = set(list(sent) + list(received))
        users = User.objects.filter(id__in=user_ids)
        serializer = UserMiniSerializer(users, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def with_user(self, request):
        """Get message thread with a specific user."""
        username = request.query_params.get('username')
        if not username:
            return Response({'detail': 'username param required.'}, status=400)
        other = get_object_or_404(User, username=username)
        qs = Message.objects.filter(
            Q(sender=request.user, recipient=other) |
            Q(sender=other, recipient=request.user)
        ).order_by('created_at')
        # Mark as read
        qs.filter(recipient=request.user, is_read=False).update(is_read=True)
        serializer = MessageSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)


# ─── SEARCH VIEW ─────────────────────────────────────────────────────────────

class SearchView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        q = request.query_params.get('q', '').strip()
        kind = request.query_params.get('type', 'all')  # tweets | users | hashtags | all

        if not q:
            return Response({'error': 'Query param "q" is required.'}, status=400)

        result = {}

        if kind in ('tweets', 'all'):
            tweets = Tweet.objects.filter(
                Q(content__icontains=q), is_deleted=False
            ).order_by('-created_at')[:20]
            result['tweets'] = TweetSerializer(tweets, many=True, context={'request': request}).data

        if kind in ('users', 'all'):
            users = User.objects.filter(
                Q(username__icontains=q) | Q(display_name__icontains=q)
            )[:10]
            result['users'] = UserSerializer(users, many=True, context={'request': request}).data

        if kind in ('hashtags', 'all'):
            tags = Hashtag.objects.filter(name__icontains=q.lstrip('#'))[:10]
            result['hashtags'] = HashtagSerializer(tags, many=True).data

        return Response(result)