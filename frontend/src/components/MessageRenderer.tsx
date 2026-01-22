/**
 * Message renderer component for Phase III chat interface.
 * Displays user and assistant messages with proper styling.
 */
'use client'

interface Message {
  role: 'user' | 'assistant'
  content: string
  tool_calls?: any[]
}

interface MessageRendererProps {
  message: Message
}

export function MessageRenderer({ message }: MessageRendererProps) {
  const isUser = message.role === 'user'

  return (
    <div style={{
      display: 'flex',
      justifyContent: isUser ? 'flex-end' : 'flex-start',
      width: '100%'
    }}>
      <div style={{
        maxWidth: '70%',
        padding: '12px 16px',
        borderRadius: '12px',
        background: isUser
          ? 'linear-gradient(90deg, #00f5ff 0%, #a855f7 100%)'
          : 'rgba(168, 85, 247, 0.1)',
        border: isUser ? 'none' : '1px solid #a855f7',
        color: '#fff'
      }}>
        <div style={{
          fontSize: '14px',
          lineHeight: '1.5',
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word'
        }}>
          {message.content}
        </div>

        {/* Show tool calls if present */}
        {message.tool_calls && message.tool_calls.length > 0 && (
          <div style={{
            marginTop: '12px',
            paddingTop: '12px',
            borderTop: '1px solid rgba(255, 255, 255, 0.2)',
            fontSize: '12px',
            opacity: 0.8
          }}>
            <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>
              Actions performed:
            </div>
            {message.tool_calls.map((call, index) => (
              <div key={index} style={{ marginLeft: '8px' }}>
                • {call.tool}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
