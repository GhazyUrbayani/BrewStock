// dibantu AI: AssistantPage
import { useCallback, useEffect, useRef, useState } from 'react'
import './AssistantPage.css'

type AssistantPageProps = {
  authRequest: <T>(
    pathValue: string,
    optionsValue?: { method?: string; body?: unknown },
  ) => Promise<T>
}

type AssistantMessage = {
  id: string
  role: 'user' | 'assistant'
  content: string
  createdAt: string
}

type InsightPayload =
  | string
  | {
      insight?: string
      message?: string
      response?: string
    }

const timeFormatter = new Intl.DateTimeFormat('id-ID', {
  hour: '2-digit',
  minute: '2-digit',
})

function formatTime(value: string) {
  const parsedDate = new Date(value)
  if (Number.isNaN(parsedDate.getTime())) {
    return ''
  }
  return timeFormatter.format(parsedDate)
}

function readInsightText(payloadValue: InsightPayload) {
  if (typeof payloadValue === 'string') {
    return payloadValue
  }

  if (payloadValue.insight && typeof payloadValue.insight === 'string') {
    return payloadValue.insight
  }

  if (payloadValue.message && typeof payloadValue.message === 'string') {
    return payloadValue.message
  }

  if (payloadValue.response && typeof payloadValue.response === 'string') {
    return payloadValue.response
  }

  return 'Insight belum tersedia.'
}

function buildMessage(role: 'user' | 'assistant', content: string): AssistantMessage {
  return {
    id: crypto.randomUUID(),
    role,
    content,
    createdAt: new Date().toISOString(),
  }
}

export default function AssistantPage({ authRequest }: AssistantPageProps) {
  const [messageItems, setMessageItems] = useState<AssistantMessage[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')
  const messageListRef = useRef<HTMLDivElement | null>(null)

  const sendPrompt = useCallback(async () => {
    const trimmedValue = inputValue.trim()
    if (!trimmedValue || isTyping) {
      return
    }

    setErrorMessage('')
    setInputValue('')
    const userMessage = buildMessage('user', trimmedValue)
    setMessageItems((previousValue) => [...previousValue, userMessage])
    setIsTyping(true)

    try {
      const payloadValue = await authRequest<InsightPayload>('/api/v1/ai/insight', {
        method: 'POST',
        body: { message: trimmedValue },
      })
      const insightText = readInsightText(payloadValue)
      const assistantMessage = buildMessage('assistant', insightText)
      setMessageItems((previousValue) => [...previousValue, assistantMessage])
    } catch (errorValue) {
      const messageValue = errorValue instanceof Error ? errorValue.message : 'Insight gagal dimuat.'
      setErrorMessage(messageValue)
    } finally {
      setIsTyping(false)
    }
  }, [authRequest, inputValue, isTyping])

  const clearConversation = useCallback(() => {
    setMessageItems([])
    setErrorMessage('')
  }, [])

  useEffect(() => {
    if (!messageListRef.current) {
      return
    }
    messageListRef.current.scrollTop = messageListRef.current.scrollHeight
  }, [messageItems, isTyping])

  return (
    <section className="assistant-panel" aria-label="AI assistant">
      <header className="assistant-header">
        <div>
          <p className="assistant-eyebrow">AI assistant</p>
          <h2 className="assistant-title">Tanya insight stok</h2>
        </div>
        <div className="assistant-actions">
          <button
            type="button"
            className="ghost-button"
            onClick={clearConversation}
            aria-label="Bersihkan percakapan"
            disabled={messageItems.length === 0}
          >
            Reset
          </button>
        </div>
      </header>

      <div
        className="assistant-body"
        role="log"
        aria-live="polite"
        aria-relevant="additions"
        ref={messageListRef}
      >
        {messageItems.length === 0 ? (
          <div className="assistant-empty">Tanyakan rekomendasi restock atau status stok terkini.</div>
        ) : (
          messageItems.map((itemValue) => (
            <article key={itemValue.id} className={`assistant-message ${itemValue.role}`}>
              <p>{itemValue.content}</p>
              <span className="assistant-time">{formatTime(itemValue.createdAt)}</span>
            </article>
          ))
        )}
        {isTyping ? (
          <div className="assistant-typing" role="status" aria-label="Claude mengetik">
            <span>Claude sedang mengetik</span>
            <span className="assistant-dots">
              <span className="assistant-dot" />
              <span className="assistant-dot" />
              <span className="assistant-dot" />
            </span>
          </div>
        ) : null}
      </div>

      <div className="assistant-footer">
        <div className="assistant-error" aria-live="polite">
          {errorMessage}
        </div>
        <form
          className="assistant-form"
          onSubmit={(eventValue) => {
            eventValue.preventDefault()
            void sendPrompt()
          }}
        >
          <textarea
            className="assistant-input"
            value={inputValue}
            onChange={(eventValue) => setInputValue(eventValue.target.value)}
            onKeyDown={(eventValue) => {
              if (eventValue.key === 'Enter' && !eventValue.shiftKey) {
                eventValue.preventDefault()
                void sendPrompt()
              }
            }}
            placeholder="Contoh: Apakah stok susu cukup untuk 7 hari ke depan?"
            aria-label="Tulis pertanyaan untuk AI"
          />
          <button
            type="submit"
            className="primary-button"
            aria-label="Kirim pesan ke AI"
            disabled={isTyping || inputValue.trim().length === 0}
          >
            {isTyping ? 'Menunggu...' : 'Kirim'}
          </button>
        </form>
      </div>
    </section>
  )
}

export type { AssistantPageProps }
