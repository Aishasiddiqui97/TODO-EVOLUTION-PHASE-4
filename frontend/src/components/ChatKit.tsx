"""
Chat interface component for Phase III.
Provides a conversational UI for task management.
"""
'use client'

import { useState, useEffect, useRef } from 'react'
import { MessageRenderer } from './MessageRenderer'

interface Message {
  role: 'user' | 'assistant'
  content: string
  tool_calls?: any[]
}

interface ChatKitProps {
  conversationId?: string
  onConversationChange?: (conversationId: string) => void
}

export function ChatKit({ conversationId, onConversationChange }: ChatKitProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const userMessage: Message = {
      role: 'user',
      content: input
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify({
          conversation_id: conversationId,
          message: input
        })
      })

      if (!response.ok) {
        throw new Error('Failed to send message')
      }

      const data = await response.json()

      const assistantMessage: Message = {
        role: 'assistant',
        content: data.response,
        tool_calls: data.tool_calls
      }

      setMessages(prev => [...prev, assistantMessage])

      if (data.conversation_id && onConversationChange) {
        onConversationChange(data.conversation_id)
      }
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      background: 'linear-gradient(135deg, #0a0a0a 0%, #1a0a2e 50%, #0a0a0a 100%)'
    }}>
      {/* Header */}
      <div style={{
        padding: '20px',
        background: 'rgba(0, 0, 0, 0.5)',
        backdropFilter: 'blur(10px)',
        borderBottom: '2px solid #00f5ff'
      }}>
        <h1 style={{
          fontSize: '24px',
          background: 'linear-gradient(90deg, #00f5ff 0%, #a855f7 50%, #ff006e 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          margin: 0
        }}>
          Todo AI Chatbot
        </h1>
      </div>

      {/* Messages */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '20px',
        display: 'flex',
        flexDirection: 'column',
        gap: '16px'
      }}>
        {messages.length === 0 && (
          <div style={{
            textAlign: 'center',
            color: '#888',
            marginTop: '40px'
          }}>
            <p>Start a conversation by typing a message below.</p>
            <p style={{ fontSize: '14px', marginTop: '10px' }}>
              Try: "Add buy groceries to my list" or "What's on my todo list?"
            </p>
          </div>
        )}

        {messages.map((message, index) => (
          <MessageRenderer key={index} message={message} />
        ))}

        {loading && (
          <div style={{
            alignSelf: 'flex-start',
            padding: '12px 16px',
            background: 'rgba(168, 85, 247, 0.1)',
            border: '1px solid #a855f7',
            borderRadius: '12px',
            color: '#a855f7'
          }}>
            Thinking...
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div style={{
        padding: '20px',
        background: 'rgba(0, 0, 0, 0.5)',
        backdropFilter: 'blur(10px)',
        borderTop: '2px solid #00f5ff'
      }}>
        <div style={{
          display: 'flex',
          gap: '12px'
        }}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            disabled={loading}
            style={{
              flex: 1,
              padding: '12px 16px',
              background: 'rgba(255, 255, 255, 0.05)',
              border: '2px solid #00f5ff',
              borderRadius: '12px',
              color: '#fff',
              fontSize: '16px',
              outline: 'none'
            }}
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            style={{
              padding: '12px 24px',
              background: loading || !input.trim()
                ? 'rgba(100, 100, 100, 0.3)'
                : 'linear-gradient(90deg, #00f5ff 0%, #a855f7 100%)',
              border: 'none',
              borderRadius: '12px',
              color: '#fff',
              fontSize: '16px',
              fontWeight: 'bold',
              cursor: loading || !input.trim() ? 'not-allowed' : 'pointer',
              transition: 'all 0.3s'
            }}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  )
}
