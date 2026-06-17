<template>
  <div class="tasks-layout">
    <!-- Left: Survey List -->
    <aside class="tasks-sidebar">
      <div class="sidebar-header">
        <h3>我的问卷任务</h3>
      </div>
      <div class="task-list" v-if="tasks.length">
        <div
          v-for="t in tasks" :key="t.id"
          class="task-item"
          :class="{ active: activeSurvey?.id === t.id, done: t.submitted }"
          @click="openSurvey(t)"
        >
          <div class="task-item-title">{{ t.title }}</div>
          <div class="task-item-meta">
            <span class="text-sm" :class="t.submitted ? 'text-secondary' : 'text-muted'">{{ t.submitted ? '完成时间 ' + formatDate(t.updated_at) : '您尚未开始答题' }}</span>
          </div>
          <div class="task-item-meta">
            <span v-if="t.submitted" class="tag tag-success">已提交</span>
            <span v-else class="tag tag-warning">待完成</span>
            <span class="text-sm text-secondary">{{ t.dept_name }}</span>
          </div>
        </div>
      </div>
      <div v-else class="sidebar-empty text-center" style="padding:var(--spacing-xl)">
        <p style="font-size:36px;margin-bottom:8px">📋</p>
        <p class="text-secondary text-sm">暂无问卷任务</p>
      </div>
    </aside>

    <!-- Right: Survey Display -->
    <section class="tasks-main">
      <template v-if="activeSurvey">
        <div class="display-card card" v-if="!submitted" :style="taskCardStyle">
          <div class="display-logo" v-if="activeSurvey.style?.logo_image" :style="{ backgroundColor: activeSurvey.style?.logo_bg_color || '#fff' }">
            <img :src="activeSurvey.style.logo_image" alt="Logo" />
          </div>
          <img v-if="activeSurvey.style?.header_image" :src="activeSurvey.style.header_image" class="display-header-img" alt="Header" />
          <div class="display-header" v-if="activeSurvey.style?.show_title !== false">
            <h2>{{ activeSurvey.title }}</h2>
            <p class="text-secondary text-sm" v-if="activeSurvey.description && activeSurvey.style?.show_description !== false">{{ activeSurvey.description }}</p>
          </div>
          <!-- Current Page Questions -->
          <template v-for="q in currentPageQuestions" :key="q.id">
            <!-- Separators -->
            <div v-if="q.type === 'page_break'" class="page-break-line"></div>
            <div v-else-if="q.type === 'section_break'" class="section-break-title">{{ q.title || '章节标题' }}</div>
            <!-- Regular Question -->
            <div v-else class="display-q">
            <div class="dq-title">
              <span class="dq-num">{{ getQNumber(q.id) }}.</span>
              <span>{{ q.title }}</span>
              <span v-if="q.is_required" style="color:var(--color-danger)">*</span>
            </div>
            <!-- Radio -->
            <div v-if="q.type === 'radio'" class="dq-options">
              <label v-for="opt in q.options" :key="opt.id" class="dq-opt">
                <input type="radio" :name="'q-'+q.id" :value="opt.id" v-model="answers[q.id]" />
                <span>{{ opt.title }}</span>
              </label>
            </div>
            <!-- Checkbox -->
            <div v-if="q.type === 'checkbox'" class="dq-options">
              <label v-for="opt in q.options" :key="opt.id" class="dq-opt">
                <input type="checkbox" :value="opt.id" v-model="answers[q.id]" />
                <span>{{ opt.title }}</span>
              </label>
            </div>
            <!-- Text / Textarea -->
            <textarea v-if="q.type === 'text' || q.type === 'textarea'" class="input" :rows="q.type === 'textarea' ? 3 : 1" v-model="answers[q.id]" placeholder="请输入"></textarea>
            <!-- Rating -->
            <div v-if="q.type === 'rating'" class="dq-rating">
              <span v-for="i in (q.config?.max_score || 5)" :key="i" class="rating-star" :class="{ active: answers[q.id] >= i }" @click="answers[q.id] = i">★</span>
            </div>
            <!-- Dropdown -->
            <select v-if="q.type === 'dropdown'" class="input" v-model="answers[q.id]" style="max-width:300px">
              <option value="">请选择</option>
              <option v-for="opt in q.options" :key="opt.id" :value="opt.id">{{ opt.title }}</option>
            </select>
            <!-- Scale -->
            <div v-if="q.type === 'scale'" class="dq-scale">
              <span class="text-sm">{{ q.config?.left_label }}</span>
              <label v-for="i in (q.config?.scale || 5)" :key="i" class="scale-radio"><input type="radio" :value="i" v-model="answers[q.id]" /><span>{{ i }}</span></label>
              <span class="text-sm">{{ q.config?.right_label }}</span>
            </div>
            <!-- Date / Time -->
            <input v-if="q.type === 'date'" class="input" type="date" v-model="answers[q.id]" style="max-width:240px" />
            <input v-if="q.type === 'time'" class="input" type="time" v-model="answers[q.id]" style="max-width:240px" />
            <!-- Slider -->
            <div v-if="q.type === 'slider'" class="dq-slider">
              <input type="range" :min="q.config?.min || 0" :max="q.config?.max || 100" v-model="answers[q.id]" style="flex:1" />
              <span>{{ answers[q.id] || 0 }}{{ q.config?.unit || '' }}</span>
            </div>
            <!-- Ranking -->
            <div v-if="q.type === 'ranking'" class="dq-options">
              <div v-for="opt in q.options" :key="opt.id" class="dq-opt">
                <span>{{ opt.title }}</span>
                <input type="number" :min="1" :max="q.options.length" v-model="answers[q.id+'_'+opt.id]" style="width:60px;margin-left:auto" class="input" />
              </div>
            </div>
            <!-- Multi Text -->
            <div v-if="q.type === 'multi_text'">
              <div v-for="(field, fi) in (q.config?.fields || [])" :key="fi" style="margin-bottom:8px">
                <label style="font-size:13px;display:block;margin-bottom:2px">{{ field.label }}</label>
                <input class="input" :placeholder="field.placeholder" v-model="answers[q.id+'_field_'+fi]" />
              </div>
            </div>
            <!-- File Upload -->
            <div v-if="q.type === 'file_upload'" style="margin-top:4px">
              <input type="file" @change="e => handleTaskFile(q, e)" />
              <span v-if="taskFiles[q.id]" class="text-sm text-secondary" style="margin-left:8px">{{ taskFiles[q.id].name }}</span>
            </div>
            <!-- Image Radio -->
            <div v-if="q.type === 'image_radio'" class="dq-options">
              <label v-for="opt in q.options" :key="opt.id" class="dq-opt">
                <input type="radio" :name="'q-'+q.id" :value="opt.id" v-model="answers[q.id]" />
                <span>{{ opt.title }}</span>
              </label>
            </div>
            <!-- Image Checkbox -->
            <div v-if="q.type === 'image_checkbox'" class="dq-options">
              <label v-for="opt in q.options" :key="opt.id" class="dq-opt">
                <input type="checkbox" :value="opt.id" v-model="answers[q.id]" />
                <span>{{ opt.title }}</span>
              </label>
            </div>
            </div>
          </template>
          <!-- Page Navigation -->
          <div class="page-nav" v-if="pages.length > 1">
            <button class="btn btn-secondary btn-sm" :disabled="currentPage === 0" @click="currentPage--">上一页</button>
            <span class="text-sm text-secondary page-indicator">{{ currentPage + 1 }} / {{ pages.length }}</span>
            <button class="btn btn-primary btn-sm" :disabled="currentPage >= pages.length - 1" @click="currentPage++">下一页</button>
          </div>
          <div style="text-align:center;margin-top:var(--spacing-xl)">
            <button class="btn btn-primary btn-lg" @click="submitSurvey" :disabled="submitting">
              {{ submitting ? '提交中...' : '提交问卷' }}
            </button>
          </div>
        </div>
        <div class="submitted-card" v-else>
          <div class="submitted-inner">
            <div class="submitted-icon">✓</div>
            <h2>已完成提交</h2>
            <p>感谢您的参与！您的回答已成功提交。</p>
            <div class="submitted-info">
              <span>如需修改请联系管理员</span>
            </div>
          </div>
        </div>
      </template>
      <div v-else class="tasks-empty">
        <div class="empty-inner">
          <div class="empty-icon">📋</div>
          <h3>{{ tasks.length ? '选择左侧问卷开始答题' : '暂无待完成问卷' }}</h3>
          <p class="empty-sub" v-if="!tasks.length">管理员发布问卷后，将自动出现在这里</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { surveysAPI, responsesAPI, departmentsAPI } from '../api'

