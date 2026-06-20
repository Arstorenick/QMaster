<template>
  <div class="dept-page">
    <div class="dept-layout">
      <!-- Left: Tree -->
      <aside class="dept-sidebar">
        <div class="dept-sidebar-header">
          <h3>组织架构</h3>
          <div class="dept-sidebar-actions">
            <button class="btn btn-primary btn-sm" @click="showCreate = true" v-if="auth.isCreator">+ 新建</button>
            <button class="btn btn-secondary btn-sm" @click="activeTab = 'import'" v-if="auth.isCreator">导入</button>
          </div>
        </div>
        <div class="dept-search-wrap">
          <svg class="dept-search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
          <input v-model="search" class="input dept-search-input" placeholder="搜索部门..." />
        </div>
        <div class="dept-tree" v-if="filteredTree.length">
          <DeptNode
            v-for="dept in filteredTree" :key="dept.id"
            :dept="dept" :level="0"
            :active-id="activeDept?.id" :search="search"
            @select="selectDept" @delete="handleDelete"
          />
        </div>
        <div v-else class="dept-sidebar-empty">
          <p class="text-secondary text-sm">{{ departments.length ? '无匹配部门' : '暂无部门' }}</p>
        </div>
      </aside>

      <!-- Right: Content -->
      <section class="dept-main">
        <template v-if="activeTab === 'import'">
          <div class="import-page">
            <div class="dept-detail-header">
              <h2>批量导入</h2>
              <button class="btn btn-ghost btn-sm" @click="activeTab = 'detail'">← 返回</button>
            </div>

            <div class="import-content">
              <!-- Step 1: Choose type -->
              <div class="import-card card">
                <div class="import-step"><span class="step-num">1</span> 选择导入类型</div>
                <div class="import-type-tabs">
                  <button :class="['import-type-btn', { active: importType === 'department' }]" @click="importType = 'department'">
                    <img :src="deptImg" alt="dept" class="import-type-img" />
                    <span>导入部门</span>
                  </button>
                  <button :class="['import-type-btn', { active: importType === 'user' }]" @click="importType = 'user'">
                    <span class="type-icon">👤</span>
                    <span>导入用户</span>
                  </button>
                </div>
              </div>

              <!-- Step 2: Upload / Paste -->
              <div class="import-card card">
                <div class="import-step"><span class="step-num">2</span> 上传 CSV 文件或粘贴内容</div>
                <div class="import-format">
                  <template v-if="importType === 'department'">
                    <p><strong>格式：</strong><code>部门名称,上级部门完整路径</code></p>
                    <p class="text-secondary text-sm">上级部门留空则为顶级部门，路径如：<code>沈阳公司 > 和平区分公司</code></p>
                  </template>
                  <template v-else>
                    <p><strong>格式：</strong><code>用户名,密码,角色编号,部门完整路径</code></p>
                    <p class="text-secondary text-sm">角色编号：1=总管理 2=管理员 3=用户 4=部门负责人</p>
                  </template>
                </div>

                <!-- Drag & Drop -->
                <div
                  class="import-dropzone"
                  :class="{ dragover: dragOver }"
                  @dragover.prevent="dragOver = true"
                  @dragleave="dragOver = false"
                  @drop.prevent="onDrop"
                >
                  <input type="file" accept=".csv" @change="handleFileUpload" ref="fileInput" style="display:none" />
                  <p class="drop-text">{{ csvText ? '已加载文件' : '拖拽 CSV 文件到此处' }}</p>
                  <button class="btn btn-secondary btn-sm" @click="$refs.fileInput.click()" v-if="!csvText">或点击选择文件</button>
                  <button class="btn btn-ghost btn-sm" @click="csvText = ''; importResult = null" v-else>清除</button>
                </div>

                <div class="form-group" style="margin-top:12px">
                  <label>或直接粘贴内容</label>
                  <textarea v-model="csvText" class="input" rows="6" :placeholder="importType === 'department' ? '总部\n华东分公司,总部\n华南分公司,总部' : 'zhangsan,123456,2,总部\nlisi,123456,3,华东分公司'"></textarea>
                </div>

                <!-- Preview -->
                <div v-if="csvText" class="import-preview">
                  <div class="flex items-center justify-between" style="margin-bottom:8px">
                    <span class="text-sm" style="font-weight:600">数据预览</span>
                    <span class="text-sm text-secondary">{{ previewRows.length }} 行</span>
                  </div>
                  <div class="preview-table-wrap">
                    <table class="table" style="font-size:12px">
                      <thead>
                        <tr v-if="importType === 'department'"><th>部门名称</th><th>上级部门</th></tr>
                        <tr v-else><th>用户名</th><th>密码</th><th>角色</th><th>部门路径</th></tr>
                      </thead>
                      <tbody>
                        <tr v-for="(row, i) in previewRows" :key="i">
                          <td v-for="(cell, j) in row" :key="j">{{ cell }}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>

              <!-- Step 3: Execute -->
              <div class="import-card card">
                <div class="import-step"><span class="step-num">3</span> 开始导入</div>
                <button class="btn btn-primary" @click="doImport" :disabled="!csvText.trim() || importing">
                  {{ importing ? '导入中...' : `导入 ${previewRows.length} 条` }}
                </button>
                <div v-if="importResult" class="import-result">
                  <div class="result-success" v-if="importResult.created?.length">
                    ✅ 成功 <strong>{{ importResult.total }}</strong> 条
                  </div>
                  <div class="result-errors" v-if="importResult.errors?.length">
                    <p style="color:var(--color-danger);margin-bottom:4px">❌ {{ importResult.errors.length }} 条失败：</p>
                    <ul class="error-list">
                      <li v-for="(e, i) in importResult.errors" :key="i">{{ e }}</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>

        <template v-else-if="activeTab === 'dashboard'">
          <div class="dept-detail-header">
            <h2>部门统计看板</h2>
            <button class="btn btn-ghost" @click="activeTab = 'detail'">← 返回</button>
          </div>
          <div class="dashboard-content">
            <div class="dept-stats-row">
              <div class="dashboard-stat">
                <div class="dashboard-stat-icon dsi-blue">
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 22c0-4.4 3.6-8 8-8s8 3.6 8 8"/></svg>
                </div>
                <div class="dashboard-stat-info">
                  <span class="dashboard-stat-num">{{ dashboard.total_users }}</span>
                  <span class="dashboard-stat-label">总用户数</span>
                </div>
              </div>
              <div class="dashboard-stat">
                <div class="dashboard-stat-icon dsi-green">
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                </div>
                <div class="dashboard-stat-info">
                  <span class="dashboard-stat-num">{{ dashboard.total_surveys }}</span>
                  <span class="dashboard-stat-label">总问卷数</span>
                </div>
              </div>
              <div class="dashboard-stat">
                <div class="dashboard-stat-icon dsi-purple">
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
                </div>
                <div class="dashboard-stat-info">
                  <span class="dashboard-stat-num">{{ dashboard.total_submissions }}</span>
                  <span class="dashboard-stat-label">总提交数</span>
                </div>
              </div>
            </div>
            <div class="card dashboard-table-card">
              <h4>各部门概览</h4>
              <table class="table">
                <thead><tr><th>部门</th><th>成员数</th><th>提交数</th><th>子部门数</th></tr></thead>
                <tbody><tr v-for="d in dashboard.departments" :key="d.id"><td><strong>{{ d.name }}</strong></td><td><span class="tag tag-primary">{{ d.member_count }} 人</span></td><td>{{ d.submission_count }} 份</td><td>{{ d.children_count }}</td></tr></tbody>
              </table>
            </div>
          </div>
        </template>

        <template v-else>
          <template v-if="activeDept">
            <div class="dept-detail-header">
              <div>
                <div class="flex items-center gap-sm"><h2>{{ activeDept.name }}</h2><span class="tag tag-primary">{{ activeMembers.length }} 人</span></div>
                <p class="text-secondary text-sm mt-sm">{{ activeDept.full_path }}</p>
              </div>
              <div class="flex items-center gap-sm">
                <button class="btn btn-secondary btn-sm" @click="loadDashboard">看板</button>
                <button class="btn btn-secondary btn-sm" @click="exportMembers">导出CSV</button>
              </div>
            </div>
            <div class="card" style="padding:var(--spacing-xl);margin:0 var(--spacing-xl) var(--spacing-xl);border-radius:var(--radius-xl)">
              <div class="members-card-header">
                <div class="members-header-left">
                  <h4>部门成员</h4>
                  <span class="members-count">{{ activeMembers.length }} 人</span>
                </div>
                <div class="members-search">
                  <svg class="members-search-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
                  <input v-model="memberSearch" class="input members-search-input" placeholder="搜索成员..." />
                </div>
              </div>
              <!-- Bulk action bar -->
              <div v-if="auth.isCreator" class="bulk-bar" :class="{ active: selectedMemberIds.length > 0 }">
                <div class="bulk-bar-left">
                  <div class="bulk-count">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 00-4-4H6a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75"/></svg>
                    <span v-if="selectedMemberIds.length"><strong>{{ selectedMemberIds.length }}</strong> 人已选</span>
                    <span v-else class="text-secondary">勾选成员进行批量操作</span>
                  </div>
                </div>
                <div class="bulk-bar-right">
                  <div class="bulk-field">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                    <select v-model="bulkRole" class="bulk-select">
                      <option value="">变更角色</option>
                      <option :value="2">设为管理员</option>
                      <option :value="3">设为用户</option>
                    </select>
                  </div>
                  <div class="bulk-field">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/></svg>
                    <select v-model="bulkDept" class="bulk-select" style="min-width:160px">
                      <option value="">变更部门</option>
                      <option v-for="d in flatDepts" :key="d.id" :value="d.id">{{ d.full_path }}</option>
                    </select>
                  </div>
                  <button class="bulk-btn bulk-btn-primary" @click="applyBulk" :disabled="(!bulkRole && !bulkDept) || !selectedMemberIds.length || bulkSaving">
                    <svg v-if="!bulkSaving" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
                    {{ bulkSaving ? '执行中...' : '应用' }}
                  </button>
                </div>
              </div>

              <table class="table" v-if="filteredMembers.length">
                <thead><tr>
                  <th v-if="auth.isCreator" style="width:40px"><input type="checkbox" :checked="allSelected" @change="toggleSelectAll" /></th>
                  <th>账号</th><th>用户名</th><th>工号</th><th>联系方式</th><th>所属部门</th><th>角色</th><th v-if="auth.isCreator">操作</th>
                </tr></thead>
                <tbody>
                  <tr v-for="m in filteredMembers" :key="m.id" :class="{ rowSelected: selectedMemberIds.includes(m.id) }">
                    <td v-if="auth.isCreator">
                      <input type="checkbox" :checked="selectedMemberIds.includes(m.id)" @change="toggleMemberSelect(m.id)" />
                    </td>
                    <td><strong>{{ m.username }}</strong></td>
                    <td>{{ m.display_name || '-' }}</td>
                    <td class="text-secondary text-sm">{{ m.employee_id || '-' }}</td>
                    <td class="text-secondary text-sm">{{ m.phone || '-' }}</td>
                    <td class="text-secondary text-sm">{{ shortDeptName(m.department_name) }}</td>
                    <td><span class="tag" :class="m.role === 1 ? 'tag-primary' : m.role === 2 ? 'tag-success' : 'tag-warning'">{{ m.role_label }}</span></td>
                    <td v-if="auth.isCreator">
                      <button class="btn btn-ghost btn-sm" @click="openEditMember(m)">✎</button>
                    </td>
                  </tr>
                </tbody>
              </table>
              <p v-else class="text-secondary text-sm text-center" style="padding:var(--spacing-xl)">暂无成员</p>
            </div>
          </template>
          <div v-else class="dept-empty text-center">
            <img :src="deptImg" alt="dept" style="width:100px;height:100px;object-fit:contain;margin:0 auto 16px;display:block" />
            <h3>选择左侧部门查看</h3>
          </div>
        </template>
      </section>
    </div>

    <!-- Create Dialog -->
    <Teleport to="body">
      <div class="modal-overlay" v-if="showCreate" @click.self="showCreate = false">
        <div class="modal card">
          <h3>新建部门</h3>
          <div class="form-group"><label>部门名称</label><input v-model="newName" class="input" /></div>
          <div class="form-group"><label>上级部门</label><select v-model="newParent" class="input"><option :value="null">无</option><option v-for="d in flatDepts" :key="d.id" :value="d.id">{{ d.full_path }}</option></select></div>
          <div class="modal-actions"><button class="btn btn-ghost" @click="showCreate = false">取消</button><button class="btn btn-primary" @click="createDept" :disabled="!newName.trim()">创建</button></div>
        </div>
      </div>
    </Teleport>

    <!-- Edit Member Dialog -->
    <Teleport to="body">
      <div class="modal-overlay" v-if="showEditMember" @click.self="showEditMember = false">
        <div class="modal card" style="max-width:440px">
          <h3>编辑成员信息</h3>
          <p class="text-sm text-secondary" style="margin-bottom:16px">{{ editMemberForm.username }}</p>
          <div class="form-group"><label>用户名</label><input v-model="editMemberForm.display_name" class="input" placeholder="姓名" /></div>
          <div class="form-group"><label>工号</label><input v-model="editMemberForm.employee_id" class="input" placeholder="工号" /></div>
          <div class="form-group"><label>联系方式</label><input v-model="editMemberForm.phone" class="input" placeholder="手机号或邮箱" /></div>
          <div class="form-group"><label>所属部门</label>
            <select v-model="editMemberForm.department" class="input" :disabled="editMemberForm.id === auth.user?.id">
              <option :value="null">不修改</option>
              <option v-for="d in flatDepts" :key="d.id" :value="d.id">{{ d.full_path }}</option>
            </select>
            <small v-if="editMemberForm.id === auth.user?.id" style="color:var(--color-text-tertiary)">不能修改自己的所属部门</small>
          </div>
          <div class="form-group" v-if="auth.isCreator">
            <label>角色</label>
            <select v-model="editMemberForm.role" class="input" :disabled="editMemberForm.id === auth.user?.id">
              <option :value="2">管理员</option>
              <option :value="3">用户</option>
            </select>
            <small v-if="editMemberForm.id === auth.user?.id" style="color:var(--color-text-tertiary)">不能修改自己的角色</small>
          </div>
          <div class="form-group" v-if="auth.isCreator && editMemberForm.role === 2 && flatDepts.length">
            <label>管理部门</label>
            <select v-model="editMemberForm.managed_department" class="input" :disabled="editMemberForm.id === auth.user?.id">
              <option :value="null">默认（其所属部门）</option>
              <option v-for="d in flatDepts" :key="d.id" :value="d.id">{{ d.full_path }}</option>
            </select>
            <small v-if="editMemberForm.id === auth.user?.id" style="color:var(--color-text-tertiary)">不能修改自己的管理部门</small>
            <small v-else style="color:var(--color-text-tertiary)">该管理员只能管理所选部门及其子部门</small>
          </div>
          <p v-if="editMemberMsg" class="text-sm" :style="{ color: editMemberMsg === '保存成功' ? 'var(--color-success)' : 'var(--color-danger)' }">{{ editMemberMsg }}</p>
          <div class="modal-actions">
            <button class="btn btn-ghost" @click="showEditMember = false">取消</button>
            <button class="btn btn-primary" @click="saveEditMember" :disabled="editMemberSaving">{{ editMemberSaving ? '保存中...' : '保存' }}</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { departmentsAPI } from '../api'
