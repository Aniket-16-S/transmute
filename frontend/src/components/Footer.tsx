import { useEffect, useState } from 'react'

function Footer() {
  const [appInfo, setAppInfo] = useState<{ name: string; version: string } | null>(null)

  useEffect(() => {
    fetch('/api/health/info')
      .then(res => res.json())
      .then(data => setAppInfo(data))
      .catch(() => {}) // Silently fail if API is unavailable
  }, [])

  return (
    <footer className="bg-surface-dark border-t border-surface-light mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="text-center text-text-muted text-sm">
          <p>
            {appInfo?.name || 'Transmute'} 
            {appInfo?.version && (
              <span className="ml-2 text-text-muted/60">v{appInfo.version}</span>
            )}
          </p>
        </div>
      </div>
    </footer>
  )
}

export default Footer
