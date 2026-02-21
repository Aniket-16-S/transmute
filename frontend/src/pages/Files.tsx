import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import FileListItem, { FileInfo } from '../components/FileListItem'

function Files() {
  const [files, setFiles] = useState<FileInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const navigate = useNavigate()

  useEffect(() => {
    const fetchFiles = async () => {
      try {
        const response = await fetch('/api/files/')
        if (!response.ok) throw new Error('Failed to fetch files')
        const data = await response.json()
        setFiles(data.files)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load files')
      } finally {
        setLoading(false)
      }
    }
    fetchFiles()
  }, [])

  const handleDelete = async (fileId: string) => {
    setDeletingId(fileId)
    try {
      const response = await fetch(`/api/files/${fileId}`, { method: 'DELETE' })
      if (!response.ok) throw new Error('Delete failed')
      setFiles(prev => prev.filter(f => f.id !== fileId))
      setSelectedIds(prev => {
        const newSet = new Set(prev)
        newSet.delete(fileId)
        return newSet
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Delete failed')
    } finally {
      setDeletingId(null)
    }
  }

  const toggleSelection = (fileId: string) => {
    setSelectedIds(prev => {
      const newSet = new Set(prev)
      if (newSet.has(fileId)) {
        newSet.delete(fileId)
      } else {
        newSet.add(fileId)
      }
      return newSet
    })
  }

  const handleBringToConverter = () => {
    const selectedFiles = files.filter(f => selectedIds.has(f.id))
    navigate('/', { state: { files: selectedFiles } })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-surface-dark to-surface-light p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-primary">Files</h1>
          {selectedIds.size > 0 && (
            <button
              onClick={handleBringToConverter}
              className="bg-primary hover:bg-primary-dark text-text font-semibold py-2 px-6 rounded-lg transition duration-200 shadow-md hover:shadow-lg"
            >
              Convert {selectedIds.size} File{selectedIds.size > 1 ? 's' : ''}
            </button>
          )}
        </div>

        {error && (
          <div className="p-3 bg-primary/20 border border-primary rounded-lg text-primary-light text-sm mb-4">
            {error}
          </div>
        )}

        {loading && (
          <p className="text-text-muted text-sm">Loading files...</p>
        )}

        {!loading && files.length === 0 && (
          <p className="text-text-muted text-sm">No uploaded files yet.</p>
        )}

        {!loading && files.length > 0 && (
          <div className="space-y-3">
            {files.map(file => (
              <div
                key={file.id}
                className="flex items-center gap-3"
              >
                <input
                  type="checkbox"
                  checked={selectedIds.has(file.id)}
                  onChange={() => toggleSelection(file.id)}
                  className="w-5 h-5 rounded border-surface-dark bg-surface-dark text-primary focus:ring-2 focus:ring-primary cursor-pointer"
                />
                <div className="flex-1">
                  <FileListItem
                    file={file}
                    onDelete={() => handleDelete(file.id)}
                    isDeleting={deletingId === file.id}
                    isPending={true}
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default Files