import deptImg from '../assets/departments.png'
import DeptNode from '../components/common/DeptNode.vue'

const auth = useAuthStore()
const departments = ref([])
const flatDepts = ref([])
const activeDept = ref(null)
const activeMembers = ref([])
const search = ref('')
const memberSearch = ref('')
const activeTab = ref('detail')
const showCreate = ref(false)
const newName = ref('')
const newParent = ref(null)

const importType = ref('department')
const csvText = ref('')
const importing = ref(false)
const importResult = ref(null)
const dragOver = ref(false)

const previewRows = computed(() => {
  if (!csvText.value.trim()) return []
  return csvText.value.trim().split('\n').map(line => line.split(',').map(c => c.trim())).filter(r => r[0])
})

const dashboard = ref({ total_users: 0, total_surveys: 0, total_submissions: 0, departments: [] })

const showEditMember = ref(false)
const editMemberForm = reactive({ id: null, username: '', display_name: '', employee_id: '', phone: '', role: 3, department: null, managed_department: null })
const editMemberSaving = ref(false)
const editMemberMsg = ref('')

const selectedMemberIds = ref([])
const bulkRole = ref('')
const bulkDept = ref('')
const bulkSaving = ref(false)

const allSelected = computed(() => {
  return filteredMembers.value.length > 0 && filteredMembers.value.every(m => selectedMemberIds.value.includes(m.id))
})

