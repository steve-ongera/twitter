# Xitter — Twitter/X Clone

A full-stack Twitter/X clone built with **Django REST Framework** (backend) and **React + Vite** (frontend). Features JWT authentication, real-time-style feed, tweets, likes, retweets, bookmarks, notifications, direct messages, hashtags, and full profile management.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, React Router v6, Vite |
| Styling | Custom CSS (Twitter-exact design system) |
| Icons | Remix Icons (CDN) |
| Fonts | Chirp (Google Fonts) |
| Backend | Django 4+, Django REST Framework |
| Auth | JWT via `djangorestframework-simplejwt` |
| Database | PostgreSQL (or SQLite for dev) |
| Media | Django media uploads (`MEDIA_ROOT`) |

---

## Project Structure

```
xitter/
├── index.html                        # HTML entry point (loads Remix Icons CDN)
├── vite.config.js                    # Vite config + dev proxy → localhost:8000
├── package.json                      # Dependencies & npm scripts
│
└── src/
    ├── main.jsx                      # React root, BrowserRouter, theme init
    ├── App.jsx                       # Route definitions (public + private)
    │
    ├── styles/
    │   └── main.css                  # Full design system (dark/light themes,
    │                                 #   layout, components, responsive)
    │
    ├── context/
    │   └── AuthContext.jsx           # Global auth state, JWT refresh logic,
    │                                 #   login / register / logout helpers
    │
    ├── utils/
    │   ├── api.js                    # Centralised fetch wrapper with auto
    │   │                             #   token refresh + all API calls
    │   └── helpers.js                # timeAgo(), formatCount(),
    │                                 #   formatTweetContent(), getInitials()
    │
    ├── components/
    │   ├── Avatar.jsx                # User avatar with initials fallback
    │   ├── TweetCard.jsx             # Tweet display with optimistic
    │   │                             #   like / retweet / bookmark toggles
    │   ├── TweetComposer.jsx         # Tweet creation box (text + image,
    │   │                             #   char counter, Ctrl+Enter to post)
    │   └── Layout.jsx                # App shell: left sidebar, right panel,
    │                                 #   mobile bottom nav, compose modal
    │
    └── pages/
        ├── Home.jsx                  # Feed (For You / Following tabs)
        ├── Explore.jsx               # Trending tweets + hashtag chips
        ├── Notifications.jsx         # Like / retweet / reply / follow / mention
        ├── Messages.jsx              # DM conversations + chat thread
        ├── Bookmarks.jsx             # Saved tweets + clear-all action
        ├── Profile.jsx               # User profile, edit modal, follow/unfollow
        ├── TweetDetail.jsx           # Single tweet + reply thread + composer
        ├── HashtagPage.jsx           # Tweets filtered by hashtag
        ├── SearchPage.jsx            # Search tweets / users / hashtags tabs
        ├── Settings.jsx              # Dark/light toggle, profile link, logout
        ├── Login.jsx                 # JWT login form
        ├── Register.jsx              # Registration form with validation
        └── NotFound.jsx              # 404 page
```

---

## Backend Structure (Django)

```
backend/
├── manage.py
├── config/
│   ├── settings.py
│   ├── urls.py                       # Includes /api/ prefix
│   └── wsgi.py
│
└── api/                              # Main Django app
    ├── models.py                     # User, Tweet, Like, Bookmark,
    │                                 #   Hashtag, Notification, Message
    ├── serializers.py                # DRF serializers for all models
    ├── views.py                      # ViewSets + APIViews
    └── urls.py                       # Router + auth + search endpoints
```

### API Endpoints

```
POST   /api/auth/register/                  Register new user
POST   /api/auth/login/                     Login → access + refresh tokens
POST   /api/auth/logout/                    Blacklist refresh token
POST   /api/auth/token/refresh/             Refresh access token
GET    /api/auth/me/                        Get current user
PATCH  /api/auth/me/                        Update profile

GET    /api/users/                          List / search users
GET    /api/users/{username}/               User profile
POST   /api/users/{username}/follow/        Follow user
POST   /api/users/{username}/unfollow/      Unfollow user
GET    /api/users/{username}/tweets/        User's tweets
GET    /api/users/{username}/likes/         User's liked tweets
GET    /api/users/{username}/followers/     Followers list
GET    /api/users/{username}/following/     Following list
GET    /api/users/suggestions/              Who to follow

GET    /api/tweets/                         List tweets
POST   /api/tweets/                         Create tweet
GET    /api/tweets/{slug}/                  Tweet detail (increments views)
DELETE /api/tweets/{slug}/                  Soft-delete tweet
GET    /api/tweets/feed/                    Home timeline
GET    /api/tweets/explore/                 Trending feed
GET    /api/tweets/{slug}/thread/           Tweet + replies
POST   /api/tweets/{slug}/like/             Toggle like
POST   /api/tweets/{slug}/bookmark/         Toggle bookmark
POST   /api/tweets/{slug}/retweet/          Toggle retweet

GET    /api/hashtags/trending/              Top 10 hashtags
GET    /api/hashtags/{slug}/tweets/         Tweets for hashtag

GET    /api/bookmarks/                      User's bookmarks
DELETE /api/bookmarks/clear_all/            Clear all bookmarks

GET    /api/notifications/                  User's notifications
POST   /api/notifications/mark_all_read/    Mark all as read
POST   /api/notifications/{id}/mark_read/   Mark one as read
GET    /api/notifications/unread_count/     Unread badge count

GET    /api/messages/conversations/         Conversation partners
GET    /api/messages/with_user/?username=   Message thread
POST   /api/messages/                       Send message

GET    /api/search/?q=&type=               Search (tweets/users/hashtags/all)
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL (or SQLite for local dev)

---

### Backend Setup

```bash
# 1. Clone and enter repo
git clone <repo-url>
cd xitter

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install Python dependencies
pip install django djangorestframework djangorestframework-simplejwt \
            django-cors-headers Pillow psycopg2-binary

