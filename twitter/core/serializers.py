from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Tweet, Like, Bookmark, Hashtag, Notification, Message


# ─── USER SERIALIZERS ────────────────────────────────────────────────────────

class UserMiniSerializer(serializers.ModelSerializer):
    """Compact user info for embedding in tweets/notifications."""
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'display_name', 'avatar_url', 'is_verified']

    def get_avatar_url(self, obj):
        request = self.context.get('request')
        if obj.avatar and request:
            return request.build_absolute_uri(obj.avatar.url)
        return None


class UserSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()
    banner_url = serializers.SerializerMethodField()
    followers_count = serializers.ReadOnlyField()
    following_count = serializers.ReadOnlyField()
    tweets_count = serializers.ReadOnlyField()
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'display_name', 'bio', 'location', 'website',
            'avatar_url', 'banner_url', 'is_verified', 'is_private',
            'followers_count', 'following_count', 'tweets_count',
            'is_following', 'created_at',
        ]

    def get_avatar_url(self, obj):
        request = self.context.get('request')
        if obj.avatar and request:
            return request.build_absolute_uri(obj.avatar.url)
        return None

    def get_banner_url(self, obj):
        request = self.context.get('request')
        if obj.banner and request:
            return request.build_absolute_uri(obj.banner.url)
        return None

    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.followers.filter(id=request.user.id).exists()
        return False


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'display_name', 'password', 'password2']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        if not user.is_active:
            raise serializers.ValidationError("Account is disabled.")
        data['user'] = user
        return data


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['display_name', 'bio', 'location', 'website', 'avatar', 'banner', 'is_private']


# ─── TWEET SERIALIZERS ───────────────────────────────────────────────────────

class TweetSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)
    likes_count = serializers.ReadOnlyField()
    replies_count = serializers.ReadOnlyField()
    retweets_count = serializers.ReadOnlyField()
    bookmarks_count = serializers.ReadOnlyField()
    is_liked = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()
    is_retweeted = serializers.SerializerMethodField()
    reply_to_user = serializers.SerializerMethodField()
    media_url = serializers.SerializerMethodField()
    hashtags = serializers.SerializerMethodField()

    class Meta:
        model = Tweet
        fields = [
            'id', 'user', 'content', 'slug', 'media_url',
            'reply_to', 'reply_to_user', 'retweet_of',
            'likes_count', 'replies_count', 'retweets_count', 'bookmarks_count',
            'views_count', 'is_liked', 'is_bookmarked', 'is_retweeted',
            'hashtags', 'created_at',
        ]

    def get_media_url(self, obj):
        request = self.context.get('request')
        if obj.media and request:
            return request.build_absolute_uri(obj.media.url)
        return None

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def get_is_bookmarked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.bookmarks.filter(user=request.user).exists()
        return False

    def get_is_retweeted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.retweets.filter(user=request.user, is_deleted=False).exists()
        return False

    def get_reply_to_user(self, obj):
        if obj.reply_to:
            return obj.reply_to.user.username
        return None

    def get_hashtags(self, obj):
        return [tag.name for tag in obj.hashtags.all()]


class CreateTweetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tweet
        fields = ['content', 'media', 'reply_to', 'retweet_of']

    def create(self, validated_data):
        import re
        user = self.context['request'].user
        tweet = Tweet.objects.create(user=user, **validated_data)

        # Extract and link hashtags
        tags = re.findall(r'#(\w+)', tweet.content)
        for tag_name in tags:
            hashtag, _ = Hashtag.objects.get_or_create(name=tag_name.lower())
            hashtag.tweets.add(tweet)

        # Create notifications
        if tweet.reply_to and tweet.reply_to.user != user:
            Notification.objects.create(
                recipient=tweet.reply_to.user,
                sender=user,
                notification_type='reply',
                tweet=tweet,
            )
        # Mention notifications
        mentions = re.findall(r'@(\w+)', tweet.content)
        for username in mentions:
            try:
                mentioned_user = User.objects.get(username=username)
                if mentioned_user != user:
                    Notification.objects.create(
                        recipient=mentioned_user,
                        sender=user,
                        notification_type='mention',
                        tweet=tweet,
                    )
            except User.DoesNotExist:
                pass

        return tweet


# ─── ENGAGEMENT SERIALIZERS ──────────────────────────────────────────────────

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'tweet', 'created_at']
        read_only_fields = ['user']


class BookmarkSerializer(serializers.ModelSerializer):
    tweet = TweetSerializer(read_only=True)

    class Meta:
        model = Bookmark
        fields = ['id', 'tweet', 'created_at']


class HashtagSerializer(serializers.ModelSerializer):
    tweets_count = serializers.ReadOnlyField()

    class Meta:
        model = Hashtag
        fields = ['id', 'name', 'slug', 'tweets_count']


# ─── NOTIFICATION SERIALIZERS ────────────────────────────────────────────────

class NotificationSerializer(serializers.ModelSerializer):
    sender = UserMiniSerializer(read_only=True)
    tweet = TweetSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'sender', 'notification_type', 'tweet', 'is_read', 'created_at']


# ─── MESSAGE SERIALIZERS ─────────────────────────────────────────────────────

class MessageSerializer(serializers.ModelSerializer):
    sender = UserMiniSerializer(read_only=True)
    recipient = UserMiniSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'recipient', 'content', 'is_read', 'created_at']


class CreateMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['recipient', 'content']

    def create(self, validated_data):
        sender = self.context['request'].user
        return Message.objects.create(sender=sender, **validated_data)