import ReactMarkdown from 'react-markdown'

export default function Message({ message }) {
  const isUser = message.type === 'user'
  const isError = message.type === 'error'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[85%] px-4 py-3 rounded-2xl ${
        isError
          ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
          : isUser
            ? 'bg-gradient-to-r from-cyan-500 to-violet-500 text-white'
            : 'bg-slate-700/50 text-slate-200 border border-slate-600/50'
      }`}>
        {isUser || isError ? (
          <p className="text-sm whitespace-pre-wrap break-words leading-relaxed">
            {message.content}
          </p>
        ) : (
          <div className="text-sm prose prose-invert prose-sm max-w-none 
            prose-p:my-2 prose-p:leading-relaxed
            prose-ul:my-2 prose-ul:pl-4
            prose-ol:my-2 prose-ol:pl-4
            prose-li:my-1
            prose-strong:text-cyan-300 prose-strong:font-semibold
            prose-em:text-violet-300
            prose-headings:text-white prose-headings:font-semibold prose-headings:mt-3 prose-headings:mb-2
            prose-code:bg-slate-800 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:text-cyan-300
            prose-a:text-cyan-400 prose-a:no-underline hover:prose-a:underline">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        )}

        {!isUser && !isError && message.confidence !== undefined && (
          <div className="mt-3 pt-2 border-t border-slate-600/50 text-xs flex items-center gap-2 flex-wrap">
            <span className="flex items-center gap-1 bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded-full">
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {(message.confidence * 100).toFixed(0)}% confidence
            </span>
            <span className="bg-cyan-500/20 text-cyan-400 px-2 py-0.5 rounded-full">
              {message.retrieved_chunks} sources
            </span>
          </div>
        )}

        <p className={`text-xs mt-2 ${isUser ? 'text-white/60' : 'text-slate-500'}`}>
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </p>
      </div>
    </div>
  )
}
