<template>
  <div class="header">
    <span class="header__title">Chen-Assistant</span>
    <span class="header__time">{{ currentTime }}</span>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const currentTime = ref('')
let timer: number

function updateTime() {
  const now = new Date()
  currentTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  })
}

onMounted(() => {
  updateTime()
  timer = window.setInterval(updateTime, 1000)
})

onUnmounted(() => {
  clearInterval(timer)
})
</script>

<style scoped lang="less">
.header {
  height: 56px;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--main-0);
  border-bottom: 1px solid var(--gray-200);
  flex-shrink: 0;
}

.header__title {
  font-size: 16px;
  font-weight: 600;
  color: var(--main-800);
}

.header__time {
  font-size: 13px;
  color: var(--gray-500);
  font-variant-numeric: tabular-nums;
}
</style>