const auth = useAuthStore()
const tasks = ref([])
const activeSurvey = ref(null)
const activeQuestions = ref([])
const answers = reactive({})
const submitted = ref(false)
const submitting = ref(false)
const currentPage = ref(0)
const taskFiles = reactive({})

const pages = computed(() => {
  if (!activeSurvey.value?.questions) return []
  const result = []
  let current = []
  for (const q of activeSurvey.value.questions) {
    if (q.type === 'page_break') {
      if (current.length) result.push(current)
      current = []
    } else {
      current.push(q)
    }
  }
  if (current.length) result.push(current)
  return result.length ? result : [activeSurvey.value.questions.filter(q => !['page_break','section_break','divider'].includes(q.type))]
})

const currentPageQuestions = computed(() => pages.value[currentPage.value] || [])

const taskCardStyle = computed(() => {
  const s = activeSurvey.value?.style || {}
  return {
    '--survey-theme': s.theme_color || '#4F46E5',
    '--survey-progress': s.progress_color || s.theme_color || '#4F46E5',
  }
})

onMounted(loadTasks)

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleString('zh-CN', { hour12: false })
}

async function loadTasks() {
  if (!auth.user?.department) {
    tasks.value = []
    return
  }
  const { data } = await surveysAPI.myTasks().catch(() => ({ data: [] }))
  tasks.value = data
}

