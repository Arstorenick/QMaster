<template>
  <div class="home-layout">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <h3>我的问卷</h3>
        <button class="btn btn-primary btn-sm" @click="showCreateDialog = true">+ 新建</button>
      </div>

      <div class="survey-list" v-if="surveys.length">
        <div
          v-for="s in surveys" :key="s.id"
          class="survey-item"
          :class="{ active: currentSurvey?.id === s.id }"
          @click="selectSurvey(s)"
        >
          <div class="survey-item-title">{{ s.title || '未命名问卷' }}</div>
          <div class="survey-item-desc" v-if="s.description">{{ s.description }}</div>
          <div class="survey-item-time">发布时间：{{ s.published_at ? formatPublishDate(s.published_at) : '您尚未发布该问卷' }}</div>
          <div class="survey-item-meta">
            <span class="tag" :class="s.status === 1 ? 'tag-success' : 'tag-warning'">
              {{ s.status === 1 ? '已发布' : s.status === 2 ? '已关闭' : '草稿' }}
            </span>
            <button class="btn btn-ghost btn-sm survey-edit-btn" @click.stop="openEditDialog(s)">✎ 编辑</button>
          </div>
        </div>
      </div>
      <div class="sidebar-empty" v-else>
        <p class="text-secondary">暂无问卷</p>
        <button class="btn btn-primary btn-sm mt-sm" @click="showCreateDialog = true">创建第一份问卷</button>
      </div>
    </aside>

    <!-- Main Content -->
    <section class="main-area" v-if="currentSurvey">
      <div class="toolbar">
        <div class="toolbar-tabs">
          <button :class="['tab', { active: activeTab === 'edit' }]" @click="activeTab = 'edit'">编辑题目</button>
          <button :class="['tab', { active: activeTab === 'deploy' }]" @click="switchToDeploy">目标部门</button>
          <button :class="['tab', { active: activeTab === 'style' }]" @click="activeTab = 'style'">样式设置</button>
          <button :class="['tab', { active: activeTab === 'stats' }]" @click="activeTab = 'stats'">数据统计</button>
        </div>
        <div class="toolbar-actions">
          <button class="btn btn-ghost" @click="previewSurvey">预览</button>
          <button
            class="btn"
            :class="currentSurvey.status === 1 ? 'btn-secondary' : 'btn-primary'"
            @click="currentSurvey.status === 1 ? togglePublish() : confirmPublish()"
          >
            {{ currentSurvey.status === 1 ? '停止收集' : '发布问卷' }}
          </button>
          <button
            v-if="currentSurvey.status === 1"
            class="btn btn-secondary"
            @click="copySurvey"
          >复制为新问卷</button>
          <button class="btn btn-secondary" @click="showShareDialog = true">分享</button>
          <button v-if="currentSurvey.status === 0" class="btn btn-ghost" @click="showDeleteDialog = true" style="color: var(--color-danger)">删除</button>
        </div>
      </div>

      <!-- Locked Banner -->
      <div class="lock-banner" v-if="currentSurvey.status !== 0 && activeTab === 'edit'">
        <span v-if="currentSurvey.status === 1">🔒 问卷已发布，题目只读。如需修改请「停止收集」后复制为新问卷。</span>
        <span v-else>🔒 问卷已停止收集，题目只读。如需修改请「复制为新问卷」。</span>
      </div>

      <!-- Editor Tab -->
      <SurveyEditor
        v-if="activeTab === 'edit'"
        :survey="currentSurvey"
        :questions="questions"
        :readonly="currentSurvey.status !== 0"
        :scoring-enabled="currentSurvey.scoring_enabled"
        @refresh="loadQuestions"
        @toggleScoring="toggleScoring"
      />

      <!-- Deploy Tab -->
      <section class="deploy-panel" v-if="activeTab === 'deploy'">
        <div class="deploy-top-row">
          <div class="deploy-stat-card">
            <div class="deploy-stat-num">{{ allDeptCount }}</div>
            <div class="deploy-stat-label">部门总数</div>
          </div>
          <div class="deploy-stat-card">
            <div class="deploy-stat-num">{{ targetCheckedDepts.length }}</div>
            <div class="deploy-stat-label">已选部门</div>
          </div>
        </div>
        <div class="deploy-card card">
          <div class="deploy-card-header">
            <h4>📂 选择推送范围</h4>
            <div class="deploy-card-actions">
              <button class="btn btn-secondary btn-sm" @click="autoPopulateDepts" v-if="targetDepts.length">自动填充本部门</button>
              <button class="btn btn-ghost btn-sm" @click="targetCheckedDepts = []">清空</button>
            </div>
          </div>
          <p class="text-secondary text-sm" style="margin-bottom:12px">勾选要推送问卷的部门，发布后该部门下的所有成员将收到问卷任务</p>
          <div class="deploy-tree">
            <div v-for="dept in targetDepts" :key="dept.id">
              <PublishDeptNode :dept="dept" :level="0" :checked-ids="targetCheckedDepts" @toggle="toggleDeptCheck" />
            </div>
            <div v-if="!targetDepts.length" class="deploy-empty">
              <img :src="taskImg" alt="empty" style="width:56px;height:56px;object-fit:contain;margin-bottom:12px;opacity:0.3" />
              <p class="text-secondary">暂无部门数据，请先在「组织架构」中创建部门</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Style Tab -->
      <StylePanel
        v-if="activeTab === 'style'"
        :survey="currentSurvey"
        @updated="onStyleUpdated"
      />

      <!-- Statistics Tab -->
      <StatisticsPanel
        v-if="activeTab === 'stats'"
        :survey="currentSurvey"
      />
    </section>

    <!-- Empty state -->
    <section class="main-area main-empty" v-else>
      <div class="text-center">
        <img :src="taskImg" alt="task" style="width:100px;height:100px;object-fit:contain;margin:0 auto 16px;display:block" />
        <h3>选择问卷或创建新问卷</h3>
        <p class="text-secondary mt-sm">从左侧列表选择问卷开始编辑</p>
      </div>
    </section>

    <!-- Create Dialog -->
    <Teleport to="body">
      <div class="modal-overlay" v-if="showCreateDialog" @click.self="showCreateDialog = false">
        <div class="modal card">
          <h3>创建问卷</h3>
          <form @submit.prevent="createSurvey" class="mt-md">
            <div class="form-group">
              <label>问卷标题</label>
              <input v-model="newTitle" class="input" placeholder="例如：2024年度员工满意度调查" />
            </div>
            <div class="form-group">
              <label>问卷说明（选填）</label>
              <textarea v-model="newDesc" class="input" rows="2" placeholder="简要说明这份问卷的目的"></textarea>
            </div>
            <div class="modal-actions">
              <button type="button" class="btn btn-ghost" @click="showCreateDialog = false">取消</button>
              <button type="submit" class="btn btn-primary" :disabled="!newTitle.trim()">创建</button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Edit Dialog -->
    <Teleport to="body">
      <div class="modal-overlay" v-if="showEditDialog" @click.self="showEditDialog = false">
        <div class="modal card">
          <h3>编辑问卷</h3>
          <form @submit.prevent="saveEditSurvey" class="mt-md">
            <div class="form-group">
              <label>问卷标题</label>
              <input v-model="editTitle" class="input" placeholder="问卷标题" />
            </div>
            <div class="form-group">
              <label>问卷说明</label>
              <textarea v-model="editDesc" class="input" rows="2" placeholder="问卷说明（选填）"></textarea>
            </div>
            <div class="modal-actions">
              <button type="button" class="btn btn-ghost" @click="showEditDialog = false">取消</button>
              <button type="submit" class="btn btn-primary" :disabled="!editTitle.trim()">保存</button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Delete Confirm Dialog -->
    <Teleport to="body">
      <div class="modal-overlay" v-if="showDeleteDialog" @click.self="showDeleteDialog = false">
        <div class="delete-modal">
          <div class="delete-modal-icon">
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
              <circle cx="24" cy="24" r="24" fill="#FEE2E2"/>
              <path d="M24 14v14m0 6h.01" stroke="#DC2626" stroke-width="3" stroke-linecap="round"/>
            </svg>
          </div>
          <h3>确认删除问卷</h3>
          <p class="delete-modal-title">"{{ currentSurvey?.title }}"</p>
          <p class="delete-modal-hint">此操作不可撤销，问卷及所有数据将被永久删除</p>
          <div class="delete-modal-actions">
            <button class="btn btn-secondary" @click="showDeleteDialog = false">取消</button>
            <button class="btn btn-danger" @click="confirmDeleteSurvey">确认</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Share Dialog -->
    <Teleport to="body">
      <div class="modal-overlay" v-if="showShareDialog" @click.self="showShareDialog = false">
        <div class="modal card" style="max-width: 420px">
          <h3>分享问卷</h3>
          <div class="mt-md">
            <label>问卷链接</label>
            <div class="share-link-row">
              <input :value="shareLink" class="input" readonly @focus="$event.target.select()" />
              <button class="btn btn-secondary btn-sm" @click="copyLink">复制</button>
            </div>
            <div class="qr-wrapper mt-md" v-if="shareLink">
              <canvas ref="qrCanvas"></canvas>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useAuthStore } from '../stores/auth'