function toggleMemberSelect(id) {
  const idx = selectedMemberIds.value.indexOf(id)
  if (idx > -1) selectedMemberIds.value.splice(idx, 1)
  else selectedMemberIds.value.push(id)
}

function toggleSelectAll() {
  if (allSelected.value) {
    selectedMemberIds.value = []
  } else {
    selectedMemberIds.value = filteredMembers.value.map(m => m.id)
  }
}

async function applyBulk() {
  if (!selectedMemberIds.value.length) return
  bulkSaving.value = true
  try {
    if (bulkRole.value) {
      await departmentsAPI.bulkUpdateRole(selectedMemberIds.value, bulkRole.value)
    }
    if (bulkDept.value) {
      await departmentsAPI.bulkUpdateDept(selectedMemberIds.value, bulkDept.value)
    }
    selectedMemberIds.value = []
    bulkRole.value = ''
    bulkDept.value = ''
    if (activeDept.value) {
      const { data } = await departmentsAPI.get(activeDept.value.id)
      activeMembers.value = data.members || []
    }
  } catch (e) {
    alert('操作失败')
  }
  bulkSaving.value = false
}

onMounted(loadData)

async function loadData() {
  const [treeRes, flatRes] = await Promise.all([
    departmentsAPI.tree(), departmentsAPI.flat(),
  ])
  departments.value = treeRes.data
  flatDepts.value = flatRes.data
  // Load dashboard on demand
}

