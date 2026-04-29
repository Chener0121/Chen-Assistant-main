<template>
  <div class="dashboard">
    <!-- 统计卡片行 -->
    <div class="dashboard__stats">
      <div v-for="stat in stats" :key="stat.label" class="card stat-card">
        <span class="stat-card__icon" :style="{ background: stat.bg, color: stat.color }">
          <component :is="stat.icon" :size="20" />
        </span>
        <div class="stat-card__info">
          <span class="stat-card__value">{{ stat.value }}</span>
          <span class="stat-card__label">{{ stat.label }}</span>
        </div>
      </div>
    </div>

    <!-- 文档上传 -->
    <div class="card">
      <div class="card__header">
        <FileUp :size="18" />
        <span>文档上传</span>
      </div>
      <el-upload
        drag
        :auto-upload="true"
        :show-file-list="false"
        accept=".pdf,.docx"
        :before-upload="beforeUpload"
        :http-request="handleUpload"
      >
        <div class="upload-area">
          <UploadCloud :size="36" />
          <p>拖拽文件到此处，或 <em>点击上传</em></p>
          <span class="upload-area__tip">支持 PDF、DOCX 格式</span>
        </div>
      </el-upload>
    </div>

    <!-- 文档列表 -->
    <div class="card">
      <div class="card__header">
        <FolderOpen :size="18" />
        <span>文档列表</span>
      </div>
      <div v-if="documents.length === 0" class="empty">暂无文档，请先上传学习笔记</div>
      <div v-else class="doc-list">
        <div v-for="doc in documents" :key="doc.file_id" class="doc-item">
          <div class="doc-item__info">
            <FileText :size="16" />
            <span class="doc-item__name">{{ doc.file_id }}</span>
            <el-tag size="small" :type="subjectTagType(doc.subject)">{{ doc.subject }}</el-tag>
          </div>
          <div class="doc-item__actions">
            <span class="doc-item__chunks">{{ doc.chunk_count }} 个片段</span>
            <el-button type="danger" text size="small" @click="handleDelete(doc.file_id)">
              <Trash2 :size="14" />
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 薄弱知识点 -->
    <div class="card">
      <div class="card__header">
        <AlertTriangle :size="18" />
        <span>薄弱知识点</span>
      </div>
      <div v-if="weakPoints.length === 0" class="empty">暂无薄弱知识点，开始提问后将自动分析</div>
      <div v-else class="weak-list">
        <div v-for="wp in weakPoints" :key="wp.knowledge_point" class="weak-item">
          <div class="weak-item__info">
            <span class="weak-item__name">{{ wp.knowledge_point }}</span>
            <el-tag size="small" :type="levelTagType(wp.level)">{{ levelLabel(wp.level) }}</el-tag>
          </div>
          <div class="weak-item__meta">
            <span>{{ wp.subject }}</span>
            <span>提问 {{ wp.ask_count }} 次</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  FileText, FileUp, FolderOpen, UploadCloud, Trash2,
  AlertTriangle, BookOpen, Lightbulb, ShieldAlert,
} from 'lucide-vue-next'
import { fetchDocuments, uploadDocument, deleteDocument } from '@/apis/document'
import { fetchWeakPoints } from '@/apis/analytics'
import { fetchGraph } from '@/apis/graph'

const documents = ref<any[]>([])
const weakPoints = ref<any[]>([])
const kpCount = ref(0)

// 统计卡片
const stats = computed(() => {
  const subjects = new Set(documents.value.map((d: any) => d.subject))
  return [
    { label: '文档总数', value: documents.value.length, icon: FolderOpen, color: 'var(--color-primary-500)', bg: 'var(--color-primary-50)' },
    { label: '学科数量', value: subjects.size, icon: BookOpen, color: 'var(--color-accent-700)', bg: 'var(--color-accent-50)' },
    { label: '知识点数', value: kpCount.value, icon: Lightbulb, color: 'var(--color-warning-700)', bg: 'var(--color-warning-50)' },
    { label: '薄弱知识点', value: weakPoints.value.length, icon: ShieldAlert, color: 'var(--color-error-500)', bg: 'var(--color-error-50)' },
  ]
})