import { surveysAPI, questionsAPI, departmentsAPI } from '../api'
import SurveyEditor from '../components/survey/SurveyEditor.vue'
import taskImg from '../assets/task.png'
import PublishDeptNode from '../components/survey/PublishDeptNode.vue'
import StylePanel from '../components/survey/StylePanel.vue'
import StatisticsPanel from '../components/statistics/StatisticsPanel.vue'

const auth = useAuthStore()
const surveys = ref([])
const currentSurvey = ref(null)
const questions = ref([])
const activeTab = ref('edit')

const showCreateDialog = ref(false)
const newTitle = ref('')
const newDesc = ref('')

const showEditDialog = ref(false)
const editingSurveyId = ref(null)
const editTitle = ref('')
const editDesc = ref('')

const targetDepts = ref([])
const targetCheckedDepts = ref([])
const lastClickedDept = ref(null)

const showDeleteDialog = ref(false)

const showShareDialog = ref(false)
const qrCanvas = ref(null)

const shareLink = computed(() => {
  if (!currentSurvey.value) return ''
  return `${window.location.origin}/display/${currentSurvey.value.id}`
})

function countAllDepts(list) {
  let n = 0
  for (const d of list) {
    n++
    if (d.children) n += countAllDepts(d.children)
  }
  return n
}
const allDeptCount = computed(() => countAllDepts(targetDepts.value))

