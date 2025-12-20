import { useState, useEffect } from 'react'
import { checkHealth } from './api'
import DocumentUpload from './components/DocumentUpload'
import ChatInterface from './components/ChatInterface'

function App() {
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)
  const [uploadedDoc, setUploadedDoc] = useState(null)

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const status = await checkHealth()
        setHealth(status)
      } catch (err) {
        setHealth({ status: 'degraded', error: err.message })
      } finally {
        setLoading(false)
      }
    }
    checkBackend()
    const interval = setInterval(checkBackend, 10000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="h-screen flex flex-col bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Background decoration */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse-glow"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-violet-500/10 rounded-full blur-3xl animate-pulse-glow"></div>
      </div>

      {/* Header - Fixed */}
      <header className="relative z-10 border-b border-white/10 bg-slate-900/80 backdrop-blur-xl flex-shrink-0">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-cyan-500 to-violet-500 rounded-xl flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div>
                <h1 className="text-lg font-bold text-white">RAG System</h1>
                <p className="text-slate-400 text-xs">Document Q&A with AI</p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              {uploadedDoc && (
                <div className="hidden sm:flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/30 px-3 py-1.5 rounded-lg">
                  <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
                  <span className="text-emerald-400 text-sm">{uploadedDoc.chunks_created} chunks</span>
                </div>
              )}
              <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border ${
                health?.status === 'healthy' 
                  ? 'bg-emerald-500/10 border-emerald-500/30' 
                  : 'bg-amber-500/10 border-amber-500/30'
              }`}>
                <div className={`w-2 h-2 rounded-full animate-pulse ${
                  health?.status === 'healthy' ? 'bg-emerald-400' : 'bg-amber-400'
                }`}></div>
                <span className={`text-sm ${
                  health?.status === 'healthy' ? 'text-emerald-400' : 'text-amber-400'
                }`}>
                  {loading ? 'Connecting...' : health?.status === 'healthy' ? 'Online' : 'Offline'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content - Fills remaining space */}
      <main className="relative z-10 flex-1 overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 h-full">
          {loading ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="w-12 h-12 border-4 border-slate-700 border-t-cyan-500 rounded-full animate-spin mx-auto mb-4"></div>
                <p className="text-slate-400">Loading...</p>
              </div>
            </div>
          ) : (
            <div className="grid lg:grid-cols-3 gap-6 h-full">
              {/* Left Panel - Sticky */}
              <div className="lg:col-span-1 h-full overflow-hidden flex flex-col">
                <div className="sticky top-0 space-y-4 overflow-y-auto flex-1 pr-2">
                  <DocumentUpload onUploadSuccess={setUploadedDoc} />
                  
                  {/* How it works */}
                  <div className="glass-card rounded-xl p-5">
                    <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
                      <span className="w-6 h-6 bg-gradient-to-br from-cyan-500 to-violet-500 rounded-lg flex items-center justify-center text-xs">?</span>
                      How it works
                    </h3>
                    <ol className="space-y-3 text-sm">
                      <li className="flex items-center gap-3 text-slate-300">
                        <span className="w-6 h-6 bg-cyan-500/20 text-cyan-400 rounded-md flex items-center justify-center text-xs font-bold">1</span>
                        Upload a PDF document
                      </li>
                      <li className="flex items-center gap-3 text-slate-300">
                        <span className="w-6 h-6 bg-violet-500/20 text-violet-400 rounded-md flex items-center justify-center text-xs font-bold">2</span>
                        Ask questions about it
                      </li>
                      <li className="flex items-center gap-3 text-slate-300">
                        <span className="w-6 h-6 bg-emerald-500/20 text-emerald-400 rounded-md flex items-center justify-center text-xs font-bold">3</span>
                        Get AI answers with citations
                      </li>
                    </ol>
                  </div>

                  {/* Stats */}
                  {uploadedDoc && (
                    <div className="glass-card rounded-xl p-5">
                      <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
                        <span className="w-6 h-6 bg-gradient-to-br from-emerald-500 to-cyan-500 rounded-lg flex items-center justify-center">
                          <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                          </svg>
                        </span>
                        Document Stats
                      </h3>
                      <div className="grid grid-cols-2 gap-3">
                        <div className="bg-cyan-500/10 border border-cyan-500/20 rounded-lg p-3 text-center">
                          <p className="text-2xl font-bold text-cyan-400">{uploadedDoc.chunks_created}</p>
                          <p className="text-xs text-slate-400">Chunks</p>
                        </div>
                        <div className="bg-violet-500/10 border border-violet-500/20 rounded-lg p-3 text-center">
                          <p className="text-2xl font-bold text-violet-400">{uploadedDoc.total_tokens}</p>
                          <p className="text-xs text-slate-400">Tokens</p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Chat Panel - Independent scroll */}
              <div className="lg:col-span-2 h-full overflow-hidden">
                <ChatInterface />
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

export default App
