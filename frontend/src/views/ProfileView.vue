<template>
  <div class="profile-page">
    <div class="container" style="max-width:560px;margin:0 auto;padding:var(--spacing-xl)">
      <h2>个人信息</h2>

      <div class="card" style="padding:var(--spacing-xl);margin-top:var(--spacing-md)">
        <h4 style="margin-bottom:var(--spacing-md)">基本信息</h4>
        <div class="form-group">
          <label>账号</label>
          <input class="input" :value="auth.user?.username" disabled />
        </div>
        <div class="form-group">
          <label>用户名</label>
          <input v-model="form.display_name" class="input" placeholder="请输入姓名" />
        </div>
        <div class="form-group">
          <label>工号</label>
          <input v-model="form.employee_id" class="input" placeholder="请输入工号" />
        </div>
        <div class="form-group">
          <label>性别</label>
          <select v-model="form.gender" class="input">
            <option value="">未选择</option>
            <option value="male">男</option>
            <option value="female">女</option>
          </select>
        </div>
        <div class="form-group">
          <label>联系方式</label>
          <input v-model="form.phone" class="input" placeholder="手机号或邮箱" />
        </div>
        <div class="form-group">
          <label>所属部门</label>
          <div class="dept-select-btn" @click="showDeptPicker = true">
            <span v-if="deptPath">{{ deptPath }}</span>
            <span v-else class="text-secondary">点击选择部门</span>
            <span style="margin-left:auto">›</span>
          </div>
        </div>
        <div class="form-group">
          <label>角色</label>
          <input class="input" :value="auth.user?.role_label" disabled />
        </div>
        <p v-if="infoSaved" class="text-sm" style="color:var(--color-success)">已保存</p>
        <div class="form-actions">
          <button class="btn btn-primary" @click="saveProfile" :disabled="saving">
            {{ saving ? '保存中...' : '保存' }}
          </button>
          <button class="btn btn-secondary" @click="showPwdDialog = true">修改密码</button>
        </div>
      </div>
    </div>

    <!-- Department Picker Dialog -->
    <Teleport to="body">
      <div class="modal-overlay" v-if="showDeptPicker" @click.self="showDeptPicker = false">
        <div class="modal card dept-picker-modal">
          <h3 style="margin-bottom:12px">选择部门</h3>
          <!-- Breadcrumb -->
          <div class="dept-breadcrumb">
            <span class="bread-item" @click="deptNavTo(null)">全部</span>
            <template v-for="(b, i) in deptBreadcrumb" :key="b.id">
              <span class="bread-sep">›</span>
              <span class="bread-item" @click="deptNavTo(b, i)">{{ b.name }}</span>
            </template>
          </div>
          <!-- Department list -->
          <div class="dept-list">
            <div v-if="deptPickList.length" class="dept-pick-grid">
              <div
                v-for="d in deptPickList" :key="d.id"
                class="dept-pick-item"
                :class="{ selected: selectedDeptId === d.id }"
                @click="selectDeptLevel(d)"
              >
                <span class="dept-pick-name">{{ d.name }}</span>
                <span v-if="d.children?.length" class="dept-pick-arrow">›</span>
              </div>
            </div>
            <p v-else class="text-secondary text-sm text-center" style="padding:20px">无下级部门</p>
          </div>
          <div class="modal-actions">
            <button class="btn btn-ghost btn-sm" @click="clearDept">清除</button>
            <button class="btn btn-ghost" @click="showDeptPicker = false">取消</button>
            <button class="btn btn-primary" @click="confirmDept">确认</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Change Password Dialog -->
    <Teleport to="body">
      <div class="modal-overlay" v-if="showPwdDialog" @click.self="showPwdDialog = false">
        <div class="modal card">
          <h3>修改密码</h3>
          <div class="form-group">
            <label>当前密码</label>
            <input v-model="pwd.old_password" class="input" type="password" placeholder="输入当前密码" />
          </div>
          <div class="form-group">
            <label>新密码</label>
            <input v-model="pwd.new_password" class="input" type="password" placeholder="至少 6 位" />
          </div>
          <div class="form-group">
            <label>确认新密码</label>
            <input v-model="pwd.confirm_password" class="input" type="password" placeholder="再次输入新密码" />
          </div>
          <p v-if="pwdError" class="text-sm" style="color:var(--color-danger)">{{ pwdError }}</p>
          <p v-if="pwdSaved" class="text-sm" style="color:var(--color-success)">密码已修改</p>
          <div class="modal-actions">
            <button class="btn btn-ghost" @click="closePwdDialog">取消</button>
            <button class="btn btn-primary" @click="changePassword" :disabled="pwdSaving">
              {{ pwdSaving ? '修改中...' : '确认修改' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { profileAPI, departmentsAPI } from '../api'

const auth = useAuthStore()
const departmentTree = ref([])
const form = reactive({ display_name: '', employee_id: '', phone: '', gender: '', department: null })
const saving = ref(false)
const infoSaved = ref(false)

// Department picker
const showDeptPicker = ref(false)
const deptBreadcrumb = ref([])
const deptPickList = ref([])
const selectedDeptId = ref(null)
const selectedDeptPath = ref('')
const deptPath = ref('')

const showPwdDialog = ref(false)
const pwd = reactive({ old_password: '', new_password: '', confirm_password: '' })
const pwdSaving = ref(false)
const pwdSaved = ref(false)
const pwdError = ref('')

onMounted(async () => {
  form.display_name = auth.user?.display_name || ''
  form.employee_id = auth.user?.employee_id || ''
  form.phone = auth.user?.phone || ''
  form.gender = auth.user?.gender || ''
  form.department = auth.user?.department || null
  selectedDeptId.value = auth.user?.department || null
  deptPath.value = auth.user?.department_name || ''
  const { data } = await departmentsAPI.tree()
  departmentTree.value = data
  deptPickList.value = data
})

// ── Department picker ──
function selectDeptLevel(dept) {
  selectedDeptId.value = dept.id
  if (dept.children?.length) {
    deptBreadcrumb.value.push(dept)
    deptPickList.value = dept.children
  }
}

function deptNavTo(target, index) {
  if (!target) {
    deptBreadcrumb.value = []
    deptPickList.value = departmentTree.value
    return
  }
  deptBreadcrumb.value = deptBreadcrumb.value.slice(0, index + 1)
  deptPickList.value = target.children || []
}

function confirmDept() {
  showDeptPicker.value = false
  if (selectedDeptId.value) {
    form.department = selectedDeptId.value
    // Build full path
    const parts = deptBreadcrumb.value.map(b => b.name)
    if (parts.length) {
      const leaf = deptBreadcrumb.value[deptBreadcrumb.value.length - 1]
      if (leaf.children?.find(c => c.id === selectedDeptId.value)) {
        parts.push(deptPickList.value.find(d => d.id === selectedDeptId.value)?.name || '')
      }
    }
    if (!parts.length && selectedDeptId.value) {
      const found = departmentTree.value.find(d => d.id === selectedDeptId.value)
      if (found) parts.push(found.name)
    }
    deptPath.value = parts.join(' > ')
  }
}

function clearDept() {
  selectedDeptId.value = null
  deptPath.value = ''
  form.department = null
  deptBreadcrumb.value = []
  deptPickList.value = departmentTree.value
}

async function saveProfile() {
  saving.value = true; infoSaved.value = false
  await profileAPI.update({
    display_name: form.display_name,
    employee_id: form.employee_id,
    phone: form.phone,
    gender: form.gender,
    department: form.department || null,
  })
  await auth.fetchMe()
  saving.value = false; infoSaved.value = true
  setTimeout(() => infoSaved.value = false, 2000)
}

function closePwdDialog() {
  showPwdDialog.value = false
  pwd.old_password = ''; pwd.new_password = ''; pwd.confirm_password = ''
  pwdError.value = ''; pwdSaved.value = false
}

async function changePassword() {
  pwdError.value = ''; pwdSaved.value = false
  if (pwd.new_password.length < 6) { pwdError.value = '新密码至少 6 位'; return }
  if (pwd.new_password !== pwd.confirm_password) { pwdError.value = '两次输入的新密码不一致'; return }
  pwdSaving.value = true
  try {
    await profileAPI.changePassword({ old_password: pwd.old_password, new_password: pwd.new_password })
    pwdSaved.value = true
    setTimeout(closePwdDialog, 1500)
  } catch (e) {
    pwdError.value = e.response?.data?.old_password?.[0] || e.response?.data?.new_password?.[0] || '修改失败'
  }
  pwdSaving.value = false
}
</script>

<style scoped>
.form-group { margin-bottom: var(--spacing-md); }
.form-group label { display: block; font-size: var(--font-size-sm); font-weight: 500; margin-bottom: var(--spacing-xs); color: var(--color-text-primary); }
.form-actions { display: flex; gap: var(--spacing-sm); margin-top: var(--spacing-md); }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.3); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 200; }
.modal { width: 90%; max-width: 420px; padding: var(--spacing-xl); }
.modal-actions { display: flex; justify-content: flex-end; gap: var(--spacing-sm); margin-top: var(--spacing-lg); }
.dept-select-btn { display: flex; align-items: center; padding: 8px 14px; border: 1.5px solid var(--color-border); border-radius: var(--radius-md); cursor: pointer; font-size: var(--font-size-sm); transition: all var(--transition-fast); background: var(--color-bg-white); }
.dept-select-btn:hover { border-color: var(--color-primary); }
.dept-picker-modal { max-width: 480px; max-height: 70vh; display: flex; flex-direction: column; }
.dept-breadcrumb { display: flex; align-items: center; gap: 4px; flex-wrap: wrap; margin-bottom: 12px; padding: 8px 0; border-bottom: 1px solid var(--color-border-light); }
.bread-item { font-size: var(--font-size-sm); color: var(--color-primary); cursor: pointer; padding: 2px 6px; border-radius: var(--radius-sm); }
.bread-item:hover { background: var(--color-primary-light); }
.bread-sep { color: var(--color-text-tertiary); font-size: 14px; }
.dept-list { flex: 1; overflow-y: auto; max-height: 350px; }
.dept-pick-grid { display: flex; flex-direction: column; gap: 2px; }
.dept-pick-item { display: flex; align-items: center; justify-content: space-between; padding: 10px 12px; border-radius: var(--radius-md); cursor: pointer; transition: background var(--transition-fast); }
.dept-pick-item:hover { background: var(--color-bg-hover); }
.dept-pick-item.selected { background: var(--color-primary-light); color: var(--color-primary); }
.dept-pick-name { font-size: var(--font-size-sm); font-weight: 500; }
.dept-pick-arrow { font-size: 18px; color: var(--color-text-tertiary); }
</style>