onMounted(loadSurveys)

async function loadSurveys() {
  const { data } = await surveysAPI.list()
  surveys.value = data
}

async function selectSurvey(survey) {
  const { data } = await surveysAPI.get(survey.id)
  currentSurvey.value = data
  await loadQuestions()
}

async function loadQuestions() {
  if (!currentSurvey.value) return
  const { data } = await questionsAPI.list(currentSurvey.value.id)
  questions.value = data
}

async function createSurvey() {
  if (!newTitle.value.trim()) return
  const { data } = await surveysAPI.create({
    title: newTitle.value.trim(),
    description: newDesc.value.trim(),
  })
  showCreateDialog.value = false
  newTitle.value = ''
  newDesc.value = ''
  await loadSurveys()
  currentSurvey.value = data
  questions.value = []
  activeTab.value = 'edit'
}

async function togglePublish() {
  const s = currentSurvey.value
  const newStatus = s.status === 1 ? 0 : 1
  await surveysAPI.publish(s.id, newStatus)
  s.status = newStatus
  await loadSurveys()
}

async function switchToDeploy() {
  activeTab.value = 'deploy'
  const { data } = await departmentsAPI.tree()
  targetDepts.value = data
  if (auth.user?.department && !targetCheckedDepts.value.length) {
    autoPopulateDepts()
  }
}

function toggleDeptCheck(deptId) {
  lastClickedDept.value = deptId
  const arr = [...targetCheckedDepts.value]
  const idx = arr.indexOf(deptId)
  if (idx > -1) arr.splice(idx, 1)
  else arr.push(deptId)
  targetCheckedDepts.value = arr
}

function autoPopulateDepts() {
  if (!lastClickedDept.value) {
    if (!auth.user?.department) return
    lastClickedDept.value = auth.user.department
  }
  const ids = []
  function collectIds(list) {
    for (const d of list) {
      ids.push(d.id)
      if (d.children) collectIds(d.children)
    }
  }
  function findAndCollect(list) {
    for (const d of list) {
      if (d.id === lastClickedDept.value) {
        collectIds([d])
        return true
      }
      if (d.children && findAndCollect(d.children)) return true
    }
    return false
  }
  findAndCollect(targetDepts.value)
  targetCheckedDepts.value = ids
}

