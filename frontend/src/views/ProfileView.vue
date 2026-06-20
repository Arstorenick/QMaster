<template>
  <div class="profile-page">
    <div class="profile-container">
      <div class="profile-card card">
        <!-- Header row -->
        <div class="profile-top">
          <div class="profile-avatar">{{ (auth.user?.display_name || auth.user?.username || '?').charAt(0).toUpperCase() }}</div>
          <div class="profile-top-info">
            <h2>{{ auth.user?.display_name || auth.user?.username }}</h2>
          </div>
        </div>

        <!-- Form: single column -->
        <div class="profile-form">
          <div class="form-row">
            <label>账号</label>
            <input class="input" :value="auth.user?.username" disabled />
          </div>
          <div class="form-row">
            <label>用户名</label>
            <input v-model="form.display_name" class="input" placeholder="请输入姓名" />
          </div>
          <div class="form-row">
            <label>工号</label>
            <input v-model="form.employee_id" class="input" placeholder="请输入工号" />
          </div>
          <div class="form-row">
            <label>性别</label>
            <select v-model="form.gender" class="input">
              <option value="">未选择</option>
              <option value="male">男</option>
              <option value="female">女</option>
            </select>
          </div>
          <div class="form-row">
            <label>联系方式</label>
            <input v-model="form.phone" class="input" placeholder="手机号或邮箱" />
          </div>
          <div class="form-row">
            <label>所属部门</label>
            <div v-if="auth.isCreator" class="dept-select-btn" style="opacity:0.6;cursor:default">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/></svg>
              <span v-if="deptPath" class="dept-select-text">{{ deptPath }}</span>
              <span v-else class="dept-select-placeholder">未设置</span>
            </div>
            <div v-else class="dept-select-btn" @click="showDeptPicker = true">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/></svg>
              <span v-if="deptPath" class="dept-select-text">{{ deptPath }}</span>
              <span v-else class="dept-select-placeholder">点击选择部门</span>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m9 18 6-6-6-6"/></svg>
            </div>
            <small v-if="auth.isCreator" style="color:var(--color-text-tertiary)">管理员不能修改自己的所属部门</small>
          </div>
          <div class="form-row">
            <label>角色</label>
            <div class="dept-select-btn" style="opacity:0.6;cursor:default">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
              <span class="dept-select-text">{{ auth.user?.role_label }}</span>
            </div>
            <small v-if="auth.isCreator" style="color:var(--color-text-tertiary)">管理员不能修改自己的角色</small>
          </div>
        </div>

        <!-- Actions -->
        <p v-if="infoSaved" class="profile-success">✓ 信息已保存</p>
        <div class="profile-actions">
          <button class="btn btn-primary" @click="saveProfile" :disabled="saving">{{ saving ? '保存中...' : '保存' }}</button>
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
  const data = {
    display_name: form.display_name,
    employee_id: form.employee_id,
    phone: form.phone,
    gender: form.gender,
  }
  if (!auth.isCreator) data.department = form.department || null
  await profileAPI.update(data)
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
.profile-page {
  min-height: calc(100vh - var(--header-height));
  display: flex; align-items: center; justify-content: center;
  background: var(--color-bg);
  padding: var(--spacing-lg);
}
.profile-container { width: 100%; max-width: 420px; }

/* ── Header ── */
.profile-top { display: flex; align-items: center; gap: 14px; margin-bottom: var(--spacing-lg); }
.profile-avatar {
  width: 48px; height: 48px; border-radius: 50%;
  background: linear-gradient(135deg, #2563EB, #3B82F6);
  color: #fff; font-size: 20px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; box-shadow: 0 3px 12px rgba(37, 99, 235, 0.2);
}
.profile-top-info h2 { font-size: 20px; font-weight: 700; line-height: 1.2; }
.profile-meta { display: flex; align-items: center; gap: var(--spacing-sm); margin-top: 2px; }
.profile-role-tag {
  font-size: 12px; font-weight: 500;
  color: var(--color-primary); background: var(--color-primary-50);
  padding: 2px 10px; border-radius: 10px;
}
.profile-dept { font-size: 12px; color: var(--color-text-tertiary); }

/* ── Card + Form ── */
.profile-card { padding: var(--spacing-xl); border-radius: var(--radius-xl); }
.profile-form { display: flex; flex-direction: column; gap: var(--spacing-sm); }
.form-row { display: flex; flex-direction: column; gap: 3px; }
.form-row label { font-size: 13px; font-weight: 600; color: var(--color-text-primary); }

/* ── Actions ── */
.profile-actions { display: flex; gap: var(--spacing-sm); margin-top: var(--spacing-lg); }
.profile-success {
  font-size: 13px; font-weight: 500; color: var(--color-success);
  padding: 6px 12px; margin-top: var(--spacing-sm);
  background: #ECFDF5; border-radius: var(--radius-md);
  display: inline-block;
}

/* ── Department Select ── */
.dept-select-btn {
  display: flex; align-items: flex-start; gap: var(--spacing-sm);
  padding: 9px 12px; border: 1px solid var(--color-border);
  border-radius: var(--radius-md); cursor: pointer; font-size: 14px;
  transition: all 0.15s ease; background: var(--color-bg-white);
  min-height: 40px;
}
.dept-select-btn:hover { border-color: var(--color-primary); box-shadow: 0 0 0 3px var(--color-primary-100); }
.dept-select-text { flex: 1; min-width: 0; line-height: 1.4; word-break: break-all; }
.dept-select-placeholder { flex: 1; color: var(--color-text-tertiary); }
.dept-select-btn svg { flex-shrink: 0; opacity: 0.4; margin-top: 2px; }

/* ── Modals ── */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.3); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 200; }
.modal { width: 90%; max-width: 420px; padding: var(--spacing-xl); border-radius: var(--radius-xl); }
.modal h3 { font-size: 18px; font-weight: 700; }
.modal-actions { display: flex; justify-content: flex-end; gap: var(--spacing-sm); margin-top: var(--spacing-lg); }
.dept-picker-modal { max-width: 480px; max-height: 70vh; display: flex; flex-direction: column; }
.dept-breadcrumb { display: flex; align-items: center; gap: 4px; flex-wrap: wrap; margin-bottom: 14px; padding: 8px 0; border-bottom: 1px solid var(--color-border-light); }
.bread-item { font-size: 13px; color: var(--color-primary); cursor: pointer; padding: 4px 8px; border-radius: var(--radius-sm); font-weight: 500; }
.bread-item:hover { background: var(--color-primary-50); }
.bread-sep { color: var(--color-text-tertiary); font-size: 14px; }
.dept-list { flex: 1; overflow-y: auto; max-height: 320px; }
.dept-pick-grid { display: flex; flex-direction: column; gap: 2px; }
.dept-pick-item { display: flex; align-items: center; justify-content: space-between; padding: 11px 14px; border-radius: var(--radius-md); cursor: pointer; transition: all 0.15s; }
.dept-pick-item:hover { background: var(--color-bg-hover); }
.dept-pick-item.selected { background: var(--color-primary-light); color: var(--color-primary); font-weight: 600; }
.dept-pick-name { font-size: 14px; font-weight: 500; }
.dept-pick-arrow { font-size: 18px; color: var(--color-text-tertiary); }
</style>
