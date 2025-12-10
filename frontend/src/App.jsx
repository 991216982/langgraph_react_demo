import React, { useMemo, useState } from 'react'

export default function App() {
  const [input, setInput] = useState('帮我生成两天的晚餐计划并添加到家庭日历')
  const [messages, setMessages] = useState([])
  const [sessionId, setSessionId] = useState(() => Math.random().toString(36).slice(2))
  const [loading, setLoading] = useState(false)

  const send = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/invoke', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, messages: [["user", input]] })
      })
      const data = await response.json()
      setMessages(data.messages || [])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 800, margin: '40px auto', fontFamily: 'sans-serif' }}>
      <h2>Demo 家用助理</h2>
      <div style={{ display: 'flex', gap: 8 }}>
        <input style={{ flex: 1, padding: 8 }} value={input} onChange={event => setInput(event.target.value)} />
        <button onClick={send} disabled={loading}>{loading ? '发送中...' : '发送'}</button>
      </div>
      <div style={{ marginTop: 8, fontSize: 12, color: '#666' }}>会话ID：{sessionId}</div>
      <div style={{ marginTop: 24 }}>
        <h3>消息记录</h3>
        {useMemo(() => {
          const rounds = []
          let current = []
          for (const m of messages) {
            const role = m?.[0]
            const isUser = role === 'human' || role === 'user'
            if (isUser) {
              if (current.length) rounds.push(current)
              current = []
            }
            current.push(m)
          }
          if (current.length) rounds.push(current)
          const desc = rounds.reverse()
          return desc.map((round, idx) => (
            <div key={idx} style={{ borderTop: '1px solid #ddd', marginTop: 16, paddingTop: 16 }}>
              {round.map((message, i) => (
                <div key={i} style={{ marginBottom: 8 }}>
                  <strong>{message[0]}:</strong> {message[1]}
                </div>
              ))}
            </div>
          ))
        }, [messages])}
      </div>
    </div>
  )
}
