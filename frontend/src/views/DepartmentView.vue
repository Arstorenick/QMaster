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
                <thead><tr><th>账号</th><th>用户名</th><th>工号</th><th>联系方式</th><th>所属部门</th><th>角色</th></tr></thead>
                <tbody>
                  <tr v-for="m in filteredMembers" :key="m.id">
                    <td style="min-width:160px"><strong>{{ m.username }}</strong></td>
                    <td>{{ m.display_name || '-' }}</td>
                    <td class="text-secondary text-sm">{{ m.employee_id || '-' }}</td>
                    <td class="text-secondary text-sm">{{ m.phone || '-' }}</td>
                    <td class="text-secondary text-sm" style="min-width:100px">{{ shortDeptName(m.department_name) }}</td>
                    <td><span class="tag" :class="m.role === 1 ? 'tag-primary' : m.role === 2 ? 'tag-success' : m.role === 4 ? 'tag-primary' : 'tag-warning'">{{ m.role_label }}</span></td>
                  </tr>
                </tbody>
              </table>
              <p v-else class="text-secondary text-sm text-center" style="padding:var(--spacing-lg)">暂无成员</p>
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

async function loadDashboard() {
  activeTab.value = 'dashboard'
  const { data } = await departmentsAPI.dashboard()
  dashboard.value = data
}
</script>

<style scoped>
.dept-page { height: calc(100vh - var(--header-height)); }
.dept-layout { display: flex; height: 100%; }
.dept-sidebar {
  width: var(--sidebar-width); flex-shrink: 0;
  border-right: 1px solid var(--color-border-light);
  background: var(--color-bg); display: flex; flex-direction: column;
}
.dept-sidebar-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: var(--spacing-md) var(--spacing-md) 0;
}
.dept-sidebar-header h3 { font-size: 14px; font-weight: 600; color: var(--color-text-primary); }
.dept-sidebar :deep(.input) { margin: var(--spacing-sm) var(--spacing-md); width: auto; }
.dept-tree { flex: 1; overflow-y: auto; padding: 4px 0 var(--spacing-md); }
.dept-main { flex: 1; overflow-y: auto; background: var(--color-bg-white); }
.dept-detail-header {
  display: flex; align-items: flex-start; justify-content: space-between;
  padding: var(--spacing-xl) var(--spacing-xl) var(--spacing-lg);
  border-bottom: 1px solid var(--color-border-light);
}
.dept-detail-header h2 { font-size: 20px; }
.dept-stats { display: flex; gap: var(--spacing-md); flex-wrap: wrap; padding: var(--spacing-lg) var(--spacing-xl); }
.stat-item {
  background: var(--color-bg); border-radius: var(--radius-lg);
  padding: var(--spacing-md) var(--spacing-xl); text-align: center;
  border: 1px solid var(--color-border-light); min-width: 100px;
}
.stat-num { font-size: 22px; font-weight: 700; color: var(--color-primary); display: block; line-height: 1.2; }
.stat-label { font-size: 11px; color: var(--color-text-tertiary); margin-top: 2px; }
.dept-empty {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; height: 100%; color: var(--color-text-secondary);
}
.dept-empty h3 { color: var(--color-text-primary); }
.form-group { margin-bottom: var(--spacing-md); }
.form-group label { display: block; font-size: var(--font-size-sm); font-weight: 500; margin-bottom: 4px; color: var(--color-text-primary); }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.3); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 200; }
.modal { width: 90%; max-width: 480px; padding: var(--spacing-xl); }
.modal-actions { display: flex; justify-content: flex-end; gap: var(--spacing-sm); margin-top: var(--spacing-lg); }
.dept-main :deep(.card) { margin: 0 var(--spacing-xl) var(--spacing-xl); }
.dept-main :deep(.table) { font-size: 13px; }
.dept-main :deep(.table th) { font-size: 11px; letter-spacing: 0.03em; }

/* Import */
.import-page { max-width: 700px; margin: 0 auto; }
.import-content { padding: var(--spacing-xl); display: flex; flex-direction: column; gap: var(--spacing-md); }
.import-card { padding: var(--spacing-xl); }
.import-step { font-size: 14px; font-weight: 600; margin-bottom: var(--spacing-md); color: var(--color-text-primary); }
.step-num { display: inline-flex; align-items: center; justify-content: center; width: 24px; height: 24px; background: var(--color-primary); color: #fff; border-radius: 50%; font-size: 12px; margin-right: 8px; }
.import-type-tabs { display: flex; gap: var(--spacing-sm); }
.import-type-btn { display: flex; flex-direction: column; align-items: center; gap: 6px; padding: var(--spacing-lg) var(--spacing-xl); border: 2px solid var(--color-border-light); border-radius: var(--radius-md); background: var(--color-bg-white); cursor: pointer; transition: all var(--transition-fast); font-family: var(--font-family); min-width: 140px; }
.import-type-btn:hover { border-color: var(--color-primary-100); }
.import-type-btn.active { border-color: var(--color-primary); background: var(--color-primary-light); }
.type-icon { font-size: 28px; }
.import-type-img { width: 40px; height: 40px; object-fit: contain; }
.import-format { background: var(--color-bg); padding: var(--spacing-md); border-radius: var(--radius-md); margin-bottom: var(--spacing-md); }
.import-format code { background: var(--color-primary-50); color: var(--color-primary-700); padding: 1px 6px; border-radius: 4px; font-size: 12px; }
.import-dropzone { border: 2px dashed var(--color-border); border-radius: var(--radius-md); padding: var(--spacing-xl); text-align: center; transition: all var(--transition-fast); cursor: pointer; }
.import-dropzone:hover, .import-dropzone.dragover { border-color: var(--color-primary); background: var(--color-primary-50); }
.drop-text { font-size: 14px; color: var(--color-text-secondary); margin-bottom: var(--spacing-sm); }
.import-preview { margin-top: var(--spacing-md); }
.preview-table-wrap { max-height: 200px; overflow-y: auto; border: 1px solid var(--color-border-light); border-radius: var(--radius-md); }
.import-result { margin-top: var(--spacing-md); padding: var(--spacing-md); border-radius: var(--radius-md); }
.result-success { color: var(--color-success); font-size: 14px; margin-bottom: 8px; }
.error-list { font-size: 12px; color: var(--color-danger); padding-left: var(--spacing-lg); line-height: 1.8; }
</style>
