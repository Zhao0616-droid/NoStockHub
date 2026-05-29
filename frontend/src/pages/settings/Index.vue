<template>
  <div class="settings-page">
    <h2 style="margin-bottom: 24px">系统设置</h2>

    <el-tabs type="border-card">
      <!-- 个人资料 -->
      <el-tab-pane label="个人资料">
        <div class="tab-content">
          <el-form :model="profile" label-width="100px" max-width="500px">
            <el-form-item label="用户名">
              <el-input v-model="profile.username" disabled />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="profile.email" placeholder="请输入邮箱" />
            </el-form-item>
            <el-form-item label="手机号">
              <el-input v-model="profile.phone" placeholder="请输入手机号" />
            </el-form-item>
            <el-form-item label="头像">
              <div style="display: flex; align-items: center; gap: 16px">
                <el-avatar :size="64" :src="profile.avatar" />
                <el-upload
                  :auto-upload="false"
                  accept="image/*"
                  :disabled="uploadingAvatar"
                  @change="handleAvatarChange"
                  style="flex: 1"
                >
                  <el-button type="primary" :loading="uploadingAvatar">
                    {{ uploadingAvatar ? '上传中...' : '选择图片' }}
                  </el-button>
                </el-upload>
              </div>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveProfile" :loading="saving">保存</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>

      <!-- 安全设置 -->
      <el-tab-pane label="安全设置">
        <div class="tab-content">
          <el-form label-width="120px" max-width="500px">
            <el-form-item label="修改密码">
              <el-button type="primary" @click="showPasswordDialog = true">修改密码</el-button>
            </el-form-item>
            <el-form-item label="双因素认证">
              <el-switch 
                v-model="twoFactorEnabled" 
                @change="handleTwoFactorChange"
                :loading="twoFactorLoading"
              />
              <span v-if="twoFactorEnabled" style="margin-left: 12px; color: #67c23a">已启用</span>
              <span v-else style="margin-left: 12px; color: #f56c6c">已禁用</span>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>

      <!-- 通知偏好 -->
      <el-tab-pane label="通知偏好">
        <div class="tab-content">
          <el-form label-width="100px" max-width="500px">
            <el-form-item label="通知类型">
              <el-checkbox-group v-model="notificationPrefs">
                <div class="notif-item">
                  <el-checkbox value="task_assigned">任务分配通知</el-checkbox>
                  <span class="notif-desc">当有新任务分配给我时通知</span>
                </div>
                <div class="notif-item">
                  <el-checkbox value="status_change">状态变更通知</el-checkbox>
                  <span class="notif-desc">当任务状态发生变更时通知</span>
                </div>
                <div class="notif-item">
                  <el-checkbox value="comment_mention">评论@提及通知</el-checkbox>
                  <span class="notif-desc">当评论中被@提及时通知</span>
                </div>
                <div class="notif-item">
                  <el-checkbox value="email_notification">邮件通知</el-checkbox>
                  <span class="notif-desc">启用邮件通知</span>
                </div>
              </el-checkbox-group>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveNotificationPrefs" :loading="saving">保存偏好</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>

      <!-- 主题设置 -->
      <el-tab-pane label="主题设置">
        <div class="tab-content">
          <el-form label-width="100px" max-width="500px">
            <el-form-item label="语言">
              <el-select v-model="language" placeholder="选择语言">
                <el-option label="简体中文" value="zh-CN" />
                <el-option label="English" value="en-US" />
              </el-select>
            </el-form-item>
            <el-form-item label="主题">
              <el-radio-group v-model="themeMode">
                <el-radio value="light">浅色主题</el-radio>
                <el-radio value="dark">深色主题</el-radio>
                <el-radio value="auto">跟随系统</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="字体大小">
              <el-slider v-model="fontSize" :min="12" :max="18" :step="1" style="width: 200px" />
              <span style="margin-left: 12px">{{ fontSize }}px</span>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveThemeSettings" :loading="saving">保存设置</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 修改密码对话框 -->
    <el-dialog 
      v-model="showPasswordDialog" 
      title="修改密码" 
      width="400px"
      :close-on-click-modal="false"
    >
      <el-form ref="passwordFormRef" :model="passwordForm" :rules="passwordRules" label-position="top">
        <el-form-item label="旧密码" prop="oldPassword">
          <el-input 
            v-model="passwordForm.oldPassword" 
            type="password" 
            show-password 
            placeholder="请输入旧密码"
          />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input 
            v-model="passwordForm.newPassword" 
            type="password" 
            show-password 
            placeholder="请输入新密码"
          />
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirmPassword">
          <el-input 
            v-model="passwordForm.confirmPassword" 
            type="password" 
            show-password 
            placeholder="再次输入新密码"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPasswordDialog = false">取消</el-button>
        <el-button type="primary" @click="changePassword" :loading="saving">确认修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { authAPI, notificationAPI, fileAPI } from '@/api'

function formatDRFErrors(data) {
  if (!data || typeof data !== 'object') return null
  return Object.values(data).flat().join('; ')
}

const auth = useAuthStore()
const themeStore = useThemeStore()
const saving = ref(false)
const twoFactorLoading = ref(false)
const showPasswordDialog = ref(false)

const profile = ref({
  username: '',
  email: '',
  phone: '',
  avatar: ''
})

const twoFactorEnabled = ref(false)
const notificationPrefs = ref(['task_assigned', 'status_change', 'comment_mention'])
const language = ref('zh-CN')
const themeMode = ref(themeStore.mode)
const fontSize = ref(14)