async function selectDept(dept) {
  activeDept.value = dept
  activeTab.value = 'detail'
  memberSearch.value = ''
  const { data } = await departmentsAPI.get(dept.id)
  activeMembers.value = data.members || []
}

async function createDept() {
  await departmentsAPI.create({ name: newName.value.trim(), parent: newParent.value || null })
  showCreate.value = false; newName.value = ''; newParent.value = null
  await loadData()
}

async function handleDelete(id) {
  if (!confirm('确定删除？')) return
  await departmentsAPI.delete(id)
  if (activeDept.value?.id === id) activeDept.value = null
  await loadData()
}

const filteredTree = computed(() => {
  if (!search.value) return departments.value
  const kw = search.value.toLowerCase()
  function filter(list) {
    const result = []
    for (const d of list) {
      const match = d.name.toLowerCase().includes(kw) || d.full_path.toLowerCase().includes(kw)
      const filteredChildren = d.children ? filter(d.children) : []
      if (match || filteredChildren.length) result.push({ ...d, children: filteredChildren })
    }
    return result
  }
  return filter(departments.value)
})

const filteredMembers = computed(() => {
  if (!memberSearch.value) return activeMembers.value
  const kw = memberSearch.value.toLowerCase()
  return activeMembers.value.filter(m => m.username.toLowerCase().includes(kw))
})

