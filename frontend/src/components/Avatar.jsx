import { getInitials } from '../utils/helpers'

export default function Avatar({ user, size = 'md', className = '' }) {
  const sizeClass = `avatar-${size}`
  const src = user?.avatar_url

  return (
    <div className={`avatar ${sizeClass} ${className}`}>
      {src
        ? <img src={src} alt={user?.username} />
        : <span>{getInitials(user?.display_name || user?.username)}</span>
      }
    </div>
  )
}