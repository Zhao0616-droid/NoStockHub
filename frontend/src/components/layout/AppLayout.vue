<template>
  <el-container class="app-layout">
    <el-aside :width="isCollapse ? '64px' : '220px'" class="app-aside">
      <Sidebar :is-collapse="isCollapse" />
    </el-aside>
    <el-container class="app-right">
      <el-header height="56px" class="app-header">
        <Navbar @toggle-sidebar="isCollapse = !isCollapse" />
      </el-header>
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref } from 'vue'
import Navbar from './Navbar.vue'
import Sidebar from './Sidebar.vue'

const isCollapse = ref(false)
</script>

<style scoped lang="scss">
.app-layout {
  height: 100vh;
  overflow: hidden;
}
.app-aside {
  background: var(--app-sidebar-bg);
  transition: width 0.3s;
  overflow: hidden;
  height: 100vh;
}
.app-right {
  overflow: hidden;
}
.app-header {
  background: var(--app-header-bg);
  border-bottom: 1px solid var(--app-header-border);
  padding: 0 16px;
  flex-shrink: 0;
}
.app-main {
  background: var(--app-main-bg);
  flex: 1;
  overflow-y: auto;
}
</style>
