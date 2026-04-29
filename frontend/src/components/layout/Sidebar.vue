<template>
  <div class="sidebar">
    <!-- 顶部 Logo -->
    <div class="sidebar__logo">
      <img src="/耄耋.jpg" alt="logo" class="sidebar__logo-img" />
    </div>

    <!-- 导航菜单 -->
    <nav class="sidebar__nav">
      <router-link
        v-for="item in menuItems"
        :key="item.path"
        :to="item.path"
        class="sidebar__item"
        :class="{ 'is-active': route.path === item.path }"
      >
        <span class="sidebar__icon">
          <component :is="item.icon" :size="20" />
        </span>
      </router-link>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { BarChart3, MessageCircle, Network } from 'lucide-vue-next'

const route = useRoute()

const menuItems = [
  { path: '/dashboard', icon: BarChart3 },
  { path: '/chat', icon: MessageCircle },
  { path: '/graph', icon: Network },
]
</script>

<style scoped lang="less">
.sidebar {
  width: 64px;
  height: 100vh;
  overflow: hidden;
  background: var(--bg-sider);
  border-right: 1px solid var(--gray-200);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar__logo {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid var(--gray-200);
  flex-shrink: 0;
}

.sidebar__logo-img {
  width: 42px;
  height: 42px;
  border-radius: 8px;
  object-fit: cover;
}

.sidebar__nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 12px;
  gap: 4px;
}

.sidebar__item {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  text-decoration: none;
  cursor: pointer;

  .sidebar__icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border-radius: 8px;
    background: var(--gray-100);
    color: var(--gray-600);
    transition: all 0.2s;
  }

  &:hover .sidebar__icon {
    background: var(--main-50);
    color: var(--color-primary-500);
  }

  &.is-active .sidebar__icon {
    color: var(--main-0);
    background: var(--color-primary-500);
  }
}
</style>
