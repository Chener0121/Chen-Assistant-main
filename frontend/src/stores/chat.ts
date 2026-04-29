import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface Message {
  role: 'user' | 'assistant'
  content: string
  data?: any
}

export interface Conversation {
  id: string
  title: string
  messages: Message[]
  summary: string      // 旧消息的压缩摘要
  createdAt: string
}

const STORAGE_KEY = 'chen-chat'

// 未压缩消息超过此数量时触发摘要压缩
const COMPRESS_THRESHOLD = 20
// 每次压缩处理的消息数
const COMPRESS_BATCH = 10

export const useChatStore = defineStore('chat', () => {
  const conversations = ref<Conversation[]>([])
  const activeId = ref('')
  const loading = ref(false)

  const activeConversation = computed(() =>
    conversations.value.find(c => c.id === activeId.value),
  )

  function load() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      if (raw) {
        const data = JSON.parse(raw)
        conversations.value = data.conversations || []
        activeId.value = data.activeId || ''
        // 兼容没有 summary 字段的旧会话
        conversations.value.forEach(c => {
          if (c.summary === undefined) c.summary = ''
        })
      }
    } catch { /* ignore */ }
  }

  function save() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      conversations: conversations.value,
      activeId: activeId.value,
    }))
  }

  function createConversation() {
    const conv: Conversation = {
      id: Date.now().toString(),
      title: '新对话',
      messages: [],
      summary: '',
      createdAt: new Date().toISOString(),
    }
    conversations.value.unshift(conv)
    activeId.value = conv.id
    save()
  }

  function switchConversation(id: string) {
    activeId.value = id
    save()
  }

  function deleteConversation(id: string) {
    conversations.value = conversations.value.filter(c => c.id !== id)
    if (activeId.value === id) {
      activeId.value = conversations.value[0]?.id || ''
    }
    save()
  }

  function addUserMessage(content: string) {
    const conv = activeConversation.value
    if (!conv) return
    conv.messages.push({ role: 'user', content })
    if (conv.title === '新对话') {
      conv.title = content.length > 20 ? content.slice(0, 20) + '...' : content
    }
    save()
  }

  function addAssistantMessage(content: string, data?: any) {
    const conv = activeConversation.value
    if (!conv) return
    conv.messages.push({ role: 'assistant', content, data })
    save()
  }

  /** 获取最近 10 条消息作为 history 发给后端 */
  function getRecentHistory(): { role: string, content: string }[] {
    const conv = activeConversation.value
    if (!conv) return []
    const recent = conv.messages.slice(-10)
    return recent.map(m => ({
      role: m.role === 'user' ? 'human' : 'ai',
      content: m.content,
    }))
  }

  /** 检查是否需要压缩，如果需要返回待压缩的消息 */
  function getMessagesToCompress(): { role: string, content: string }[] | null {
    const conv = activeConversation.value
    if (!conv || conv.messages.length <= COMPRESS_THRESHOLD) return null
    const batch = conv.messages.slice(0, COMPRESS_BATCH)
    return batch.map(m => ({
      role: m.role === 'user' ? 'human' : 'ai',
      content: m.content,
    }))
  }

  /** 压缩完成后更新 summary 并移除已压缩的消息 */
  function applyCompression(summary: string) {
    const conv = activeConversation.value
    if (!conv) return
    conv.summary = conv.summary
      ? conv.summary + '\n' + summary
      : summary
    conv.messages = conv.messages.slice(COMPRESS_BATCH)
    save()
  }

  return {
    conversations,
    activeId,
    activeConversation,
    loading,
    load,
    createConversation,
    switchConversation,
    deleteConversation,
    addUserMessage,
    addAssistantMessage,
    getRecentHistory,
    getMessagesToCompress,
    applyCompression,
  }
})
