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

    <!-- 提问趋势 + 文档上传 -->
    <div class="dashboard__row">
      <div class="card dashboard__chart">
        <div class="card__header">
          <TrendingUp :size="18" />
          <span>提问趋势</span>
          <div class="chart-tabs">
            <span :class="{ active: chartMode === 'hourly' }" @click="switchChart('hourly')">近14小时</span>
            <span :class="{ active: chartMode === 'daily' }" @click="switchChart('daily')">近14天</span>
          </div>
        </div>
        <div ref="chartRef" class="chart-container"></div>
      </div>
      <div class="card dashboard__upload">
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
            <el-tag size="small" :color="subjectColor(doc.subject)" style="color: #fff; border: none;">{{ doc.subject }}</el-tag>
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

    <!-- 复习建议 -->
    <div v-if="reviewSuggestions.length" class="card">
      <div class="card__header">
        <RefreshCw :size="18" />
        <span>复习建议</span>
      </div>
      <div class="review-list">
        <div v-for="item in reviewSuggestions" :key="item.knowledge_point" class="review-item">
          <div class="review-item__info">
            <span class="review-item__name">{{ item.knowledge_point }}</span>
            <el-tag size="small" :type="levelTagType(item.level)">{{ levelLabel(item.level) }}</el-tag>
          </div>
          <div class="review-item__meta">
            <span>{{ item.subject }}</span>
            <span>{{ item.days_inactive }} 天未复习</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  FileText, FileUp, FolderOpen, UploadCloud, Trash2,
  AlertTriangle, BookOpen, Lightbulb, ShieldAlert, TrendingUp,
  Target, RefreshCw,
} from 'lucide-vue-next'
import { fetchDocuments, uploadDocument, deleteDocument } from '@/apis/document'
import { fetchWeakPoints, fetchDailyStats, fetchDashboardStats } from '@/apis/analytics'
import { fetchGraph } from '@/apis/graph'

const documents = ref<any[]>([])
const weakPoints = ref<any[]>([])
const kpCount = ref(0)
const coveragePercent = ref(0)  // 改名但保留，存活跃知识点总数
const reviewCount = ref(0)
const reviewSuggestions = ref<any[]>([])
const chartRef = ref<HTMLElement>()
const chartMode = ref('daily')

let chartInstance: echarts.ECharts | null = null

// 统计卡片
const stats = computed(() => {
  const subjects = new Set(documents.value.map((d: any) => d.subject))
  return [
    { label: '文档总数', value: documents.value.length, icon: FolderOpen, color: 'var(--color-primary-500)', bg: 'var(--color-primary-50)' },
    { label: '学科数量', value: subjects.size, icon: BookOpen, color: 'var(--color-accent-700)', bg: 'var(--color-accent-50)' },
    { label: '知识点数', value: kpCount.value, icon: Lightbulb, color: 'var(--color-warning-700)', bg: 'var(--color-warning-50)' },
    { label: '活跃知识点', value: coveragePercent.value, icon: Target, color: '#6DC8EC', bg: '#E8F6FD' },
    { label: '薄弱知识点', value: weakPoints.value.length, icon: ShieldAlert, color: 'var(--color-error-500)', bg: 'var(--color-error-50)' },
    { label: '待复习', value: reviewCount.value, icon: RefreshCw, color: '#9581CC', bg: '#F0EDF8' },
  ]
})

// 加载数据
async function loadData() {
  try {
    const [docRes, wpRes, graphRes, dailyRes, dashRes] = await Promise.allSettled([
      fetchDocuments(),
      fetchWeakPoints(),
      fetchGraph(),
      fetchDailyStats(chartMode.value),
      fetchDashboardStats(),
    ])
    if (docRes.status === 'fulfilled') documents.value = docRes.value.data || []
    if (wpRes.status === 'fulfilled') weakPoints.value = wpRes.value.data || []
    if (graphRes.status === 'fulfilled') {
      const nodes = graphRes.value.data?.nodes || []
      kpCount.value = nodes.filter((n: any) => n.type === 'knowledge_point').length
    }
    if (dashRes.status === 'fulfilled') {
      const dash = dashRes.value.data || {}
      coveragePercent.value = dash.coverage?.total_active_kps || 0
      reviewCount.value = dash.review_count || 0
      reviewSuggestions.value = dash.review_suggestions || []
    }
    if (dailyRes.status === 'fulfilled') {
      await nextTick()
      renderChart(dailyRes.value.data || { dates: [], subjects: [], series: {} })
    }
  } catch { /* ignore */ }
}

