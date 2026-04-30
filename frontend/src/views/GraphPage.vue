<template>
  <div class="graph-page">
    <div v-if="loading" class="graph-empty">加载中...</div>
    <div v-else-if="!graphData.nodes.length" class="graph-empty">
      <Network :size="40" />
      <p>暂无图谱数据，上传笔记并提问后自动生成</p>
    </div>
    <template v-else>
      <div class="graph-toolbar">
        <button
          :class="['graph-toolbar__btn', { active: layoutMode === 'force' }]"
          @click="switchLayout('force')"
        >力导向</button>
        <button
          :class="['graph-toolbar__btn', { active: layoutMode === 'circular' }]"
          @click="switchLayout('circular')"
        >环形</button>
      </div>
      <div ref="chartRef" class="graph-chart"></div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as echarts from 'echarts'
import { Network } from 'lucide-vue-next'
import { fetchGraph } from '@/apis/graph'

const chartRef = ref<HTMLElement>()
const loading = ref(true)
const layoutMode = ref<'force' | 'circular'>('force')
const graphData = ref<{ nodes: any[], edges: any[] }>({ nodes: [], edges: [] })
let chartInstance: echarts.ECharts | null = null

const SUBJECT_COLORS: Record<string, string> = {
  '数学': '#3996ae',
  '语文': '#5AD8A6',
  '英语': '#F6BD16',
  '物理': '#F27C7C',
  '化学': '#9581CC',
  '历史': '#6DC8EC',
  '地理': '#FF9D4D',
  '生物': '#92D050',
  '政治': '#E885BA',
  '其他': '#8C8C8C',
}

const DEFAULT_COLORS = [
  '#3996ae', '#5AD8A6', '#F6BD16', '#F27C7C', '#9581CC',
  '#6DC8EC', '#FF9D4D', '#92D050', '#E885BA', '#8C8C8C',
]

function getColor(index: number) {
  return DEFAULT_COLORS[index % DEFAULT_COLORS.length]
}

function getNodeSubject(nodeId: string, edges: any[]): string {
  for (const e of edges) {
    if (e.type === 'contains' && e.target === nodeId) return e.source.replace('subject:', '')
    if (e.type === 'belongs_to' && e.target === nodeId) return e.source.replace('subject:', '')
  }
  return ''
}

function buildOption(data: { nodes: any[], edges: any[] }, layout: 'force' | 'circular' = 'force') {
  const subjectList = [...new Set(
    data.nodes.filter((n: any) => n.type === 'subject').map((n: any) => n.label)
  )] as string[]
  const subjectColorMap: Record<string, string> = {}
  subjectList.forEach((s, i) => {
    subjectColorMap[s] = SUBJECT_COLORS[s] || getColor(i)
  })

  // 知识点/文档 → 学科颜色
  const kpColorMap: Record<string, string> = {}
  const docColorMap: Record<string, string> = {}
  for (const edge of data.edges) {
    if (edge.type === 'contains') {
      kpColorMap[edge.target.replace('kp:', '')] = subjectColorMap[edge.source.replace('subject:', '')] || getColor(0)
    }
    if (edge.type === 'belongs_to') {
      docColorMap[edge.target.replace('doc:', '')] = subjectColorMap[edge.source.replace('subject:', '')] || getColor(0)
    }
  }

  // 计算每个节点的关联学科
  const nodeSubjectMap: Record<string, string> = {}
  for (const n of data.nodes) {
    nodeSubjectMap[n.id] = n.type === 'subject'
      ? n.label
      : getNodeSubject(n.id, data.edges)
  }

  const nodes = data.nodes.map((n: any) => {
    let symbolSize: number
    let color: string
    let fontSize: number
    let fontWeight: string | number

    if (n.type === 'subject') {
      symbolSize = 50
      color = subjectColorMap[n.label] || getColor(0)
      fontSize = 14
      fontWeight = 600
    } else if (n.type === 'document') {
      symbolSize = 30
      color = docColorMap[n.label] || getColor(0)
      fontSize = 11
      fontWeight = 400
    } else {
      const count = n.count || 1
      symbolSize = Math.max(12, Math.min(35, 10 + count * 4))
      color = kpColorMap[n.label] || getColor(0)
      fontSize = 10
      fontWeight = 400
    }

    // 缩放时隐藏知识点标签：通过较大节点始终显示标签实现
    const isSmall = n.type === 'knowledge_point'

    return {
      id: n.id,
      name: n.label,
      symbolSize,
      itemStyle: { color, borderColor: '#fff', borderWidth: 1 },
      label: {
        show: !isSmall,
        fontSize,
        fontWeight,
        color: '#323333',
        position: 'bottom' as const,
      },
      category: subjectList.indexOf(nodeSubjectMap[n.id]),
      _type: n.type,
      _count: n.count || 0,
    }
  })

  const links = data.edges.map((e: any) => ({
    source: e.source,
    target: e.target,
    lineStyle: {
      color: e.type === 'related' ? '#d9d9d9' : '#bbb',
      width: e.type === 'related' ? 1 : 1.5,
      type: e.type === 'related' ? 'dashed' as const : 'solid' as const,
      curveness: 0.1,
    },
  }))

  const seriesConfig: any = {
    type: 'graph',
    animation: true,
    draggable: true,
    roam: true,
    zoom: 1,
    emphasis: {
      focus: 'adjacency',
      lineStyle: { width: 3 },
      label: { show: true, fontSize: 12 },
    },
    categories: subjectList.map(s => ({
      name: s,
      itemStyle: { color: subjectColorMap[s] },
    })),
    data: nodes,
    links,
    label: {
      show: true,
      position: 'bottom',
    },
  }

  if (layout === 'force') {
    seriesConfig.layout = 'force'
    seriesConfig.force = {
      repulsion: 300,
      gravity: 0.1,
      edgeLength: [80, 200],
      friction: 0.6,
    }
  } else {
    seriesConfig.layout = 'circular'
    seriesConfig.circular = {
      rotateLabel: true,
    }
  }

  return {
    tooltip: {
      trigger: 'item',
      formatter(params: any) {
        if (params.dataType === 'node') {
          const node = params.data
          const type = node._type
          const typeLabel = type === 'subject' ? '学科' : type === 'document' ? '文档' : '知识点'
          const lines = [`<b>${params.name}</b>`, `<span style="color:#999">${typeLabel}</span>`]
          if (type === 'knowledge_point' && node._count > 0) {
            lines.push(`出现 ${node._count} 次`)
          }
          const subject = nodeSubjectMap[params.data.id]
          if (subject && type !== 'subject') {
            lines.push(`学科：${subject}`)
          }
          return lines.join('<br/>')
        }
        if (params.dataType === 'edge') {
          return ''
        }
        return ''
      },
    },
    legend: {
      data: subjectList,
      bottom: 10,
      textStyle: { fontSize: 12, color: '#666' },
      selectedMode: true,
    },
    series: [seriesConfig],
  }
}

