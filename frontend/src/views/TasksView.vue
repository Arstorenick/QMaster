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
        <div class="display-card card" v-if="!submitted">
          <div class="display-header" v-if="activeSurvey.style?.show_title !== false">
            <h2>{{ activeSurvey.title }}</h2>
            <p class="text-secondary text-sm" v-if="activeSurvey.description">{{ activeSurvey.description }}</p>
          </div>
          <div v-for="q in activeQuestions" :key="q.id" class="display-q">
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
          </div>
          <div style="text-align:center;margin-top:var(--spacing-xl)">
            <button class="btn btn-primary btn-lg" @click="submitSurvey" :disabled="submitting">
              {{ submitting ? '提交中...' : '提交问卷' }}
            </button>
          </div>
        </div>
        <div class="card text-center" v-else style="padding:var(--spacing-2xl)">
          <p style="font-size:48px">✅</p>
          <h3>已完成提交</h3>
          <p class="text-secondary mt-sm">感谢您的参与！</p>
        </div>
      </template>
      <div v-else class="tasks-empty text-center">
        <p style="font-size:48px;margin-bottom:16px">📝</p>
        <h3>{{ tasks.length ? '选择左侧问卷开始答题' : '暂无待完成问卷' }}</h3>
        <p class="text-secondary mt-sm">部门推送的问卷会显示在这里</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { surveysAPI, responsesAPI, departmentsAPI } from '../api'

const auth = useAuthStore()
const tasks = ref([])
const activeSurvey = ref(null)
const activeQuestions = ref([])
const answers = reactive({})
const submitted = ref(false)
const submitting = ref(false)

onMounted(loadTasks)

async function loadTasks() {
  const { data } = await surveysAPI.publicList().catch(() => ({ data: [] }))
  tasks.value = data.map(s => ({ ...s, submitted: false, dept_name: '公开' }))
}

function isAncestor(targetId, deptId) {
  // Simplified: check if target is ancestor via flat list
  // The full implementation would check the department tree
  return false
}

async function openSurvey(survey) {
  const { data } = await surveysAPI.public(survey.id)
  activeSurvey.value = data
  activeQuestions.value = data.questions?.filter(q => !['page_break','section_break','divider'].includes(q.type)) || []
  // Reset answers
  for (const key in answers) delete answers[key]
  for (const q of activeQuestions.value) {
    if (q.type === 'checkbox') answers[q.id] = []
  }
  submitted.value = false
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

async function submitSurvey() {
  const answerList = []
  for (const q of activeQuestions.value) {
    const val = answers[q.id]
    if (!val && q.is_required && !(Array.isArray(val) && val.length)) continue
    const payload = { question: q.id }
    if (q.type === 'checkbox') {
      if (Array.isArray(val)) {
        for (const optId of val) answerList.push({ question: q.id, option: optId })
      }
      continue
    }
    if (['radio','dropdown'].includes(q.type)) payload.option = val
    else if (['rating','scale','slider'].includes(q.type)) payload.answer_number = Number(val) || 0
    else payload.answer_text = val || ''
    answerList.push(payload)
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
.task-item { padding: var(--spacing-sm) var(--spacing-md); border-radius: var(--radius-md); cursor: pointer; margin-bottom: 2px; transition: all var(--transition-fast); }
.task-item:hover { background: var(--color-bg-hover); }
.task-item.active { background: var(--color-primary-light); }
.task-item-title { font-size: var(--font-size-sm); font-weight: 500; margin-bottom: 4px; }
.task-item-meta { display: flex; align-items: center; gap: var(--spacing-sm); }
.tasks-main { flex:1; overflow-y: auto; background: var(--color-bg); }
.tasks-empty { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; }
.display-card { max-width: 700px; margin: var(--spacing-xl) auto; padding: var(--spacing-xl); }
.display-header { text-align: center; margin-bottom: var(--spacing-xl); padding-bottom: var(--spacing-lg); border-bottom: 1px solid var(--color-border-light); }
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
</style>