function onDrop(e) {
  dragOver.value = false
  const file = e.dataTransfer.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (ev) => { csvText.value = ev.target.result; importResult.value = null }
  reader.readAsText(file)
}

function handleFileUpload(e) {
  const file = e.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (ev) => { csvText.value = ev.target.result; importResult.value = null }
  reader.readAsText(file)
}

async function doImport() {
  importing.value = true; importResult.value = null
  const { data } = await departmentsAPI.import({ csv: csvText.value, type: importType.value })
  importResult.value = data; importing.value = false
  await loadData()
}

function exportMembers() {
  if (!activeMembers.value.length) return
  const csv = ['用户名,角色,邮箱,加入时间']
  for (const m of activeMembers.value) csv.push(`${m.username},${m.role_label},${m.email || ''},${m.date_joined?.slice(0, 10)}`)
  const blob = new Blob(['﻿' + csv.join('\n')], { type: 'text/csv;charset=utf-8' })
  const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = `${activeDept.value?.name}_成员.csv`; a.click()
}

function shortDeptName(fullPath) {
  if (!fullPath) return '-'
  const parts = fullPath.split(' > ')
  return parts[parts.length - 1]
}

function openEditMember(m) {
  editMemberForm.id = m.id
  editMemberForm.username = m.username
  editMemberForm.display_name = m.display_name || ''
  editMemberForm.employee_id = m.employee_id || ''
  editMemberForm.phone = m.phone || ''
  editMemberForm.role = m.role
  editMemberForm.department = m.department_id || null
  editMemberForm.managed_department = m.managed_department || null
  editMemberMsg.value = ''
  showEditMember.value = true
}

