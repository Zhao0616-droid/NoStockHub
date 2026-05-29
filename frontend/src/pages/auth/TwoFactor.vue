<template>
  <div class="two-factor-page">
    <div class="two-factor-card">
      <h1>双因素认证</h1>
      <p class="subtitle">请输入您的认证器应用中显示的6位验证码</p>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="验证码" prop="code">
          <el-input
            v-model="form.code"
            placeholder="000000"
            maxlength="6"
            @keyup.enter="verify"
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            style="width: 100%"
            @click="verify"
          >
            {{ loading ? '验证中...' : '验 证' }}
          </el-button>
        </el-form-item>
      </el-form>

      <el-link type="primary" @click="showBackup = true">
        使用备份码
      </el-link>
    </div>

    <!-- 使用备份码对话框 -->
    <el-dialog v-model="showBackup" title="使用备份码" width="400px">
      <el-form :model="backupForm" label-position="top">
        <el-form-item label="备份码">
          <el-input
            v-model="backupForm.code"
            type="password"
            show-password
            placeholder="请输入备份码"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showBackup = false">取消</el-button>
        <el-button type="primary" :loading="loading" @click="verifyBackup">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const formRef = ref()
const loading = ref(false)
const showBackup = ref(false)

const form = reactive({ code: '' })
const rules = {
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 6, message: '验证码为6位数字', trigger: 'blur' }
  ]
}

const backupForm = reactive({ code: '' })

async function verify() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await auth.verifyTwoFactor(form.code)
    ElMessage.success('双因素认证成功')
    router.push('/dashboard')
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '验证码错误')
  } finally {
    loading.value = false
  }
}

async function verifyBackup() {
  if (!backupForm.code) {
    ElMessage.error('请输入备份码')
    return
  }

  loading.value = true
  try {
    await auth.verifyTwoFactor(backupForm.code)
    ElMessage.success('备份码验证成功')
    showBackup.value = false
    router.push('/dashboard')
  } catch (error) {
    ElMessage.error('备份码无效')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.two-factor-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.two-factor-card {
  width: 400px;
  padding: 40px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);

  h1 {
    text-align: center;
    font-size: 22px;
    margin-bottom: 8px;
    color: var(--el-text-color-primary);
  }

  .subtitle {
    text-align: center;
    font-size: 13px;
    color: #909399;
    margin-bottom: 24px;
  }
}
</style>
