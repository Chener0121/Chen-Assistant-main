import api from './index'

interface HistoryItem {
  role: string
  content: string
}

export function askQuestion(
  question: string,
  threadId: string = 'default',
  history: HistoryItem[] = [],
  summary: string = '',
) {
  return api.post('/qa', {
    question,
    thread_id: threadId,
    history,
    summary,
  })
}

export function summarizeMessages(messages: HistoryItem[]) {
  return api.post('/conversations/summary', { messages })
}
