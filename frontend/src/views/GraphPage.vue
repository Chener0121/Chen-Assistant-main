<template>
  <div class="graph-page">
    <div v-if="loading" class="graph-empty">加载中...</div>
    <div v-else-if="!graphData.nodes.length" class="graph-empty">
      <Network :size="40" />
      <p>暂无图谱数据，上传笔记并提问后自动生成</p>
    </div>
    <div v-else ref="chartRef" class="graph-chart"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as echarts from 'echarts'
import { Network } from 'lucide-vue-next'
import { fetchGraph } from '@/apis/graph'

const chartRef = ref<HTMLElement>()
const loading = ref(true)
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

function buildOption(data: { nodes: any[], edges: any[] }) {
  // 按学科分配颜色
  const subjectList = [...new Set(
    data.nodes.filter((n: any) => n.type === 'subject').map((n: any) => n.label)
  )]
  const subjectColorMap: Record<string, string> = {}
  subjectList.forEach((s, i) => {
    subjectColorMap[s] = SUBJECT_COLORS[s] || getColor(i)
  })

  // 知识点 → 所属学科颜色
  const kpColorMap: Record<string, string> = {}
  const docColorMap: Record<string, string> = {}
  for (const edge of data.edges) {
    if (edge.type === 'contains') {
      const subjectName = edge.source.replace('subject:', '')
      const kpName = edge.target.replace('kp:', '')
      kpColorMap[kpName] = subjectColorMap[subjectName] || getColor(0)
    }
    if (edge.type === 'belongs_to') {
      const subjectName = edge.source.replace('subject:', '')
      const docName = edge.target.replace('doc:', '')
      docColorMap[docName] = subjectColorMap[subjectName] || getColor(0)
    }
  }

  const nodes = data.nodes.map((n: any) => {
    let symbolSize: number
    let color: string
    let fontSize: number

    if (n.type === 'subject') {
      symbolSize = 50
      color = subjectColorMap[n.label] || getColor(0)
      fontSize = 14
    } else if (n.type === 'document') {
      symbolSize = 30
      color = docColorMap[n.label] || getColor(0)
      fontSize = 11
    } else {
      const count = n.count || 1
      symbolSize = Math.max(12, Math.min(35, 10 + count * 4))
      color = kpColorMap[n.label] || getColor(0)
      fontSize = 10
    }

    return {
      id: n.id,
      name: n.label,
      symbolSize,
      itemStyle: { color, borderColor: '#fff', borderWidth: 1 },
      label: {
        show: true,
        fontSize,
        color: '#323333',
      },
      category: subjectList.indexOf(n.label) >= 0
        ? subjectList.indexOf(n.label)
        : subjectList.indexOf(
            [...data.edges
              .filter((e: any) => e.target === n.id || e.source === n.id)
              .map((e: any) => {
                const sub = e.type === 'contains' ? e.source.replace('subject:', '') : ''
                return sub
              })
              .filter(Boolean)][0] || ''
          ),
    }
  })

  const links = data.edges.map((e: any) => ({
    source: e.source,
    target: e.target,
    lineStyle: {
      color: e.type === 'related' ? '#ccc' : '#aaa',
      width: e.type === 'related' ? 1 : 1.5,
      type: e.type === 'related' ? 'dashed' : 'solid',
      curveness: 0.1,
    },
  }))

  // 图例按学科显示
  const legendData = subjectList.map(s => ({
    name: s,
    itemStyle: { color: subjectColorMap[s] },
  }))

  return {
    tooltip: {
      formatter(params: any) {
        if (params.dataType === 'node') {
          return params.name
        }
        return ''
      },
    },
    legend: {
      data: legendData.map(l => l.name),
      bottom: 10,
      textStyle: { fontSize: 12, color: '#666' },
    },
    series: [{
      type: 'graph',
      layout: 'force',
      animation: true,
      draggable: true,
      roam: true,
      zoom: 1,
      force: {
        repulsion: 300,
        gravity: 0.1,
        edgeLength: [80, 200],
        friction: 0.6,
      },
      emphasis: {
        focus: 'adjacency',
        lineStyle: { width: 3 },
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
    }],
  }
}

function handleResize() {
  chartInstance?.resize()
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
        chartInstance.setOption(buildOption(data))
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
</style>