# 4. Configure settings.py
```

**`config/settings.py` — required additions:**

```python
INSTALLED_APPS = [
    ...
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'api',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',   # Must be first
    ...
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
]

AUTH_USER_MODEL = 'api.User'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

```bash
# 5. Run migrations
python manage.py makemigrations
python manage.py migrate

# 6. Create superuser (optional)
python manage.py createsuperuser

# 7. Start Django server
python manage.py runserver       # → http://localhost:8000
```

---

### Frontend Setup

```bash
# From the xitter/ frontend directory:

# 1. Install dependencies
npm install

# 2. Start dev server (proxies /api → localhost:8000)
npm run dev                      # → http://localhost:3000

# 3. Build for production
npm run build
npm run preview
```

> The Vite dev server proxies all `/api/*` requests to `http://localhost:8000` automatically — no CORS issues during development.

---

## Features

### Authentication
- JWT access + refresh tokens stored in `localStorage`
- Automatic silent token refresh on 401 responses
- Protected routes redirect to `/login`; authenticated users redirect away from auth pages

### Tweets
- Create with text (up to 280 chars) and optional image attachment
- Soft delete (flagged `is_deleted`, not removed from DB)
- Hashtag auto-extraction and linking (`#tag` → `/hashtag/tag`)
- Mention auto-extraction and linking (`@user` → `/user`)
- View count increment on detail fetch

### Engagement
- **Like** — optimistic UI toggle with count update
- **Retweet** — creates a new tweet record linked to original
- **Bookmark** — save/unsave, bulk clear
- **Reply** — threaded replies on tweet detail page

### Feed
- **For You** — paginated feed from followed users + own tweets
- **Explore** — engagement-ranked tweets (likes + retweets + replies)

### Notifications
- Types: like, retweet, reply, follow, mention
- Unread badge on sidebar nav item (polls every 30s)
- Auto mark-all-read on page visit

### Direct Messages
- Conversation list with all DM partners
- Full message thread with sent/received bubble layout
- Auto-scroll to latest message

### Profile
- Banner image, avatar, bio, location, website
- Followers / following counts
- Tweets and Likes tabs
- Inline edit modal for own profile
- Follow / Unfollow with hover-to-unfollow button state

### Search
- Searches tweets, users, and hashtags simultaneously
- Tabbed results view

### Theming
- Dark (default) and Light mode
- Toggle in Settings, persisted to `localStorage`
- Full CSS variable system — every colour and spacing value is a variable

### Responsive Design
- **≥ 1265px** — full 3-column layout (sidebar + feed + right panel)
- **≤ 1024px** — right panel hidden, sidebar collapses to icon-only
- **≤ 768px** — sidebar replaced by mobile bottom navigation bar + FAB compose button
- **≤ 480px** — compact tweet cards and adjusted spacing

---

## Key Design Decisions

| Decision | Rationale |
|---|---|
| Optimistic UI for likes/retweets/bookmarks | Instant feedback; reverts on API error |
| Soft delete for tweets | Preserves reply threads and retweet references |
| Slug as tweet identifier in URLs | Human-readable URLs; matches DRF `lookup_field` |
| Token refresh in `api.js` wrapper | One place handles 401s across the entire app |
| CSS variables for theming | Zero-JS theme switching; light/dark with one attribute |
| `formatTweetContent()` with `dangerouslySetInnerHTML` | Renders clickable hashtag and mention links in tweet body |

---

## Environment Variables (Optional)

For production, move sensitive config to environment variables:

```bash
# .env (backend)
SECRET_KEY=your-secret-key
DEBUG=False
DATABASE_URL=postgres://user:pass@localhost/xitter
ALLOWED_HOSTS=yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

---

## License

MIT