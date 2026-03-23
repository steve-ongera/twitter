from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.utils import timezone
import uuid


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    display_name = models.CharField(max_length=50, blank=True)
    bio = models.TextField(max_length=160, blank=True)
    location = models.CharField(max_length=30, blank=True)
    website = models.URLField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    banner = models.ImageField(upload_to='banners/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)
    followers = models.ManyToManyField(
        'self', symmetrical=False, related_name='following', blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"@{self.username}"

    @property
    def followers_count(self):
        return self.followers.count()

    @property
    def following_count(self):
        return self.following.count()

    @property
    def tweets_count(self):
        return self.tweets.filter(is_deleted=False).count()


class Tweet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tweets')
    content = models.TextField(max_length=280)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    media = models.ImageField(upload_to='tweet_media/', blank=True, null=True)
    reply_to = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL, related_name='replies'
    )
    retweet_of = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL, related_name='retweets'
    )
    is_deleted = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tweets'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base = f"{self.user.username}-{self.content[:50]}"
            self.slug = slugify(base)
            # Ensure uniqueness
            qs = Tweet.objects.filter(slug=self.slug)
            if qs.exists():
                self.slug = f"{self.slug}-{str(self.id)[:8]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"@{self.user.username}: {self.content[:50]}"

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def replies_count(self):
        return self.replies.filter(is_deleted=False).count()

    @property
    def retweets_count(self):
        return self.retweets.filter(is_deleted=False).count()

    @property
    def bookmarks_count(self):
        return self.bookmarks.count()


class Like(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'likes'
        unique_together = ('user', 'tweet')

    def __str__(self):
        return f"@{self.user.username} liked {self.tweet.id}"


class Bookmark(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bookmarks'
        unique_together = ('user', 'tweet')
        ordering = ['-created_at']

    def __str__(self):
        return f"@{self.user.username} bookmarked {self.tweet.id}"


class Hashtag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=110, unique=True, blank=True)
    tweets = models.ManyToManyField(Tweet, related_name='hashtags', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'hashtags'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"#{self.name}"

    @property
    def tweets_count(self):
        return self.tweets.count()


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('like', 'Like'),
        ('retweet', 'Retweet'),
        ('reply', 'Reply'),
        ('follow', 'Follow'),
        ('mention', 'Mention'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    tweet = models.ForeignKey(Tweet, null=True, blank=True, on_delete=models.CASCADE, related_name='notifications')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sender} → {self.recipient} ({self.notification_type})"


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField(max_length=1000)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'messages'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender} → {self.recipient}: {self.content[:30]}"