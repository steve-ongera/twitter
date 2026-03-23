from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Tweet, Like, Bookmark, Hashtag, Notification, Message


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'display_name', 'email', 'is_verified', 'followers_count', 'created_at']
    list_filter = ['is_verified', 'is_private', 'is_staff']
    search_fields = ['username', 'email', 'display_name']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile', {'fields': ('display_name', 'bio', 'location', 'website', 'avatar', 'banner')}),
        ('Status', {'fields': ('is_verified', 'is_private')}),
    )


@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    list_display = ['user', 'content_preview', 'likes_count', 'replies_count', 'is_deleted', 'created_at']
    list_filter = ['is_deleted']
    search_fields = ['content', 'user__username']
    readonly_fields = ['slug', 'views_count']

    def content_preview(self, obj):
        return obj.content[:60]
    content_preview.short_description = 'Content'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'tweet', 'created_at']


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'tweet', 'created_at']


@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'tweets_count']
    readonly_fields = ['slug']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'sender', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'content_preview', 'is_read', 'created_at']

    def content_preview(self, obj):
        return obj.content[:40]
    content_preview.short_description = 'Content'