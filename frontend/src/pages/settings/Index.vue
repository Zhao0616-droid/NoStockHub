<template>
  <div class="settings-page">
    <h2>系统设置</h2>

    <el-row :gutter="16">
      <el-col :span="12">
        <!-- 个人资料 -->
        <el-card header="个人资料">
          <el-form :model="profile" label-width="80px">
            <el-form-item label="用户名">
              <el-input v-model="profile.username" disabled />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="profile.email" />
            </el-form-item>
            <el-form-item label="手机号">
              <el-input v-model="profile.phone" />
            </el-form-item>
            <el-form-item label="头像">
              <el-upload action="#" :show-file-list="false">
                <el-avatar :size="64" :src="profile.avatar" />
              </el-upload>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveProfile">保存</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="12">
        <!-- 安全设置 -->
        <el-card header="安全设置" style="margin-bottom:16px">
          <el-form label-width="100px">
            <el-form-item label="修改密码">
              <el-button text type="primary" @click="showPassword = true">修改</el-button>
            </el-form-item>
            <el-form-item label="双因素认证">
              <el-switch v-model="twoFA" />
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 通知偏好 -->
        <el-card header="通知偏好">
          <el-checkbox-group v-model="notifPrefs">
            <div class="notif-item"><el-checkbox value="task_assigned" label="任务分配通知" /></div>
            <div class="notif-item"><el-checkbox value="status_change" label="状态变更通知" /></div>
            <div class="notif-item"><el-checkbox value="comment" label="评论@提及通知" /></div>
            <div class="notif-item"><el-checkbox value="email" label="邮件通知" /></div>
          </el-checkbox-group>
        </el-card>
      </el-col>
    </el-row>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="showPassword" title="修改密码" width="400px">
      <el-form :model="passwordForm" label-position="top">
        <el-form-item label="旧密码">
          <el-input v-model="passwordForm.old" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="passwordForm.new1" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认新密码">
          <el-input v-model="passwordForm.new2" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPassword = false">取消</el-button>
        <el-button type="primary" @click="changePassword">确认修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const profile = ref({
  username: 'zhangsan', email: 'zhangsan@example.com', phone: '13800138000', avatar: ''
})
const twoFA = ref(false)
const notifPrefs = ref(['task_assigned', 'status_change', 'comment'])
const showPassword = ref(false)
const passwordForm = ref({ old: '', new1: '', new2: '' })

function saveProfile() { ElMessage.success('保存成功') }
function changePassword() { ElMessage.success('密码修改成功'); showPassword.value = false }
</script>

<style scoped lang="scss">
.notif-item { padding: 4px 0; }
</style>