// --------------- 字体大小实时应用 ---------------
function applyFontSize(size) {
  document.documentElement.style.fontSize = size + 'px'
}
watch(fontSize, (val) => { applyFontSize(val) })

function applyLanguage(lang) {
  document.documentElement.lang = lang
}
watch(language, (val) => { applyLanguage(val) })

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const passwordRules = {
  oldPassword: [
    { required: true, message: '请输入旧密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请输入确认密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ]
}

// 初始化数据
onMounted(async () => {
  // 先从 localStorage 恢复并应用设置
  const saved = localStorage.getItem('theme_settings')
  if (saved) {
    try {
      const settings = JSON.parse(saved)
      language.value = settings.language || 'zh-CN'
      fontSize.value = settings.fontSize || 14
    } catch { /* ignore parse error */ }
  }
  applyFontSize(fontSize.value)
  applyLanguage(language.value)

  try {
    // 获取用户信息
    const userProfile = await authAPI.profile()
    Object.assign(profile.value, userProfile)
    twoFactorEnabled.value = userProfile.two_factor_enabled || false

    // 获取通知偏好
    const prefs = await notificationAPI.getNotificationPreferences()
    notificationPrefs.value = prefs.preferences || []

    // 获取主题设置
    themeMode.value = themeStore.mode
  } catch (error) {
    ElMessage.error('获取设置信息失败')
  }
})

// 保存个人资料
async function saveProfile() {
  saving.value = true
  try {
    await authAPI.updateProfile({
      email: profile.value.email,
      phone: profile.value.phone,
      avatar: profile.value.avatar
    })
    ElMessage.success('个人资料保存成功')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || formatDRFErrors(error.response?.data) || '保存失败')
  } finally {
    saving.value = false
  }
}

// 处理头像上传
const uploadingAvatar = ref(false)
async function handleAvatarChange(file) {
  uploadingAvatar.value = true
  try {
    const fd = new FormData()
    fd.append('file', file.raw)
    // 提取文件名作为 URL
    const filename = file.raw.name
    // 先显示本地预览
    const reader = new FileReader()
    reader.onload = (e) => { profile.value.avatar = e.target.result }
    reader.readAsDataURL(file.raw)
    // 上传到服务器
    const res = await fileAPI.upload(file.raw, null, null)
    // 从 file_path 提取 /media/uploads/<name>（兼容 Windows/Linux 路径分隔符）
    const fp = (res.file_path || '').replace(/\\/g, '/')
    const uploadsIdx = fp.lastIndexOf('uploads/')
    if (uploadsIdx !== -1) {
      profile.value.avatar = '/media/' + fp.slice(uploadsIdx)
    }
    ElMessage.success('头像上传成功')
  } catch (e) {
    ElMessage.error(formatDRFErrors(e.response?.data) || '头像上传失败')
  } finally {
    uploadingAvatar.value = false
  }
}

// 双因素认证切换
async function handleTwoFactorChange(enabled) {
  twoFactorLoading.value = true
  try {
    if (enabled) {
      await authAPI.enableTwoFactor()
      ElMessage.success('双因素认证已启用')
    } else {
      await authAPI.disableTwoFactor()
      ElMessage.success('双因素认证已禁用')
    }
  } catch (error) {
    twoFactorEnabled.value = !enabled
    ElMessage.error(error.response?.data?.message || '操作失败')
  } finally {
    twoFactorLoading.value = false
  }
}

// 保存通知偏好
async function saveNotificationPrefs() {
  saving.value = true
  try {
    await notificationAPI.updateNotificationPreferences({
      preferences: notificationPrefs.value
    })
    ElMessage.success('通知偏好已保存')
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '保存失败')
  } finally {
    saving.value = false
  }
}

// 保存主题设置
async function saveThemeSettings() {
  saving.value = true
  try {
    themeStore.setTheme(themeMode.value)
    applyFontSize(fontSize.value)
    applyLanguage(language.value)
    // 合并写入，避免覆盖 theme store 保存的 theme 字段
    let existing = {}
    try {
      const raw = localStorage.getItem('theme_settings')
      if (raw) existing = JSON.parse(raw)
    } catch { /* ignore */ }
    existing.language = language.value
    existing.fontSize = fontSize.value
    localStorage.setItem('theme_settings', JSON.stringify(existing))
    ElMessage.success('主题设置已保存')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 修改密码
async function changePassword() {
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    ElMessage.error('两次输入的密码不一致')
    return
  }
  
  saving.value = true
  try {
    await authAPI.changePassword({
      old_password: passwordForm.oldPassword,
      new_password: passwordForm.newPassword
    })
    ElMessage.success('密码修改成功')
    showPasswordDialog.value = false
    
    // 重置表单
    Object.assign(passwordForm, {
      oldPassword: '',
      newPassword: '',
      confirmPassword: ''
    })
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '密码修改失败')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped lang="scss">
.settings-page {
  padding: 20px;
  background: var(--app-main-bg);
  min-height: 100vh;
}

.tab-content {
  padding: 20px 0;
}

.notif-item {
  display: flex;
  align-items: center;
  padding: 12px 0;
  
  .notif-desc {
    margin-left: 12px;
    font-size: 12px;
    color: #909399;
  }
}

:deep(.el-form-item__content) {
  line-height: 1;
}
</style>
