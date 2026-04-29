import api from './index'

export function askQuestion(question: string, threadId: string = 'default') {
  return api.post('/qa', { question, thread_id: threadId })
}