// 加载数据
async function loadData() {
  try {
    const [docRes, wpRes, graphRes] = await Promise.allSettled([
      fetchDocuments(),
      fetchWeakPoints(),
      fetchGraph(),
    ])
    if (docRes.status === 'fulfilled') documents.value = docRes.value.data || []
    if (wpRes.status === 'fulfilled') weakPoints.value = wpRes.value.data || []
    if (graphRes.status === 'fulfilled') {
      const nodes = graphRes.value.data?.nodes || []
      kpCount.value = nodes.filter((n: any) => n.type === 'knowledge_point').length
    }
  } catch { /* ignore */ }
}

// 上传
function beforeUpload(file: File) {
  const valid = file.name.endsWith('.pdf') || file.name.endsWith('.docx')
  if (!valid) ElMessage.error('仅支持 PDF、DOCX 格式')
  return valid
}

async function handleUpload(options: any) {
  try {
    const res: any = await uploadDocument(options.file)
    if (res.code === 201) {
      ElMessage.success(`上传成功，新增 ${res.data.added} 个片段`)
    } else {
      ElMessage.info(res.msg || '文件内容未变化')
    }
    await loadData()
  } catch (e: any) {
    ElMessage.error(e.message || '上传失败')
  }
}

// 删除
async function handleDelete(fileId: string) {
  try {
    await ElMessageBox.confirm(`确定删除「${fileId}」？`, '删除确认', { type: 'warning' })
    await deleteDocument(fileId)
    ElMessage.success('删除成功')
    await loadData()
  } catch { /* cancelled */ }
}

// 学科标签颜色
function subjectTagType(subject: string) {
  const map: Record<string, string> = {
    '数学': 'primary', '语文': 'success', '英语': 'warning',
    '物理': 'danger', '化学': 'info',
  }
  return map[subject] || 'info'
}

// 薄弱等级
function levelTagType(level: string) {
  return { high: 'danger', medium: 'warning', low: 'info' }[level] || 'info'
}

function levelLabel(level: string) {
  return { high: '高', medium: '中', low: '低' }[level] || level
}

onMounted(loadData)
</script>

<style scoped lang="less">
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 通用卡片 */
.card {
  background: var(--main-0);
  border-radius: 12px;
  padding: 20px;
  border: 0.8px solid var(--gray-200);
  box-shadow: 0 1px 3px var(--shadow-1);
}

.card__header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: var(--main-800);
  margin-bottom: 16px;
}

/* 统计卡片 */
.dashboard__stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 20px;
}

.stat-card__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  flex-shrink: 0;
}

.stat-card__value {
  display: block;
  font-size: 22px;
  font-weight: 700;
  color: var(--main-900);
}

.stat-card__label {
  font-size: 12px;
  color: var(--gray-500);
}

/* 上传区域 */
.upload-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 0;
  color: var(--gray-500);

  em {
    color: var(--color-primary-500);
    font-style: normal;
  }

  p {
    margin: 8px 0 4px;
    font-size: 14px;
  }
}

.upload-area__tip {
  font-size: 12px;
  color: var(--gray-400);
}

/* 文档列表 */
.doc-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.doc-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  border-radius: 8px;
  background: var(--gray-50);
}

.doc-item__info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--gray-600);
}

.doc-item__name {
  font-size: 14px;
  color: var(--main-800);
}

.doc-item__actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.doc-item__chunks {
  font-size: 12px;
  color: var(--gray-500);
}

/* 薄弱知识点 */
.weak-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.weak-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  border-radius: 8px;
  background: var(--gray-50);
}

.weak-item__info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.weak-item__name {
  font-size: 14px;
  color: var(--main-800);
}

.weak-item__meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--gray-500);
}

/* 空状态 */
.empty {
  text-align: center;
  padding: 24px 0;
  color: var(--gray-400);
  font-size: 13px;
}
</style>