async function switchChart(mode: string) {
  chartMode.value = mode
  try {
    const res: any = await fetchDailyStats(mode)
    await nextTick()
    renderChart(res.data || { dates: [], subjects: [], series: {} })
  } catch { /* ignore */ }
}

const CHART_COLORS = ['#3996ae', '#5AD8A6', '#F6BD16', '#F27C7C', '#9581CC', '#6DC8EC', '#FF9D4D', '#92D050', '#E885BA', '#8C8C8C']

function renderChart(data: { dates: string[]; subjects: string[]; series: Record<string, number[]> }) {
  if (!chartRef.value) return
  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }
  const seriesList = data.subjects.map((subject, i) => ({
    name: subject,
    type: 'bar' as const,
    stack: 'total',
    barWidth: 38,
    data: data.series[subject] || [],
    itemStyle: { color: CHART_COLORS[i % CHART_COLORS.length], borderRadius: [2, 2, 0, 0] },
  }))
  chartInstance.setOption({
    grid: { top: 20, right: 20, bottom: 50, left: 40 },
    legend: {
      bottom: 0,
      left: 'center',
      textStyle: { color: '#979999', fontSize: 11 },
    },
    xAxis: {
      type: 'category',
      data: data.dates,
      axisLine: { lineStyle: { color: '#d7d9d9' } },
      axisLabel: { color: '#979999', fontSize: 11 },
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#eef0f0' } },
      axisLabel: { color: '#979999', fontSize: 11 },
    },
    series: seriesList,
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#fff',
      borderColor: '#e5e7eb',
      textStyle: { color: '#1e1f1f', fontSize: 12 },
    },
  })
}

// 上传
function beforeUpload(file: File) {
  if (!file.name.endsWith('.pdf') && !file.name.endsWith('.docx')) {
    ElMessage.error('仅支持 PDF、DOCX 格式')
    return false
  }
  if (file.size === 0) {
    ElMessage.error('文件为空，请选择有效文件')
    return false
  }
  return true
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
const SUBJECT_COLORS: Record<string, string> = {
  '数学': 'rgba(57,150,174,0.75)',
  '语文': 'rgba(90,216,166,0.75)',
  '英语': 'rgba(246,189,22,0.75)',
  '物理': 'rgba(242,124,124,0.75)',
  '化学': 'rgba(149,129,204,0.75)',
  '历史': 'rgba(109,200,236,0.75)',
  '地理': 'rgba(255,157,77,0.75)',
  '生物': 'rgba(146,208,80,0.75)',
  '政治': 'rgba(232,133,186,0.75)',
  '其他': 'rgba(140,140,140,0.75)',
}

function subjectColor(subject: string) {
  return SUBJECT_COLORS[subject] || '#8C8C8C'
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

.chart-tabs {
  margin-left: auto;
  display: flex;
  gap: 2px;
  background: var(--gray-100);
  border-radius: 6px;
  padding: 2px;

  span {
    padding: 3px 10px;
    font-size: 12px;
    font-weight: 400;
    color: var(--gray-500);
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;

    &.active {
      background: var(--main-0);
      color: var(--main-800);
      font-weight: 500;
    }
  }
}

/* 统计卡片 */
.dashboard__stats {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
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
  padding: 12px 0;
  color: var(--gray-500);

  em {
    color: var(--color-primary-500);
    font-style: normal;
  }

  p {
    margin: 6px 0 2px;
    font-size: 13px;
  }
}

.upload-area__tip {
  font-size: 12px;
  color: var(--gray-400);
}

/* 折线图 */
.chart-container {
  height: 240px;
}

/* 趋势 + 上传同行 */
.dashboard__row {
  display: flex;
  gap: 16px;
}

.dashboard__chart {
  flex: 6;
}

.dashboard__upload {
  flex: 4;
  display: flex;
  flex-direction: column;

  :deep(.el-upload) {
    flex: 1;
  }

  :deep(.el-upload-dragger) {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
  }
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

/* 复习建议 */
.review-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.review-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  border-radius: 8px;
  background: var(--gray-50);
}

.review-item__info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.review-item__name {
  font-size: 14px;
  color: var(--main-800);
}

.review-item__meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--gray-500);
}
</style>