function isAncestor(targetId, deptId) {
  // Simplified: check if target is ancestor via flat list
  // The full implementation would check the department tree
  return false
}

async function openSurvey(survey) {
  submitted.value = survey.submitted
  if (survey.submitted) {
    activeSurvey.value = survey
    activeQuestions.value = []
    return
  }
  const { data } = await surveysAPI.public(survey.id)
  activeSurvey.value = data
  activeQuestions.value = data.questions || []
  currentPage.value = 0
  for (const key in answers) delete answers[key]
  for (const q of activeQuestions.value) {
    if (q.type === 'checkbox' || q.type === 'image_checkbox') answers[q.id] = []
  }
}

function getQNumber(qId) {
  if (!activeSurvey.value) return ''
  let count = 0
  for (const q of activeSurvey.value.questions || []) {
    if (q.type === 'page_break' || q.type === 'section_break') continue
    count++
    if (q.id === qId) return count
  }
  return ''
}

function handleTaskFile(q, e) {
  const file = e.target.files[0]
  if (file) {
    taskFiles[q.id] = file
    answers[q.id] = file
  }
}

async function submitSurvey() {
  const answerList = []
  for (const q of activeQuestions.value) {
    const val = answers[q.id]
    if (!val && q.is_required && !(Array.isArray(val) && val.length)) continue
    const payload = { question: q.id }
    if (q.type === 'checkbox' || q.type === 'image_checkbox') {
      if (Array.isArray(val) && val.length) {
        for (const optId of val) answerList.push({ question: q.id, option: Number(optId) })
      }
      continue
    }
    if (['radio','dropdown','image_radio'].includes(q.type)) payload.option = val ? Number(val) : null
    else if (['rating','scale','slider'].includes(q.type)) payload.answer_number = Number(val) || 0
    else if (['date','time'].includes(q.type)) payload.answer_text = val || ''
    else if (q.type === 'ranking') {
      payload.answer_json = {}
      for (const opt of q.options) {
        payload.answer_json[opt.id] = Number(answers[q.id + '_' + opt.id]) || 0
      }
    } else if (q.type === 'multi_text') {
      payload.answer_json = {}
      for (const fi in (q.config?.fields || [])) {
        payload.answer_json['field_' + fi] = answers[q.id + '_field_' + fi] || ''
      }
    } else if (q.type === 'file_upload') {
      if (val instanceof File) payload.answer_text = val.name
    } else payload.answer_text = val || ''
    if (payload.option !== undefined || payload.answer_text || payload.answer_number !== undefined || payload.answer_json) {
      answerList.push(payload)
    }
  }
  submitting.value = true
  try {
    await responsesAPI.submit(activeSurvey.value.id, { answers: answerList, duration_seconds: 0 })
    submitted.value = true
    // Update task status
    const task = tasks.value.find(t => t.id === activeSurvey.value.id)
    if (task) task.submitted = true
  } catch (e) {
    alert('提交失败: ' + (e.response?.data?.detail || '请重试'))
  }
  submitting.value = false
}
</script>