function formatPublishDate(d) {
  if (!d) return ''
  const date = new Date(d)
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const h = String(date.getHours()).padStart(2, '0')
  const min = String(date.getMinutes()).padStart(2, '0')
  const s = String(date.getSeconds()).padStart(2, '0')
  return `${y}-${m}-${day} ${h}:${min}:${s}`
}

async function copySurvey() {
  const title = prompt('新问卷标题', (currentSurvey.value?.title || '') + ' (副本)')
  if (!title) return
  const { data } = await surveysAPI.copy(currentSurvey.value.id, title)
  await loadSurveys()
  currentSurvey.value = data
  questions.value = []
  activeTab.value = 'edit'
}

async function confirmPublish() {
  const s = currentSurvey.value
  const deptIds = [...targetCheckedDepts.value]
  await surveysAPI.publish(s.id, 1, deptIds)
  s.status = 1
  await loadSurveys()
}

function openDeleteDialog() {
  showDeleteDialog.value = true
}

async function confirmDeleteSurvey() {
  await surveysAPI.delete(currentSurvey.value.id)
  showDeleteDialog.value = false
  currentSurvey.value = null
  questions.value = []
  await loadSurveys()
}

function previewSurvey() {
  if (currentSurvey.value) {
    window.open(`/display/${currentSurvey.value.id}`, '_blank')
  }
}

async function toggleScoring(enabled) {
  const s = currentSurvey.value
  s.scoring_enabled = enabled
  await surveysAPI.update(s.id, { scoring_enabled: enabled })
}

function onStyleUpdated() {
  loadSurveys()
}

function openEditDialog(survey) {
  editingSurveyId.value = survey.id
  editTitle.value = survey.title
  editDesc.value = survey.description || ''
  showEditDialog.value = true
}

async function saveEditSurvey() {
  if (!editTitle.value.trim()) return
  await surveysAPI.update(editingSurveyId.value, {
    title: editTitle.value.trim(),
    description: editDesc.value.trim(),
  })
  showEditDialog.value = false
  await loadSurveys()
  if (currentSurvey.value?.id === editingSurveyId.value) {
    const { data } = await surveysAPI.get(editingSurveyId.value)
    currentSurvey.value = data
  }
}

async function copyLink() {
  try {
    await navigator.clipboard.writeText(shareLink.value)
    alert('链接已复制')
  } catch {
    // fallback
  }
}

watch(showShareDialog, async (val) => {
  if (val && shareLink.value) {
    await nextTick()
    if (qrCanvas.value) {
      const QRCode = (await import('qrcode')).default
      QRCode.toCanvas(qrCanvas.value, shareLink.value, { width: 180, margin: 1 })
    }
  }
})
</script>

<style scoped>
.home-layout {
  display: flex;
  height: calc(100vh - var(--header-height));
}
.sidebar {
  width: var(--sidebar-width);
  border-right: 1px solid var(--color-border-light);
  background: var(--color-bg-white);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}
.sidebar-header {
  padding: var(--spacing-md);
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--color-border-light);
}
.sidebar-header h3 {
  font-size: var(--font-size-sm);
}
.survey-list {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-sm);
}
.survey-item {
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  margin-bottom: 2px;
  background: var(--color-bg);
}
.survey-item:hover { background: var(--color-bg-hover); }
.survey-item.active { background: var(--color-primary-light); box-shadow: inset 3px 0 0 var(--color-primary); }
.survey-item-title {
  font-size: var(--font-size-sm);
  font-weight: 500;
  margin-bottom: 2px;
}
.survey-item-time { font-size: 11px; color: var(--color-text-tertiary); margin-bottom: 2px; }
.survey-item-desc {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.survey-item-meta {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}
.sidebar-empty {
  padding: var(--spacing-xl);
  text-align: center;
}
.main-area {
  flex: 1;
  overflow-y: auto;
  background: var(--color-bg);
}
.main-empty {
  display: flex;
  align-items: center;
  justify-content: center;
}
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-sm) var(--spacing-lg);
  background: var(--color-bg-white);
  border-bottom: 1px solid var(--color-border-light);
  position: sticky;
  top: 0;
  z-index: 10;
}
.toolbar-tabs {
  display: flex;
  gap: 2px;
}
.tab {
  padding: 6px 16px;
  font-size: var(--font-size-sm);
  font-family: var(--font-family);
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  cursor: pointer;
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}
.tab:hover { background: var(--color-bg-hover); }
.tab.active {
  background: var(--color-primary-light);
  color: var(--color-primary);
  font-weight: 500;
}
.survey-edit-btn {
  margin-left: auto;
  opacity: 0;
  transition: opacity var(--transition-fast);
}
.survey-item:hover .survey-edit-btn {
  opacity: 1;
}

