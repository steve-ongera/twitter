export function timeAgo(dateStr) {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = Math.floor((now - date) / 1000)

  if (diff < 60) return `${diff}s`
  if (diff < 3600) return `${Math.floor(diff / 60)}m`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h`
  if (diff < 604800) return `${Math.floor(diff / 86400)}d`

  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

export function formatCount(n) {
  if (!n && n !== 0) return '0'
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`
  return String(n)
}

export function formatTweetContent(content) {
  return content
    .replace(/#(\w+)/g, '<a href="/hashtag/$1" class="text-blue" onclick="event.stopPropagation()">#$1</a>')
    .replace(/@(\w+)/g, '<a href="/$1" class="text-blue" onclick="event.stopPropagation()">@$1</a>')
}

export function getInitials(name) {
  if (!name) return '?'
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
}