<style scoped>
.tasks-layout { display: flex; height: calc(100vh - var(--header-height)); }
.tasks-sidebar { width: var(--sidebar-width); flex-shrink: 0; border-right: 1px solid var(--color-border-light); background: var(--color-bg-white); display: flex; flex-direction: column; }
.sidebar-header { padding: var(--spacing-md); border-bottom: 1px solid var(--color-border-light); }
.sidebar-header h3 { font-size: var(--font-size-sm); }
.task-list { flex:1; overflow-y: auto; padding: var(--spacing-sm); }
.task-item { padding: var(--spacing-sm) var(--spacing-md); border-radius: var(--radius-md); cursor: pointer; margin-bottom: 2px; transition: all var(--transition-fast); background: var(--color-bg); }
.task-item:hover { background: var(--color-bg-hover); }
.task-item.active { background: var(--color-primary-light); box-shadow: inset 3px 0 0 var(--color-primary); }
.task-item-title { font-size: var(--font-size-sm); font-weight: 500; margin-bottom: 4px; }
.task-item-meta { display: flex; align-items: center; gap: var(--spacing-sm); }
.tasks-main { flex:1; overflow-y: auto; background: var(--color-bg); padding: var(--spacing-lg); }
.tasks-empty {
  display: flex; align-items: center; justify-content: center;
  height: 100%; min-height: 400px;
  background: linear-gradient(180deg, var(--color-bg) 0%, var(--color-bg-white) 100%);
}
.empty-inner { text-align: center; animation: fadeInUp 0.6s ease; }
.empty-icon {
  width: 88px; height: 88px; margin: 0 auto 20px;
  border-radius: 50%; background: var(--color-primary-50);
  display: flex; align-items: center; justify-content: center;
  font-size: 40px; box-shadow: 0 4px 16px rgba(79, 70, 229, 0.1);
}
.empty-inner h3 { font-size: 18px; color: var(--color-text-primary); margin-bottom: 8px; }
.empty-sub { font-size: 13px; color: var(--color-text-tertiary); }

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}
.display-card { max-width: 1400px; margin: 0 auto var(--spacing-md); padding: var(--spacing-lg); }
.display-logo { text-align: center; padding: var(--spacing-md); border-radius: var(--radius-md) var(--radius-md) 0 0; }
.display-logo img { max-height: 60px; }
.display-header-img { width: 100%; max-height: 200px; object-fit: cover; border-radius: var(--radius-md) var(--radius-md) 0 0; }
.display-header { text-align: center; margin-bottom: var(--spacing-xl); padding-bottom: var(--spacing-lg); border-bottom: 1px solid var(--color-border-light); }
.dq-num { color: var(--survey-theme); }
.display-q { padding: var(--spacing-lg) 0; border-bottom: 1px solid var(--color-border-light); }
.dq-title { font-weight: 500; margin-bottom: var(--spacing-sm); }
.dq-num { color: var(--color-primary); font-weight: 600; }
.dq-options { display: flex; flex-direction: column; gap: var(--spacing-sm); }
.dq-opt { display: flex; align-items: center; gap: var(--spacing-sm); padding: var(--spacing-sm) var(--spacing-md); border: 1px solid var(--color-border-light); border-radius: var(--radius-md); cursor: pointer; }
.dq-opt:hover { border-color: var(--color-primary); background: var(--color-primary-light); }
.dq-rating { display: flex; gap: 4px; }
.rating-star { font-size: 32px; color: var(--color-border); cursor: pointer; }
.rating-star.active, .rating-star:hover { color: var(--color-warning); }
.dq-scale { display: flex; align-items: center; gap: var(--spacing-sm); }
.scale-radio { display: flex; flex-direction: column; align-items: center; cursor: pointer; }
.dq-slider { display: flex; align-items: center; gap: var(--spacing-md); }
.page-break-line { border-top: 2px dashed var(--color-border); margin: var(--spacing-lg) 0; }
.section-break-title { text-align: center; font-size: 22px; font-weight: 700; padding: var(--spacing-lg) 0; color: var(--color-text-primary); }
.divider-line { border-top: 1px solid var(--color-border-light); margin: var(--spacing-md) 0; }
.page-nav { display: flex; align-items: center; justify-content: center; gap: var(--spacing-lg); padding: var(--spacing-md) 0; }
.page-nav .btn { min-width: 80px; }
.page-indicator { min-width: 60px; text-align: center; }

.submitted-card {
  display: flex; align-items: center; justify-content: center;
  min-height: 100%; padding: var(--spacing-2xl);
}
.submitted-inner {
  text-align: center; max-width: 440px;
  animation: fadeInUp 0.5s ease;
}
.submitted-icon {
  width: 80px; height: 80px; margin: 0 auto 24px;
  border-radius: 50%; background: linear-gradient(135deg, #10B981, #34D399);
  color: #fff; font-size: 40px; font-weight: 700; line-height: 80px;
  box-shadow: 0 8px 24px rgba(16, 185, 129, 0.3);
}
.submitted-inner h2 {
  font-size: 24px; font-weight: 700; margin-bottom: 8px;
  color: var(--color-text-primary);
}
.submitted-inner p {
  font-size: 15px; color: var(--color-text-secondary);
  margin-bottom: 24px;
}
.submitted-info {
  display: inline-block; padding: 8px 20px;
  background: var(--color-bg); border-radius: 20px;
  font-size: 13px; color: var(--color-text-tertiary);
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
