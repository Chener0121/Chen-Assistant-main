<template>
  <div class="home">
    <h1>Chen-Assistant</h1>
    <p>学习助手，正在开发中...</p>
  </div>
</template>

<style scoped lang="less">
.home {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;

  h1 {
    font-size: var(--font-size-xl);
    color: var(--color-primary);
  }

  p {
    margin-top: var(--spacing-sm);
    color: var(--color-text-secondary);
  }
}
</style>
