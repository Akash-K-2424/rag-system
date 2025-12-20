import { useState } from 'react'

export default function CitationViewer({ citations }) {
  const [expanded, setExpanded] = useState(false)

  if (!citations?.length) return null

  return (
    <div className="ml-4 mt-2">
      <button
        onClick={() => setExpanded(!expanded)}
        className="text-sm text-cyan-400 hover:text-cyan-300 font-medium flex items-center gap-2 transition-colors"
      >
        <svg className={`w-3 h-3 transition-transform ${expanded ? 'rotate-90' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
        View {citations.length} source{citations.length > 1 ? 's' : ''}
      </button>
      
      {expanded && (
        <div className="mt-2 space-y-2 pl-5 border-l-2 border-slate-700">
          {citations.map((citation, idx) => (
            <div key={idx} className="text-sm bg-slate-800/50 border border-slate-700 p-3 rounded-lg">
              <p className="font-medium text-slate-300 flex items-center gap-2">
                <svg className="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                {citation.document}
              </p>
              <p className="text-slate-500 text-xs mt-1">
                Page {citation.page} • {citation.chunk_id}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
