<template>
  <div class="login-page">
    <div class="login-card">
      <h1 class="login-title">软件项目管理平台</h1>
      <p class="login-subtitle">NoStockHub</p>
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent="handleLogin">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" prefix-icon="User" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" prefix-icon="Lock" show-password />
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="form.remember">记住我</el-checkbox>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" class="login-btn" @click="handleLogin">
            登 录
          </el-button>
        </el-form-item>
      </el-form>
      <p class="register-link">没有账号？<el-link type="primary" @click="showRegister = true">立即注册</el-link></p>
      <el-divider style="margin: 16px 0" />
      <el-button type="warning" size="small" class="dev-btn" @click="devLogin">
        开发模式快速登录
      </el-button>
    </div>

    <el-dialog v-model="showRegister" title="用户注册" width="420px">
      <el-form :model="registerForm" :rules="registerRules" label-position="top">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="registerForm.username" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="registerForm.email" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="registerForm.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="registerForm.phone" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRegister = false">取消</el-button>
        <el-button type="primary" :loading="regLoading" @click="handleRegister">注册</el-button>
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
const regLoading = ref(false)
const showRegister = ref(false)

const form = reactive({ username: '', password: '', remember: false })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, min: 6, message: '密码至少6位', trigger: 'blur' }]
}

const registerForm = reactive({ username: '', email: '', password: '', phone: '' })
const registerRules = {
  username: [{ required: true, min: 3, message: '用户名至少3位', trigger: 'blur' }],
  email: [{ required: true, type: 'email', message: '请输入有效邮箱', trigger: 'blur' }],
  password: [{ required: true, min: 6, message: '密码至少6位', trigger: 'blur' }]
}

async function handleLogin() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    await auth.login(form.username, form.password)
    ElMessage.success('登录成功')
    router.push('/dashboard')
  } catch {
    ElMessage.error('用户名或密码错误')
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  try {
    await authAPI.register(registerForm)
    ElMessage.success('注册成功，请登录')
    showRegister.value = false
  } catch {
    ElMessage.error('注册失败')
  }
}

function devLogin() {
  localStorage.setItem('access_token', 'dev-mock-token')
  localStorage.setItem('refresh_token', 'dev-mock-refresh')
  auth.accessToken = 'dev-mock-token'
  auth.refreshToken = 'dev-mock-refresh'
  auth.user = { id: 'dev-1', username: '开发者', email: 'dev@test.com', role: 'admin' }
  ElMessage.success('开发模式登录成功')
  router.push('/dashboard')
}
</script>

<style scoped lang="scss">
.login-page {
  height: 100vh; display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.login-card {
  width: 400px; padding: 40px; background: #fff; border-radius: 12px; box-shadow: 0 20px 60px rgba(0,0,0,0.15);
}
.login-title { text-align: center; font-size: 22px; margin-bottom: 4px; color: #303133; }
.login-subtitle { text-align: center; font-size: 13px; color: #909399; margin-bottom: 28px; }
.login-btn { width: 100%; }
.register-link { text-align: center; font-size: 13px; color: #909399; margin-top: 12px; }
.dev-btn { width: 100%; }
</style>

<script>
import { authAPI } from '@/api'
export default {}
</script>
