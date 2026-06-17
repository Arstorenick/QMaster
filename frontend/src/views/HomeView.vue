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
          <button :class="['tab', { active: activeTab === 'style' }]" @click="activeTab = 'style'">样式设置</button>
          <button :class="['tab', { active: activeTab === 'stats' }]" @click="activeTab = 'stats'">数据统计</button>
        </div>
        <div class="toolbar-actions">
          <button class="btn btn-ghost btn-sm" @click="previewSurvey">预览</button>
          <button
            class="btn btn-sm"
            :class="currentSurvey.status === 1 ? 'btn-secondary' : 'btn-primary'"
            @click="currentSurvey.status === 1 ? togglePublish() : openPublishDialog()"
          >
            {{ currentSurvey.status === 1 ? '停止收集' : '发布问卷' }}
          </button>
          <button
            v-if="currentSurvey.status === 1"
            class="btn btn-secondary btn-sm"
            @click="copySurvey"
          >复制为新问卷</button>
          <button class="btn btn-secondary btn-sm" @click="showShareDialog = true">分享</button>
          <button v-if="currentSurvey.status === 0" class="btn btn-ghost btn-sm" @click="deleteCurrentSurvey" style="color: var(--color-danger)">删除</button>
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
      <div class="text-center" style="margin-top: 120px">
        <p style="font-size: 48px; margin-bottom: 16px">📋</p>
        <h3>选择问卷或创建新的</h3>
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

    <!-- Publish Settings Dialog -->
    <Teleport to="body">
      <div class="modal-overlay" v-if="showPublishDialog" @click.self="showPublishDialog = false">
        <div class="modal card" style="max-width:520px">
          <h3>发布设置</h3>
          <p class="text-secondary text-sm mt-sm">选择问卷推送的目标部门</p>

          <!-- Department Tree -->
          <div class="publish-section">
            <h4>目标部门</h4>
            <div class="publish-tree">
              <div v-for="dept in publishDepts" :key="dept.id">
                <PublishDeptNode :dept="dept" :level="0" :checked-ids="publishCheckedDepts" @toggle="toggleDeptCheck" />
              </div>
            </div>
          </div>

          <div class="modal-actions">
            <button class="btn btn-ghost" @click="showPublishDialog = false">取消</button>
            <button class="btn btn-secondary btn-sm" @click="autoPopulateDepts" v-if="publishDepts.length">自动填充本部门及下级</button>
            <button class="btn btn-primary" @click="confirmPublish">确认发布</button>
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
import { surveysAPI, questionsAPI, departmentsAPI } from '../api'
import SurveyEditor from '../components/survey/SurveyEditor.vue'
import PublishDeptNode from '../components/survey/PublishDeptNode.vue'
import StylePanel from '../components/survey/StylePanel.vue'
import StatisticsPanel from '../components/statistics/StatisticsPanel.vue'

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

const showPublishDialog = ref(false)
const publishDepts = ref([])
const publishCheckedDepts = ref([])
const lastClickedDept = ref(null)

const showShareDialog = ref(false)
const qrCanvas = ref(null)

const shareLink = computed(() => {
  if (!currentSurvey.value) return ''
  return `${window.location.origin}/display/${currentSurvey.value.id}`
})

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

async function openPublishDialog() {
  showPublishDialog.value = true
  publishCheckedDepts.value = []
  const { data } = await departmentsAPI.tree()
  publishDepts.value = data
  if (auth.user?.department) {
    autoPopulateDepts()
  }
}

function toggleDeptCheck(deptId) {
  lastClickedDept.value = deptId
  const arr = [...publishCheckedDepts.value]
  const idx = arr.indexOf(deptId)
  if (idx > -1) arr.splice(idx, 1)
  else arr.push(deptId)
  publishCheckedDepts.value = arr
}

function autoPopulateDepts() {
  if (!lastClickedDept.value) {
    // 未点击任何部门时，填充本部门及下级
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
  findAndCollect(publishDepts.value)
  publishCheckedDepts.value = ids
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
  const deptIds = [...publishCheckedDepts.value]
  await surveysAPI.publish(s.id, 1, deptIds)
  s.status = 1
  showPublishDialog.value = false
  await loadSurveys()
}

async function deleteCurrentSurvey() {
  if (!confirm('确定删除此问卷？')) return
  await surveysAPI.delete(currentSurvey.value.id)
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
.publish-section { margin: var(--spacing-md) 0; }
.scoring-toggle { display: flex; align-items: center; gap: 4px; font-size: 12px; color: var(--color-text-secondary); cursor: pointer; user-select: none; }
.scoring-toggle input { accent-color: var(--color-warning); }
.lock-banner { padding: var(--spacing-md) var(--spacing-xl); background: var(--color-warning-light); border-bottom: 1px solid #FDE68A; text-align: center; font-size: 13px; color: #92400E; }
.publish-tree { max-height: 300px; overflow-y: auto; border: 1px solid var(--color-border-light); border-radius: var(--radius-md); padding: var(--spacing-sm); }
</style>
