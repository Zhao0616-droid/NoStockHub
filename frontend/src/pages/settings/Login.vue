<template>
  <div class="login-page">
    <!-- 错误提示条 -->
    <el-alert v-if="errorMessage" title="登录失败" type="error" :closable="true" @close="errorMessage = ''" class="error-alert" />

    <div class="login-card">
      <h1 class="login-title">软件项目管理平台</h1>
      <p class="login-subtitle">NoStockHub</p>
      
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @keyup.enter="handleLogin">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" prefix-icon="User" clearable />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input 
            v-model="form.password" 
            type="password" 
            placeholder="请输入密码" 
            prefix-icon="Lock" 
            show-password 
            clearable 
          />
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="form.remember">记住我</el-checkbox>
        </el-form-item>
        <el-form-item>
          <el-button 
            type="primary" 
            size="large" 
            :loading="loading" 
            class="login-btn" 
            @click="handleLogin"
            style="width: 100%"
          >
            {{ loading ? '登录中...' : '登 录' }}
          </el-button>
        </el-form-item>
      </el-form>

      <p class="register-link">没有账号？<el-link type="primary" @click="showRegister = true">立即注册</el-link></p>
      <el-divider style="margin: 16px 0" />
      <el-button type="warning" size="small" class="dev-btn" @click="devLogin" style="width: 100%">
        开发模式快速登录（test/123456）
      </el-button>
    </div>

    <!-- 注册对话框 -->
    <el-dialog v-model="showRegister" title="用户注册" width="420px" :close-on-click-modal="false">
      <el-form ref="registerFormRef" :model="registerForm" :rules="registerRules" label-position="top">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="registerForm.username" placeholder="3-20个字符" clearable />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="registerForm.email" type="email" placeholder="请输入有效邮箱" clearable />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="registerForm.password" type="password" show-password placeholder="至少6位" clearable />
        </el-form-item>
        <el-form-item label="确认密码" prop="password2">
          <el-input v-model="registerForm.password2" type="password" show-password placeholder="再次输入密码" clearable />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="registerForm.phone" placeholder="可选" clearable />
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
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { authAPI } from '@/api'

const router = useRouter()
const auth = useAuthStore()

const formRef = ref()
const registerFormRef = ref()
const loading = ref(false)
const regLoading = ref(false)
const showRegister = ref(false)
const errorMessage = ref('')

const form = reactive({ username: '', password: '', remember: false })

onMounted(() => {
  const saved = localStorage.getItem('remember_username')
  if (saved) {
    form.username = saved
    form.remember = true
  }
})
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名3-20个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ]
}

const registerForm = reactive({ username: '', email: '', password: '', password2: '', phone: '' })
const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名3-20个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效邮箱', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  password2: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: (_rule, value, cb) => value !== registerForm.password ? cb(new Error('两次密码不一致')) : cb(), trigger: 'blur' }
  ]
}

async function handleLogin() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  errorMessage.value = ''
  loading.value = true
  
  try {
    await auth.login(form.username, form.password)
    ElMessage.success('登录成功')
    
    // 如果记住我，保存到localStorage
    if (form.remember) {
      localStorage.setItem('remember_username', form.username)
    } else {
      localStorage.removeItem('remember_username')
    }
    
    router.push('/dashboard')
  } catch (error) {
    const data = error.response?.data || {}
    const msg = data.detail || data.non_field_errors?.[0] || data.username?.[0] || data.password?.[0] || error.message || '用户名或密码错误'
    errorMessage.value = typeof msg === 'string' ? msg : JSON.stringify(msg)
    ElMessage.error(errorMessage.value)
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  const valid = await registerFormRef.value.validate().catch(() => false)
  if (!valid) return
  
  regLoading.value = true
  try {
    await authAPI.register(registerForm)
    ElMessage.success('注册成功，请登录')
    showRegister.value = false
    registerForm.username = ''
    registerForm.email = ''
    registerForm.password = ''
    registerForm.phone = ''
  } catch (error) {
    const data = error.response?.data || {}
    const msg = data.detail || data.password?.[0] || data.username?.[0] || data.email?.[0] || data.non_field_errors?.[0] || '注册失败'
    ElMessage.error(typeof msg === 'string' ? msg : JSON.stringify(msg))
  } finally {
    regLoading.value = false
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
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
}

.error-alert {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 90%;
  max-width: 500px;
  z-index: 2000;
}

.login-card {
  width: 400px;
  padding: 40px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.login-title {
  text-align: center;
  font-size: 22px;
  font-weight: bold;
  margin-bottom: 4px;
  color: #303133;
}

.login-subtitle {
  text-align: center;
  font-size: 13px;
  color: #909399;
  margin-bottom: 28px;
}

.register-link {
  text-align: center;
  font-size: 13px;
  color: #909399;
  margin-top: 12px;
  margin-bottom: 0;
}
</style>
