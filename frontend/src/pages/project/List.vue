<template>
  <div class="project-list">
    <div class="page-header">
      <h2>项目列表</h2>
      <el-button type="primary" @click="showCreate = true">+ 创建项目</el-button>
    </div>

    <!-- 搜索筛选栏 -->
    <div class="toolbar">
      <el-input v-model="search" placeholder="搜索项目..." prefix-icon="Search" clearable style="width:260px" />
      <el-select v-model="filterStatus" placeholder="状态筛选" clearable style="width:140px">
        <el-option label="全部" value="" />
        <el-option label="规划中" value="planning" />
        <el-option label="进行中" value="active" />
        <el-option label="已完成" value="completed" />
        <el-option label="已归档" value="archived" />
      </el-select>
    </div>

    <!-- 项目卡片网格 -->
    <el-row v-loading="store.loading" :gutter="16">
      <el-col v-for="p in store.projects" :key="p.id" :xs="24" :sm="12" :lg="8" style="margin-bottom:16px">
        <el-card shadow="hover" class="project-card" @click="$router.push(`/projects/${p.id}`)">
          <div class="card-header">
            <el-icon :size="24"><Folder /></el-icon>
            <span class="project-name">{{ p.name }}</span>
            <StatusTag :status="p.status" />
          </div>
          <p class="project-desc">{{ p.description || '暂无描述' }}</p>
          <div class="card-footer">
            <span>{{ p.member_count || 0 }} 人</span>
            <span>{{ p.start_date }} ~ {{ p.end_date }}</span>
          </div>
          <el-progress :percentage="p.progress || 0" :stroke-width="8"
            :color="progressColor(p.progress)" />
        </el-card>
      </el-col>
    </el-row>

    <el-empty v-if="!store.loading && !store.projects.length" description="暂无项目，点击上方按钮创建" />

    <!-- 创建项目对话框 -->
    <el-dialog v-model="showCreate" title="创建项目" width="520px" @closed="resetForm">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="项目描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="项目描述（选填）" />
        </el-form-item>
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="开始日期" prop="start_date">
              <el-date-picker v-model="form.start_date" type="date" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束日期" prop="end_date">
              <el-date-picker v-model="form.end_date" type="date" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="可见性" prop="visibility">
          <el-radio-group v-model="form.visibility">
            <el-radio value="private">私密</el-radio>
            <el-radio value="public">公开</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useProjectStore } from '@/stores/project'
import StatusTag from '@/components/common/StatusTag.vue'

const store = useProjectStore()
const search = ref('')
const filterStatus = ref('')
const showCreate = ref(false)
const creating = ref(false)
const formRef = ref()

const form = ref({ name: '', description: '', start_date: '', end_date: '', visibility: 'private' })
const rules = { name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }] }

function progressColor(v) { return v < 30 ? '#F56C6C' : v < 80 ? '#409EFF' : '#67C23A' }

async function handleCreate() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  creating.value = true
  try {
    await store.createProject(form.value)
    ElMessage.success('项目创建成功')
    showCreate.value = false
  } catch {
    ElMessage.error('创建失败')
  } finally {
    creating.value = false
  }
}

function resetForm() { form.value = { name: '', description: '', start_date: '', end_date: '', visibility: 'private' } }

watch([search, filterStatus], () => {
  store.fetchProjects({ search: search.value, status: filterStatus.value })
}, { immediate: true })
</script>

<style scoped lang="scss">
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.toolbar { display: flex; gap: 12px; margin-bottom: 16px; }
.project-card { cursor: pointer; }
.card-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.project-name { font-size: 16px; font-weight: 600; flex: 1; }
.project-desc { font-size: 13px; color: #909399; height: 40px; overflow: hidden; }
.card-footer { display: flex; justify-content: space-between; font-size: 12px; color: #909399; margin: 8px 0; }
</style>
