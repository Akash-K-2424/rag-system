import { useState, useRef } from 'react'
import { uploadDocument } from '../api'

export default function DocumentUpload({ onUploadSuccess }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef(null)

  const handleFile = async (file) => {
    if (!file) return
    if (!file.name.endsWith('.pdf')) {
      setError('Only PDF files are supported')
      return
    }

    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      const response = await uploadDocument(file)
      setSuccess(`"${response.filename}" uploaded successfully`)
      onUploadSuccess?.(response)
      if (fileInputRef.current) fileInputRef.current.value = ''
      setTimeout(() => setSuccess(null), 5000)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(e.type === 'dragenter' || e.type === 'dragover')
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files?.[0]) handleFile(e.dataTransfer.files[0])
  }

  return (
    <div className="glass-card rounded-xl p-5">
      <h2 className="text-white font-semibold mb-4 flex items-center gap-2">
        <span className="w-6 h-6 bg-gradient-to-br from-cyan-500 to-violet-500 rounded-lg flex items-center justify-center">
          <svg className="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
        </span>
        Upload Document
      </h2>

      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all ${
          dragActive 
            ? 'border-cyan-400 bg-cyan-500/10' 
            : 'border-slate-600 hover:border-cyan-500/50 hover:bg-slate-800/50'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={(e) => handleFile(e.target.files?.[0])}
          disabled={loading}
          className="hidden"
        />

        {loading ? (
          <div className="py-2">
            <div className="w-10 h-10 border-3 border-slate-600 border-t-cyan-500 rounded-full animate-spin mx-auto mb-3"></div>
            <p className="text-slate-400 text-sm">Processing...</p>
          </div>
        ) : (
          <div className="py-2">
            <div className="w-12 h-12 bg-gradient-to-br from-cyan-500/20 to-violet-500/20 rounded-xl flex items-center justify-center mx-auto mb-3">
              <svg className="w-6 h-6 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <p className="text-white font-medium text-sm">Drop PDF here</p>
            <p className="text-slate-500 text-xs mt-1">or click to browse</p>
          </div>
        )}
      </div>

      {error && (
        <div className="mt-3 p-3 bg-rose-500/10 border border-rose-500/30 rounded-lg">
          <p className="text-rose-400 text-sm flex items-center gap-2">
            <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {error}
          </p>
        </div>
      )}

      {success && (
        <div className="mt-3 p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-lg">
          <p className="text-emerald-400 text-sm flex items-center gap-2">
            <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            {success}
          </p>
        </div>
      )}
    </div>
  )
}
