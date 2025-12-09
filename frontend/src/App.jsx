import React, { useState } from 'react'

export default function App() {
  const [input, setInput] = useState('帮我生成两天的晚餐计划并添加到家庭日历')
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)

  const send = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/invoke', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: [["user", input]] })
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
      <div style={{ marginTop: 24 }}>
        <h3>消息</h3>
        <ul>
          {messages.map((message, index) => (
            <li key={index}><strong>{message[0]}:</strong> {message[1]}</li>
          ))}
        </ul>
      </div>
    </div>
  )
}
