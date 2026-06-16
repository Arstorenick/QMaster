<template>
  <div class="dept-page">
    <div class="dept-layout">
      <!-- Left: Tree -->
      <aside class="dept-sidebar">
        <div class="dept-sidebar-header">
          <h3>组织架构</h3>
          <div class="flex gap-sm">
            <button class="btn btn-primary btn-sm" @click="showCreate = true" v-if="auth.isCreator">+ 新建</button>
            <button class="btn btn-secondary btn-sm" @click="activeTab = 'import'" v-if="auth.isCreator">导入</button>
          </div>
        </div>
        <input v-model="search" class="input" placeholder="搜索部门..." />
        <div class="dept-tree" v-if="filteredTree.length">
          <DeptNode
            v-for="dept in filteredTree" :key="dept.id"
            :dept="dept" :level="0"
            :active-id="activeDept?.id" :search="search"
            @select="selectDept" @delete="handleDelete"
          />
        </div>
        <div v-else class="text-center text-secondary text-sm" style="padding:var(--spacing-xl)">
          {{ departments.length ? '无匹配部门' : '暂无部门' }}
        </div>
      </aside>

      <!-- Right: Content -->
      <section class="dept-main">
        <template v-if="activeTab === 'import'">
          <h2>批量导入</h2>
          <button class="btn btn-ghost btn-sm mt-sm" @click="activeTab = 'detail'">返回</button>
          <div class="card" style="padding:var(--spacing-xl);max-width:600px;margin-top:12px">
            <div class="form-group">
              <label>导入类型</label>
              <select v-model="importType" class="input">
                <option value="department">部门</option>
                <option value="user">用户</option>
              </select>
            </div>
            <div class="form-group">
              <label>CSV 内容</label>
              <p class="text-secondary text-sm" style="margin-bottom:8px">
                {{ importType === 'department' ? '格式：部门名,上级部门完整路径' : '格式：用户名,密码,角色,部门路径' }}
              </p>
              <textarea v-model="csvText" class="input" rows="8" placeholder="沈阳公司\n和平区分公司,沈阳公司"></textarea>
            </div>
            <div class="form-group"><input type="file" accept=".csv" @change="handleFileUpload" class="input" /></div>
            <button class="btn btn-primary" @click="doImport" :disabled="!csvText.trim() || importing">{{ importing ? '导入中...' : '开始导入' }}</button>
            <div v-if="importResult" class="mt-md">
              <p style="color:var(--color-success)">成功导入 {{ importResult.total }} 条</p>
              <p v-if="importResult.errors?.length" style="color:var(--color-danger)">错误: {{ importResult.errors.join('; ') }}</p>
            </div>
          </div>
        </template>

        <template v-else-if="activeTab === 'dashboard'">
          <h2>部门统计看板</h2>
          <button class="btn btn-ghost btn-sm mt-sm" @click="activeTab = 'detail'">返回</button>
          <div class="dept-stats" style="margin-top:12px">
            <div class="stat-item"><span class="stat-num">{{ dashboard.total_users }}</span><span class="stat-label">总用户数</span></div>
            <div class="stat-item"><span class="stat-num">{{ dashboard.total_surveys }}</span><span class="stat-label">总问卷数</span></div>
            <div class="stat-item"><span class="stat-num">{{ dashboard.total_submissions }}</span><span class="stat-label">总提交数</span></div>
          </div>
          <div class="card" style="padding:var(--spacing-lg);margin-top:12px">
            <h4 style="margin-bottom:12px">各部门概览</h4>
            <table class="table">
              <thead><tr><th>部门</th><th>成员数</th><th>提交数</th><th>子部门数</th></tr></thead>
              <tbody><tr v-for="d in dashboard.departments" :key="d.id"><td><strong>{{ d.name }}</strong></td><td><span class="tag tag-primary">{{ d.member_count }} 人</span></td><td>{{ d.submission_count }} 份</td><td>{{ d.children_count }}</td></tr></tbody>
            </table>
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
            <div class="card" style="padding:var(--spacing-lg)">
              <div class="flex items-center justify-between" style="margin-bottom:12px">
                <h4>部门成员</h4>
                <input v-model="memberSearch" class="input" placeholder="搜索成员..." style="max-width:200px" />
              </div>
              <table class="table" v-if="filteredMembers.length">
                <thead><tr><th>用户名</th><th>角色</th><th>所属部门</th><th>工号</th><th>联系方式</th><th>加入时间</th></tr></thead>
                <tbody>
                  <tr v-for="m in filteredMembers" :key="m.id">
                    <td><strong>{{ m.username }}</strong></td>
                    <td><span class="tag" :class="m.role === 1 ? 'tag-primary' : m.role === 2 ? 'tag-success' : m.role === 4 ? 'tag-primary' : 'tag-warning'">{{ m.role_label }}</span></td>
                    <td class="text-secondary text-sm">{{ m.department_name || '-' }}</td>
                    <td class="text-secondary text-sm">{{ m.employee_id || '-' }}</td>
                    <td class="text-secondary text-sm">{{ m.phone || '-' }}</td>
                    <td class="text-secondary text-sm">{{ m.date_joined?.slice(0, 10) }}</td>
                  </tr>
                </tbody>
              </table>
              <p v-else class="text-secondary text-sm text-center" style="padding:var(--spacing-lg)">暂无成员</p>
            </div>
          </template>
          <div v-else class="dept-empty text-center">
            <p style="font-size:56px;margin-bottom:16px">🏢</p>
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
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { departmentsAPI } from '../api'
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

const dashboard = ref({ total_users: 0, total_surveys: 0, total_submissions: 0, departments: [] })

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

function handleFileUpload(e) {
  const file = e.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (ev) => { csvText.value = ev.target.result }
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

async function loadDashboard() {
  activeTab.value = 'dashboard'
  const { data } = await departmentsAPI.dashboard()
  dashboard.value = data
}
</script>

<style scoped>
.dept-page { height: calc(100vh - var(--header-height)); }
.dept-layout { display: flex; height: 100%; }
.dept-sidebar { width: var(--sidebar-width); flex-shrink: 0; border-right: 1px solid var(--color-border-light); background: var(--color-bg-white); display: flex; flex-direction: column; padding: var(--spacing-md); }
.dept-sidebar-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--spacing-sm); }
.dept-sidebar-header h3 { font-size: var(--font-size-sm); }
.dept-tree { flex: 1; overflow-y: auto; margin-top: var(--spacing-sm); }
.dept-main { flex: 1; overflow-y: auto; padding: var(--spacing-xl); background: var(--color-bg); }
.dept-detail-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: var(--spacing-lg); }
.dept-stats { display: flex; gap: var(--spacing-md); flex-wrap: wrap; }
.stat-item { background: var(--color-bg-white); border-radius: var(--radius-md); padding: var(--spacing-md) var(--spacing-xl); text-align: center; border: 1px solid var(--color-border-light); }
.stat-num { font-size: var(--font-size-xl); font-weight: 700; color: var(--color-primary); display: block; }
.stat-label { font-size: var(--font-size-xs); color: var(--color-text-secondary); }
.dept-empty { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; }
.form-group { margin-bottom: var(--spacing-md); }
.form-group label { display: block; font-size: var(--font-size-sm); font-weight: 500; margin-bottom: 4px; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.3); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 200; }
.modal { width: 90%; max-width: 480px; padding: var(--spacing-xl); }
.modal-actions { display: flex; justify-content: flex-end; gap: var(--spacing-sm); margin-top: var(--spacing-lg); }
</style>
