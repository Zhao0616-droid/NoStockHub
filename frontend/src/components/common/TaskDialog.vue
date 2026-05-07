<template>
  <el-dialog
    :model-value="modelValue"
    :title="task ? '编辑任务' : '创建任务'"
    width="560px"
    @close="$emit('update:modelValue', false)"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
      <el-form-item label="任务标题" prop="title">
        <el-input v-model="form.title" placeholder="请输入任务标题" />
      </el-form-item>
      <el-form-item label="任务描述">
        <el-input v-model="form.description" type="textarea" :rows="3" placeholder="任务描述（选填）" />
      </el-form-item>
      <el-row :gutter="12">
        <el-col :span="8">
          <el-form-item label="任务类型">
            <el-select v-model="form.type" style="width:100%">
              <el-option label="任务" value="task" />
              <el-option label="缺陷" value="bug" />
              <el-option label="史诗" value="epic" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="优先级">
            <el-select v-model="form.priority" style="width:100%">
              <el-option label="低" value="low" />
              <el-option label="中" value="medium" />
              <el-option label="高" value="high" />
              <el-option label="紧急" value="urgent" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="负责人">
            <el-select v-model="form.assignee_id" style="width:100%" filterable placeholder="选择负责人">
              <el-option label="张三" value="u1" />
              <el-option label="李四" value="u2" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="12">
        <el-col :span="12">
          <el-form-item label="开始日期">
            <el-date-picker v-model="form.start_date" type="date" style="width:100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="截止日期">
            <el-date-picker v-model="form.due_date" type="date" style="width:100%" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="预估工时（小时）">
        <el-input-number v-model="form.estimated_hours" :min="0" :step="0.5" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="$emit('update:modelValue', false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="handleSave">
        {{ task ? '保存更改' : '创建任务' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useTaskStore } from '@/stores/task'

const props = defineProps({
  modelValue: Boolean,
  task: { type: Object, default: null },
  projectId: { type: String, default: '' }
})
const emit = defineEmits(['update:modelValue', 'saved'])
const taskStore = useTaskStore()

const formRef = ref()
const saving = ref(false)
const form = ref(getDefaultForm())
const rules = {
  title: [{ required: true, message: '请输入任务标题', trigger: 'blur' }],
  assignee_id: [{ required: true, message: '请选择负责人', trigger: 'change' }]
}

function getDefaultForm() {
  return {
    title: '', description: '', type: 'task', priority: 'medium',
    assignee_id: '', start_date: '', due_date: '', estimated_hours: 0,
    project_id: props.projectId
  }
}

watch(() => props.modelValue, (v) => {
  if (v && props.task) {
    form.value = { ...getDefaultForm(), ...props.task }
  } else if (v) {
    form.value = getDefaultForm()
  }
})

async function handleSave() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    if (props.task) {
      await taskStore.updateTask(props.task.id, form.value)
      ElMessage.success('任务更新成功')
    } else {
      await taskStore.createTask(form.value)
      ElMessage.success('任务创建成功')
    }
    emit('saved')
  } catch {
    ElMessage.error('操作失败')
  } finally {
    saving.value = false
  }
}
</script>
