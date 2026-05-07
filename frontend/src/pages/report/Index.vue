<template>
  <div class="report-page">
    <h2>报表</h2>

    <!-- 生成报表 -->
    <el-card header="生成报表">
      <el-form :model="reportForm" label-position="top">
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="报表类型">
              <el-select v-model="reportForm.type" style="width:100%">
                <el-option label="任务列表" value="task_list" />
                <el-option label="工时统计" value="worklog_summary" />
                <el-option label="甘特图" value="gantt" />
                <el-option label="项目进度" value="progress" />
                <el-option label="燃尽图" value="burndown" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="开始日期">
              <el-date-picker v-model="reportForm.start_date" type="date" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="结束日期">
              <el-date-picker v-model="reportForm.end_date" type="date" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="导出格式">
              <el-select v-model="reportForm.format" style="width:100%">
                <el-option label="PDF" value="pdf" />
                <el-option label="Excel" value="excel" />
                <el-option label="CSV" value="csv" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-button type="primary" :loading="generating" @click="generateReport">生成报表</el-button>
      </el-form>
    </el-card>

    <!-- 报表历史 -->
    <el-card header="报表历史" style="margin-top:16px">
      <el-table :data="reports" stripe>
        <el-table-column prop="name" label="报表名称" />
        <el-table-column prop="type" label="类型" width="120" />
        <el-table-column prop="format" label="格式" width="80" />
        <el-table-column prop="created_at" label="生成时间" width="170" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button text size="small" type="primary" v-if="row.file_path" @click="download(row)">下载</el-button>
            <el-tag v-else size="small" type="warning">生成中</el-tag>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!reports.length" description="暂无报表" />
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const generating = ref(false)
const reportForm = ref({
  type: 'task_list', start_date: '', end_date: '', format: 'pdf'
})

const reports = ref([
  { id: 'r1', name: 'Sprint1进度报告', type: 'progress', format: 'PDF', file_path: '/reports/r1.pdf', created_at: '2026-05-07 14:30' },
  { id: 'r2', name: '工时统计表', type: 'worklog_summary', format: 'Excel', file_path: '/reports/r2.xlsx', created_at: '2026-05-01 09:00' }
])

async function generateReport() {
  generating.value = true
  try { ElMessage.success('报表生成任务已提交'); generating.value = false }
  catch { ElMessage.error('生成失败'); generating.value = false }
}

function download(row) { ElMessage.success('开始下载: ' + row.name) }
</script>