async function saveEditMember() {
  editMemberSaving.value = true
  editMemberMsg.value = ''
  try {
    const payload = {
      display_name: editMemberForm.display_name,
      employee_id: editMemberForm.employee_id,
      phone: editMemberForm.phone,
      department: editMemberForm.department || null,
    }
    if (auth.isCreator && editMemberForm.id !== auth.user?.id) {
      payload.role = editMemberForm.role
      payload.managed_department = editMemberForm.managed_department || null
    }
    await departmentsAPI.updateUser(editMemberForm.id, payload)
    editMemberMsg.value = '保存成功'
    // Refresh member list
    if (activeDept.value) {
      const { data } = await departmentsAPI.get(activeDept.value.id)
      activeMembers.value = data.members || []
    }
    setTimeout(() => { showEditMember.value = false; editMemberMsg.value = '' }, 800)
  } catch (e) {
    editMemberMsg.value = '保存失败'
  }
  editMemberSaving.value = false
}

async function loadDashboard() {
  activeTab.value = 'dashboard'
  const { data } = await departmentsAPI.dashboard()
  dashboard.value = data
}
</script>

<style scoped>
.dept-page { height: calc(100vh - var(--header-height)); }
.dept-layout { display: flex; height: 100%; }

/* ── Sidebar ── */
.dept-sidebar {
  width: var(--sidebar-width); flex-shrink: 0;
  border-right: 1px solid var(--color-border-light);
  background: var(--color-bg); display: flex; flex-direction: column;
}
.dept-sidebar-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: var(--spacing-lg) var(--spacing-md) var(--spacing-sm);
}
.dept-sidebar-header h3 { font-size: 16px; font-weight: 700; }
.dept-sidebar-actions { display: flex; gap: 6px; }
.dept-search-wrap { position: relative; padding: 0 var(--spacing-md); margin-bottom: var(--spacing-sm); }
.dept-search-icon {
  position: absolute; left: 28px; top: 50%; transform: translateY(-50%);
  color: var(--color-text-tertiary); pointer-events: none;
}
.dept-search-input { padding-left: 34px !important; width: 100% !important; }
.dept-tree { flex: 1; overflow-y: auto; padding: 4px 0 var(--spacing-md); }
.dept-sidebar-empty { text-align: center; padding: var(--spacing-xl); }

/* ── Main ── */
.dept-main { flex: 1; overflow-y: auto; background: var(--color-bg-white); }
.dept-detail-header {
  display: flex; align-items: flex-start; justify-content: space-between;
  padding: var(--spacing-xl); border-bottom: 1px solid var(--color-border-light);
}
.dept-detail-header h2 { font-size: 22px; font-weight: 700; }
.dept-empty {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; height: 100%;
}
.dept-empty h3 { font-size: 18px; font-weight: 600; color: var(--color-text-primary); margin-top: 16px; }
.form-group { margin-bottom: var(--spacing-md); }
.form-group label { display: block; font-size: var(--font-size-sm); font-weight: 500; margin-bottom: 4px; color: var(--color-text-primary); }