function switchLayout(mode: 'force' | 'circular') {
  layoutMode.value = mode
  if (chartInstance) {
    chartInstance.setOption(buildOption(graphData.value, mode), true)
  }
}

function handleResize() {
  chartInstance?.resize()
}

// 缩放时控制标签显示
function setupZoomListener() {
  if (!chartInstance) return
  chartInstance.on('graphroam', (params: any) => {
    if (params.zoom) {
      const option = chartInstance!.getOption() as any
      const series = option.series[0]
      const currentZoom = series.zoom || 1
      const newZoom = params.zoom * currentZoom
      // 缩放小于 0.7 时隐藏知识点标签
      const showSmallLabels = newZoom >= 0.7
      const newData = series.data.map((node: any) => {
        if (node._type === 'knowledge_point') {
          return { ...node, label: { ...node.label, show: showSmallLabels } }
        }
        return node
      })
      chartInstance!.setOption({ series: [{ data: newData }] })
    }
  })
}

async function loadData() {
  loading.value = true
  try {
    const res: any = await fetchGraph()
    const data = res.data || { nodes: [], edges: [] }
    graphData.value = data
    if (data.nodes.length) {
      loading.value = false
      await nextTick()
      if (chartRef.value) {
        chartInstance = echarts.init(chartRef.value)
        chartInstance.setOption(buildOption(data, layoutMode.value))
        setupZoomListener()
      }
      return
    }
  } catch { /* ignore */ } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
  chartInstance = null
})
</script>

<style scoped lang="less">
.graph-page {
  height: calc(100vh - 64px - 40px);
  position: relative;
}

.graph-chart {
  width: 100%;
  height: 100%;
}

.graph-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--gray-400);
  gap: 12px;

  p {
    font-size: 14px;
  }
}

.graph-toolbar {
  position: absolute;
  top: 12px;
  right: 16px;
  z-index: 10;
  display: flex;
  gap: 0;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--gray-200);
  background: var(--main-0);
}

.graph-toolbar__btn {
  padding: 6px 16px;
  border: none;
  background: transparent;
  font-size: 13px;
  color: var(--gray-600);
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: var(--gray-50);
  }

  &.active {
    background: var(--color-primary-500);
    color: var(--main-0);
  }

  &:first-child {
    border-right: 1px solid var(--gray-200);
  }
}
</style>
