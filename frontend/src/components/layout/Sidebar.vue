<template>
  <div class="sidebar">
    <div class="logo">
      <span v-if="!isCollapse">NoStockHub</span>
      <span v-else>N</span>
    </div>
    <el-menu
      :default-active="activeMenu"
      :collapse="isCollapse"
      router
    >
      <el-menu-item index="/dashboard">
        <el-icon><Odometer /></el-icon>
        <template #title>仪表盘</template>
      </el-menu-item>
      <el-menu-item index="/projects">
        <el-icon><Folder /></el-icon>
        <template #title>项目列表</template>
      </el-menu-item>

      <template v-if="isProjectRoute">
        <el-divider style="margin:8px 0" />
        <el-menu-item :index="`/projects/${projectId}`">
          <el-icon><DataBoard /></el-icon>
          <template #title>项目概览</template>
        </el-menu-item>
        <el-menu-item :index="`/projects/${projectId}/tasks`">
          <el-icon><List /></el-icon>
          <template #title>任务列表</template>
        </el-menu-item>
        <el-menu-item :index="`/projects/${projectId}/board`">
          <el-icon><Grid /></el-icon>
          <template #title>任务看板</template>
        </el-menu-item>
        <el-menu-item :index="`/projects/${projectId}/gantt`">
          <el-icon><TrendCharts /></el-icon>
          <template #title>甘特图</template>
        </el-menu-item>
        <el-menu-item :index="`/projects/${projectId}/sprints`">
          <el-icon><Timer /></el-icon>
          <template #title>冲刺管理</template>
        </el-menu-item>
        <el-menu-item :index="`/projects/${projectId}/reports`">
          <el-icon><Document /></el-icon>
          <template #title>报表</template>
        </el-menu-item>
        <el-menu-item :index="`/projects/${projectId}/worklogs`">
          <el-icon><Clock /></el-icon>
          <template #title>工时管理</template>
        </el-menu-item>
        <el-menu-item :index="`/projects/${projectId}/files`">
          <el-icon><FolderOpened /></el-icon>
          <template #title>文件管理</template>
        </el-menu-item>
        <el-menu-item :index="`/projects/${projectId}/rates`">
          <el-icon><Coin /></el-icon>
          <template #title>费率管理</template>
        </el-menu-item>
      </template>
    </el-menu>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  Odometer, Folder, DataBoard, List,
  Grid, TrendCharts, Timer, Document,
  Clock, FolderOpened, Coin
} from '@element-plus/icons-vue'

defineProps({ isCollapse: Boolean })
const route = useRoute()

const activeMenu = computed(() => route.path)
const isProjectRoute = computed(() => route.params.id)
const projectId = computed(() => route.params.id)
</script>

<style scoped lang="scss">
.sidebar { height: 100%; display: flex; flex-direction: column; }
.logo {
  height: 56px; display: flex; align-items: center; justify-content: center;
  color: #fff; font-size: 18px; font-weight: bold;
  border-bottom: 1px solid var(--app-sidebar-logo-border);
}
.el-menu {
  border-right: none; flex: 1; overflow-y: auto;
  --el-menu-bg-color: var(--app-sidebar-bg);
  --el-menu-text-color: var(--app-sidebar-text);
  --el-menu-active-color: var(--app-sidebar-active);
  --el-menu-hover-bg-color: var(--app-sidebar-logo-border);
}
/* divider 颜色跟随 */
:deep(.el-divider) {
  border-color: var(--app-sidebar-logo-border);
}
</style>