.toolbar-actions {
  display: flex;
  gap: var(--spacing-sm);
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.3);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}
.modal {
  width: 90%;
  max-width: 480px;
  padding: var(--spacing-xl);
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-lg);
}
.share-link-row {
  display: flex;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-xs);
}
.share-link-row .input { flex: 1; }
.qr-wrapper {
  display: flex;
  justify-content: center;
}
.scoring-toggle { display: flex; align-items: center; gap: 4px; font-size: 12px; color: var(--color-text-secondary); cursor: pointer; user-select: none; }
.scoring-toggle input { accent-color: var(--color-warning); }
.lock-banner { padding: var(--spacing-md) var(--spacing-xl); background: var(--color-warning-light); border-bottom: 1px solid #FDE68A; text-align: center; font-size: 13px; color: #92400E; }
.deploy-panel { padding: var(--spacing-lg); }
.deploy-top-row { display: flex; gap: var(--spacing-md); margin-bottom: var(--spacing-lg); }
.deploy-stat-card {
  flex: 1; text-align: center;
  padding: var(--spacing-lg);
  border-radius: var(--radius-lg);
  background: linear-gradient(135deg, var(--color-primary-50) 0%, var(--color-primary-light) 100%);
  border: 1px solid var(--color-primary-100);
}
.deploy-stat-num { font-size: 32px; font-weight: 700; color: var(--color-primary); line-height: 1.1; }
.deploy-stat-label { font-size: 13px; color: var(--color-primary-600); margin-top: 4px; }
.deploy-card { padding: var(--spacing-lg); }
.deploy-card-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.deploy-card-header h4 { font-size: var(--font-size-md); font-weight: 600; }
.deploy-card-actions { display: flex; gap: var(--spacing-sm); }
.deploy-tree { max-height: 420px; overflow-y: auto; border: 1px solid var(--color-border-light); border-radius: var(--radius-md); padding: var(--spacing-sm); background: var(--color-bg); }
.deploy-empty { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: var(--spacing-2xl); }
.publish-tree { max-height: 300px; overflow-y: auto; border: 1px solid var(--color-border-light); border-radius: var(--radius-md); padding: var(--spacing-sm); }
.delete-modal {
  width: 90%; max-width: 380px;
  padding: var(--spacing-2xl);
  background: var(--color-bg-white);
  border-radius: var(--radius-xl);
  text-align: center;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
  animation: modalIn 0.2s ease;
}
.delete-modal-icon { margin-bottom: var(--spacing-md); }
.delete-modal h3 { font-size: 18px; font-weight: 700; margin-bottom: var(--spacing-sm); }
.delete-modal-title {
  font-weight: 600; color: var(--color-text-primary);
  margin-bottom: var(--spacing-sm);
  padding: 6px 12px;
  background: var(--color-bg);
  border-radius: var(--radius-md);
  display: inline-block;
}
.delete-modal-hint { font-size: 13px; color: var(--color-text-tertiary); }
.delete-modal-actions {
  display: flex; gap: var(--spacing-sm);
  justify-content: center; margin-top: var(--spacing-xl);
}
.btn-danger {
  background: #DC2626; border-color: #DC2626;
  color: #fff; padding: 8px 24px;
  border-radius: var(--radius-md);
  font-size: 14px; font-weight: 500; font-family: var(--font-family);
  cursor: pointer; transition: all 0.15s ease;
}
.btn-danger:hover { background: #B91C1C; border-color: #B91C1C; }
@keyframes modalIn { from { opacity: 0; transform: scale(0.95) translateY(-8px); } to { opacity: 1; transform: scale(1) translateY(0); } }
</style>
