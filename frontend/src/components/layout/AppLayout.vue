<template>
  <el-container class="app-layout">
    <el-aside :width="isCollapse ? '64px' : '220px'" class="app-aside">
      <Sidebar :is-collapse="isCollapse" />
    </el-aside>
    <el-container>
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
.app-layout { height: 100vh; }
.app-aside {
  background: #304156;
  transition: width 0.3s;
  overflow: hidden;
}
.app-header {
  background: #fff;
  border-bottom: 1px solid #dcdfe6;
  padding: 0 16px;
}
.app-main {
  background: #f2f3f5;
  min-height: calc(100vh - 56px);
}
</style>