/* ── Modal ── */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.3); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 200; }
.modal { width: 90%; max-width: 480px; padding: var(--spacing-xl); border-radius: var(--radius-xl); }
.modal-actions { display: flex; justify-content: flex-end; gap: var(--spacing-sm); margin-top: var(--spacing-lg); }

/* ── Member Card ── */
.dept-main :deep(.card) { margin: 0 var(--spacing-xl) var(--spacing-xl); padding: var(--spacing-xl); border-radius: var(--radius-xl); }
.dept-main :deep(.table) { font-size: 13px; }
.dept-main :deep(.table th) { font-size: 11px; letter-spacing: 0.03em; padding: 10px 12px; }

/* ── Members Table Header ── */
.members-card-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--spacing-lg); flex-wrap: wrap; gap: var(--spacing-md); }
.members-header-left { display: flex; align-items: center; gap: var(--spacing-sm); }
.members-header-left h4 { font-size: 17px; font-weight: 700; }
.members-count { font-size: 13px; color: var(--color-primary); background: var(--color-primary-50); padding: 3px 12px; border-radius: 12px; font-weight: 600; }
.members-search { position: relative; }
.members-search-icon { position: absolute; left: 10px; top: 50%; transform: translateY(-50%); color: var(--color-text-tertiary); pointer-events: none; }
.members-search-input { padding-left: 32px !important; width: 200px; }
.bulk-bar {
  display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap;
  gap: var(--spacing-md); padding: 12px 18px; margin-bottom: var(--spacing-md);
  background: var(--color-bg-white); border: 1px solid var(--color-primary-100);
  border-radius: var(--radius-lg);
  box-shadow: 0 2px 12px rgba(37, 99, 235, 0.08);
}
.bulk-bar-left { display: flex; align-items: center; }
.bulk-count { display: flex; align-items: center; gap: 8px; font-size: 14px; color: var(--color-primary); }
.bulk-count svg { flex-shrink: 0; }
.bulk-bar-right { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.bulk-field { display: flex; align-items: center; gap: 6px; }
.bulk-field svg { flex-shrink: 0; color: var(--color-text-tertiary); }
.bulk-select {
  padding: 7px 28px 7px 10px; border: 1px solid var(--color-border);
  border-radius: var(--radius-md); font-size: 13px; font-family: var(--font-family);
  color: var(--color-text-primary); background: var(--color-bg-white);
  cursor: pointer; outline: none;
  appearance: none; -webkit-appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg width='8' height='5' viewBox='0 0 8 5' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1l3 3 3-3' stroke='%23666' stroke-width='1.2' fill='none'/%3E%3C/svg%3E");
  background-repeat: no-repeat; background-position: right 10px center;
  transition: border-color 0.15s;
}
.bulk-select:hover { border-color: var(--color-primary-200); }
.bulk-select:focus { border-color: var(--color-primary); box-shadow: 0 0 0 2px var(--color-primary-100); }
.bulk-btn {
  display: flex; align-items: center; gap: 5px;
  padding: 7px 16px; border: none; border-radius: var(--radius-md);
  font-size: 13px; font-weight: 600; font-family: var(--font-family);
  cursor: pointer; transition: all 0.15s ease; white-space: nowrap;
}
.bulk-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.bulk-btn-primary { background: var(--color-primary); color: #fff; }
.bulk-btn-primary:hover:not(:disabled) { background: var(--color-primary-dark); }
.bulk-btn-ghost {
  background: transparent; color: var(--color-text-secondary);
  padding: 7px 10px;
}
.bulk-bar { opacity: 0.75; }
.bulk-bar.active { opacity: 1; }
.bulk-btn-ghost { background: transparent; color: var(--color-text-secondary); padding: 7px 10px; }
.bulk-btn-ghost:hover { background: var(--color-bg-hover); color: var(--color-text-primary); }
.rowSelected { background: var(--color-primary-50) !important; }

/* ── Dashboard Stats ── */
.dashboard-content { padding: var(--spacing-xl); }
.dept-stats-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--spacing-md); margin-bottom: var(--spacing-lg); }
.dashboard-stat {
  display: flex; align-items: center; gap: var(--spacing-md);
  padding: var(--spacing-lg);
  background: var(--color-bg-white);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-xl);
  transition: box-shadow 0.2s ease;
}
.dashboard-stat:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.06); }
.dashboard-stat-icon {
  width: 48px; height: 48px; border-radius: var(--radius-lg);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.dsi-blue { background: #EFF6FF; color: #2563EB; }
.dsi-green { background: #ECFDF5; color: #059669; }
.dsi-purple { background: #F5F3FF; color: #7C3AED; }
.dashboard-stat-info { flex: 1; min-width: 0; }
.dashboard-stat-num { font-size: 26px; font-weight: 800; color: var(--color-text-primary); line-height: 1.1; display: block; }
.dashboard-stat-label { font-size: 13px; color: var(--color-text-secondary); font-weight: 500; }
.dashboard-table-card { padding: var(--spacing-xl) !important; }
.dashboard-table-card h4 { font-size: 16px; font-weight: 600; margin-bottom: var(--spacing-md); }

/* ── Import ── */
.import-page { max-width: 700px; margin: 0 auto; }
.import-content { padding: var(--spacing-xl); display: flex; flex-direction: column; gap: var(--spacing-lg); }
.import-card { padding: var(--spacing-xl); border-radius: var(--radius-xl); }
.import-step { font-size: 15px; font-weight: 600; margin-bottom: var(--spacing-lg); color: var(--color-text-primary); display: flex; align-items: center; }
.step-num { display: inline-flex; align-items: center; justify-content: center; width: 26px; height: 26px; background: var(--color-primary); color: #fff; border-radius: 50%; font-size: 13px; font-weight: 700; margin-right: 10px; flex-shrink: 0; }
.import-type-tabs { display: flex; gap: var(--spacing-sm); }
.import-type-btn { display: flex; flex-direction: column; align-items: center; gap: 8px; padding: var(--spacing-xl) var(--spacing-2xl); border: 2px solid var(--color-border-light); border-radius: var(--radius-lg); background: var(--color-bg-white); cursor: pointer; transition: all 0.2s ease; font-family: var(--font-family); min-width: 150px; }
.import-type-btn:hover { border-color: var(--color-primary-100); box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
.import-type-btn.active { border-color: var(--color-primary); background: var(--color-primary-light); box-shadow: 0 0 0 4px var(--color-primary-100); }
.type-icon { font-size: 32px; }
.import-type-img { width: 44px; height: 44px; object-fit: contain; }
.import-format { background: var(--color-bg); padding: var(--spacing-md) var(--spacing-lg); border-radius: var(--radius-md); margin-bottom: var(--spacing-md); }
.import-format code { background: var(--color-primary-50); color: var(--color-primary-600); padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 500; }
.import-dropzone {
  border: 2px dashed var(--color-border); border-radius: var(--radius-lg);
  padding: var(--spacing-2xl); text-align: center;
  transition: all 0.2s ease; cursor: pointer;
  background: var(--color-bg);
}
.import-dropzone:hover, .import-dropzone.dragover { border-color: var(--color-primary); background: var(--color-primary-50); }
.drop-text { font-size: 15px; font-weight: 500; color: var(--color-text-secondary); margin-bottom: var(--spacing-sm); }
.import-preview { margin-top: var(--spacing-md); }
.preview-table-wrap { max-height: 200px; overflow-y: auto; border: 1px solid var(--color-border-light); border-radius: var(--radius-lg); }
.import-result { margin-top: var(--spacing-md); padding: var(--spacing-md); border-radius: var(--radius-md); background: var(--color-bg); }
.result-success { color: var(--color-success); font-size: 14px; margin-bottom: 8px; font-weight: 500; }
.error-list { font-size: 12px; color: var(--color-danger); padding-left: var(--spacing-lg); line-height: 1.8; }

@media (max-width: 768px) {
  .dept-stats-row { grid-template-columns: 1fr; }
}
</style>
