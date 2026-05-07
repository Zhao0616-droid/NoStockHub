<template>
  <div class="sprint-page">
    <div class="page-header">
      <h2>冲刺管理</h2>
      <el-button type="primary" @click="showCreate = true">+ 新建冲刺</el-button>
    </div>

    <!-- 进行中冲刺 -->
    <div v-if="activeSprint" class="active-sprint">
      <el-card>
        <template #header>
          <div class="sprint-header">
            <span>{{ activeSprint.name }} (进行中)</span>
            <el-tag type="warning">{{ activeSprint.status }}</el-tag>
          </div>
        </template>
        <p class="sprint-goal">目标: {{ activeSprint.goal }}</p>
        <p class="sprint-date">{{ activeSprint.start_date }} ~ {{ activeSprint.end_date }}</p>
        <el-progress :percentage="activeSprint.progress || 0" />
        <div class="sprint-tasks">
          <el-tag v-for="t in activeSprint.tasks" :key="t.id" closable style="margin:4px">{{ t.title }}</el-tag>
        </div>
        <div class="sprint-actions">
          <el-button @click="showBurndown = true">查看燃尽图</el-button>
          <el-button type="warning" @click="completeSprint">完成冲刺</el-button>
        </div>
      </el-card>
    </div>

    <!-- 规划中的冲刺 -->
    <el-card v-for="s in plannedSprints" :key="s.id" class="planned-sprint">
      <div class="sprint-header">
        <span>{{ s.name }} (规划中)</span>
        <el-button size="small" type="primary" @click="startSprint(s.id)">启动冲刺</el-button>
      </div>
      <p>{{ s.start_date }} ~ {{ s.end_date }}</p>
    </el-card>

    <!-- 燃尽图对话框 -->
    <el-dialog v-model="showBurndown" title="燃尽图" width="700px">
      <div class="burndown-chart" style="height:350px;background:#f5f7fa;display:flex;align-items:center;justify-content:center">
        <p style="color:#909399">燃尽图 — 使用 ECharts 渲染 (理想线 vs 实际线)</p>
      </div>
    </el-dialog>

    <!-- 创建冲刺对话框 -->
    <el-dialog v-model="showCreate" title="新建冲刺" width="480px">
      <el-form :model="form" label-position="top">
        <el-form-item label="冲刺名称" required>
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="冲刺目标">
          <el-input v-model="form.goal" type="textarea" />
        </el-form-item>
        <el-row :gutter="12">
          <el-col :span="12"><el-form-item label="开始日期"><el-date-picker v-model="form.start_date" style="width:100%" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="结束日期"><el-date-picker v-model="form.end_date" style="width:100%" /></el-form-item></el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="showCreate = false">取消</el-button>
        <el-button type="primary" @click="createSprint">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const showCreate = ref(false)
const showBurndown = ref(false)
const form = ref({ name: '', goal: '', start_date: '', end_date: '' })

const activeSprint = ref({
  id: 's1', name: 'Sprint 1', goal: '完成用户认证与项目管理模块', status: 'active',
  start_date: '2026-05-01', end_date: '2026-05-14', progress: 60,
  tasks: [{ id: 't1', title: '设计ER图' }, { id: 't2', title: '编写API' }]
})

const plannedSprints = ref([
  { id: 's2', name: 'Sprint 2', goal: '完成核心功能', start_date: '2026-05-15', end_date: '2026-05-28', status: 'planning' }
])

function createSprint() { ElMessage.success('冲刺创建成功'); showCreate.value = false }
function startSprint() { ElMessage.success('冲刺已启动') }
function completeSprint() { ElMessage.success('冲刺已完成') }
</script>

<style scoped lang="scss">
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.active-sprint { margin-bottom: 16px; }
.sprint-header { display: flex; justify-content: space-between; align-items: center; }
.sprint-goal { color: #606266; }
.sprint-date { font-size: 13px; color: #909399; margin: 8px 0; }
.sprint-tasks { margin: 12px 0; }
.sprint-actions { display: flex; gap: 8px; margin-top: 12px; }
.planned-sprint { margin-bottom: 12px; }
</style>
