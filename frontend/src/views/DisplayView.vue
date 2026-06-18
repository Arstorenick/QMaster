<template>
  <div class="display-page" v-if="survey" :style="pageStyle">
    <div class="display-container">
      <template v-for="page in pages" :key="page.index">
        <div class="display-card card" v-show="page.index === currentPage">
          <!-- Logo -->
          <div class="display-logo" v-if="style?.logo_image" :style="{ backgroundColor: style?.logo_bg_color || '#fff' }">
            <img :src="style.logo_image" alt="Logo" />
          </div>
          <!-- Header Image -->
          <img v-if="style?.header_image" :src="style.header_image" class="display-header-img" alt="Header" />
          <!-- Title -->
          <div class="display-header" v-if="style?.show_title || style?.show_description">
            <h1 v-if="style?.show_title">{{ survey.title }}</h1>
            <p v-if="style?.show_description" class="text-secondary">{{ survey.description }}</p>
          </div>

          <!-- Progress -->
          <div class="progress-bar" v-if="style?.show_progress && pages.length > 1">
            <div class="progress-fill" :style="{ width: ((currentPage + 1) / pages.length * 100) + '%' }"></div>
            <span class="progress-text">{{ currentPage + 1 }} / {{ pages.length }}</span>
          </div>

          <!-- Questions -->
          <template v-for="q in page.questions" :key="q.id">
            <!-- Section Break: standalone centered title -->
            <div v-if="q.type === 'section_break'" class="section-break-title">{{ q.title || '章节标题' }}</div>

            <!-- Regular Question -->
            <div v-else class="display-question">
            <div class="dq-title">
              <span v-if="style?.show_question_number" class="dq-num">{{ getQNumber(q.id) }}</span>
              <span>{{ q.title }}</span>
              <span v-if="q.is_required" class="dq-required">*</span>
              <span v-if="style?.show_question_type" class="tag tag-primary text-sm">{{ typeLabels[q.type] }}</span>
              <span v-if="style?.show_question_score" class="tag" style="background:var(--color-warning-light);color:#92400E;border-color:#FCD34D">{{ q.score || 0 }} 分</span>
            </div>

            <!-- Radio -->
            <div v-if="q.type === 'radio'" class="dq-options">
              <label v-for="opt in q.options" :key="opt.id" class="dq-option">
                <input type="radio" :name="'q-' + q.id" :value="opt.id" v-model="answers[q.id]" />
                <span>{{ opt.title }}</span>
              </label>
            </div>

            <!-- Checkbox -->
            <div v-if="q.type === 'checkbox'" class="dq-options">
              <label v-for="opt in q.options" :key="opt.id" class="dq-option">
                <input type="checkbox" :value="opt.id" v-model="answers[q.id]" />
                <span>{{ opt.title }}</span>
              </label>
            </div>

            <!-- Text -->
            <textarea
              v-if="q.type === 'text' || q.type === 'textarea'"
              class="input"
              :rows="q.config?.rows || 3"
              v-model="answers[q.id]"
              :placeholder="q.config?.placeholder || '请输入'"
            ></textarea>

            <!-- Rating -->
            <div v-if="q.type === 'rating'" class="dq-rating">
              <span
                v-for="i in (q.config?.max_score || 5)" :key="i"
                class="rating-star"
                :class="{ active: answers[q.id] >= i }"
                @click="answers[q.id] = i"
              >★</span>
            </div>

            <!-- Dropdown -->
            <select v-if="q.type === 'dropdown'" class="input" v-model="answers[q.id]">
              <option value="">请选择</option>
              <option v-for="opt in q.options" :key="opt.id" :value="opt.id">{{ opt.title }}</option>
            </select>

            <!-- Scale -->
            <div v-if="q.type === 'scale'" class="dq-scale">
              <span class="text-sm">{{ q.config?.left_label }}</span>
              <label v-for="i in (q.config?.scale || 5)" :key="i" class="scale-radio">
                <input type="radio" :value="i" v-model="answers[q.id]" />
                <span>{{ i }}</span>
              </label>
              <span class="text-sm">{{ q.config?.right_label }}</span>
            </div>

            <!-- Slider -->
            <div v-if="q.type === 'slider'" class="dq-slider">
              <input type="range" :min="q.config?.min || 0" :max="q.config?.max || 100" :step="q.config?.step || 1" v-model="answers[q.id]" />
              <span class="slider-value">{{ answers[q.id] || q.config?.default || 0 }}{{ q.config?.unit || '' }}</span>
            </div>

            <!-- Date / Time -->
            <div v-if="q.type === 'date' || q.type === 'time'" class="dq-datetime">
              <div v-if="(q.config?.mode || 'datetime') !== 'time'" class="dt-field">
                <span class="dt-field-icon">📅</span>
                <input type="date" class="dt-input" v-model="answers[q.id + '_date']" />
              </div>
              <div v-if="(q.config?.mode || 'datetime') !== 'date'" class="dt-field">
                <span class="dt-field-icon">🕐</span>
                <input type="time" class="dt-input" v-model="answers[q.id + '_time']" />
              </div>
            </div>

            <!-- File Upload (basic) -->
            <div v-if="q.type === 'file_upload'">
              <input type="file" @change="e => handleFileUpload(q, e)" />
              <span v-if="fileNames[q.id]" class="text-sm text-secondary">已选择: {{ fileNames[q.id] }}</span>
            </div>

            <!-- Ranking -->
            <div v-if="q.type === 'ranking'" class="dq-ranking">
              <div class="dq-ranking-hint">上下拖拽选项进行排序（越靠上优先级越高）</div>
              <draggable
                v-model="rankingOrders[q.id]"
                item-key="id"
                handle=".ranking-drag-handle"
                ghost-class="ranking-ghost"
                :animation="200"
              >
                <template #item="{ element: opt, index }">
                  <div class="dq-ranking-item">
                    <span class="ranking-drag-handle">⠿</span>
                    <span class="ranking-pos">{{ index + 1 }}</span>
                    <span class="dq-ranking-label">{{ opt.title }}</span>
                  </div>
                </template>
              </draggable>
            </div>

            <!-- Image Radio -->
            <div v-if="q.type === 'image_radio'" class="dq-image-options">
              <label v-for="opt in q.options" :key="opt.id" class="dq-image-option" :class="{ selected: answers[q.id] === opt.id }">
                <img v-if="opt.image" :src="opt.image" :alt="opt.title" />
                <input type="radio" :value="opt.id" v-model="answers[q.id]" />
                <span>{{ opt.title }}</span>
              </label>
            </div>

            <!-- Image Checkbox -->
            <div v-if="q.type === 'image_checkbox'" class="dq-image-options">
              <label v-for="opt in q.options" :key="opt.id" class="dq-image-option" :class="{ selected: (answers[q.id] || []).includes(opt.id) }">
                <img v-if="opt.image" :src="opt.image" :alt="opt.title" />
                <input type="checkbox" :value="opt.id" v-model="answers[q.id]" />
                <span>{{ opt.title }}</span>
              </label>
            </div>

          </div>
          </template>

          <!-- Page Navigation -->
          <div class="display-nav" v-if="pages.length > 1">
            <button class="btn btn-secondary" v-if="currentPage > 0" @click="currentPage--">上一页</button>
            <div class="flex-1"></div>
            <button class="btn btn-primary" v-if="currentPage < pages.length - 1" @click="currentPage++">下一页</button>
            <button class="btn btn-primary btn-lg" v-if="currentPage === pages.length - 1" @click="submit">提交问卷</button>
          </div>
          <div class="display-nav" v-else>
            <button class="btn btn-primary btn-lg" @click="submit">提交问卷</button>
          </div>
        </div>
      </template>
    </div>
  </div>
  <div v-else class="text-center" style="padding:100px">
    <p>加载中...</p>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { surveysAPI, responsesAPI } from '../api'
import draggable from 'vuedraggable'

const route = useRoute()
const router = useRouter()

const survey = ref(null)
const answers = reactive({})
const fileNames = reactive({})
const rankingOrders = reactive({})
const currentPage = ref(0)
const startTime = Date.now()

const style = computed(() => survey.value?.style || {})
const typeLabels = {
  radio: '单选', checkbox: '多选', text: '填空', textarea: '多行文本',
  dropdown: '单选', rating: '评分', ranking: '排序', scale: '量表',
  slider: '滑块', date: '日期', time: '时间',
  file_upload: '上传', image_radio: '图片单选', image_checkbox: '图片多选',
}

const pageStyle = computed(() => {
  const s = style.value || {}
  return {
    '--survey-theme': s.theme_color || '#2563EB',
    '--survey-bg': s.bg_color || '#F0F4FF',
    '--survey-progress': s.progress_color || s.theme_color || '#2563EB',
    '--survey-logo-bg': s.logo_bg_color || '#FFFFFF',
    backgroundColor: 'var(--survey-bg)',
    backgroundImage: s.bg_image ? `url(${s.bg_image})` : 'none',
    backgroundSize: 'cover',
    backgroundPosition: 'center',
  }
})

function initRankingOrders() {
  if (!survey.value?.questions) return
  for (const q of survey.value.questions) {
    if (q.type === 'ranking' && q.options?.length) {
      if (!rankingOrders[q.id]) {
        rankingOrders[q.id] = [...q.options]
      }
    }
  }
}

onMounted(async () => {
  try {
    const { data } = await surveysAPI.public(route.params.id)
    survey.value = data
    initRankingOrders()
  } catch {
    router.push('/')
  }
})

// Split questions into pages
const pages = computed(() => {
  if (!survey.value?.questions) return []
  const result = []
  let current = { index: 0, questions: [] }
  for (const q of survey.value.questions) {
    if (q.type === 'page_break') {
      if (current.questions.length) result.push(current)
      current = { index: result.length, questions: [] }
    } else if (q.type === 'section_break') {
      current.questions.push(q)
    } else {
      current.questions.push(q)
    }
  }
  if (current.questions.length) result.push(current)
  return result.length ? result : [{ index: 0, questions: survey.value.questions }]
})

function getQNumber(qId) {
  if (!survey.value) return ''
  let count = 0
  for (const q of survey.value.questions) {
    if (q.id === qId) return count + 1 + '.'
    if (q.type !== 'page_break' && q.type !== 'section_break') count++
  }
  return ''
}

function handleFileUpload(q, event) {
  const file = event.target.files[0]
  if (file) fileNames[q.id] = file.name
  answers[q.id] = file
}

async function submit() {
  // Build answers payload
  const answerList = []
  for (const page of pages.value) {
    for (const q of page.questions) {
      const payload = { question: q.id }
      if (q.type === 'checkbox' || q.type === 'image_checkbox') {
        const vals = answers[q.id]
        if (Array.isArray(vals) && vals.length) {
          for (const optId of vals) {
            answerList.push({ question: q.id, option: optId })
          }
        }
        continue
      }
      if (q.type === 'radio' || q.type === 'dropdown') {
        payload.option = answers[q.id]
      } else if (q.type === 'rating' || q.type === 'scale' || q.type === 'slider') {
        payload.answer_number = Number(answers[q.id]) || 0
      } else if (q.type === 'text' || q.type === 'textarea') {
        payload.answer_text = answers[q.id] || ''
      } else if (q.type === 'date') {
        payload.answer_json = {}
        if ((q.config?.mode || 'datetime') !== 'time') payload.answer_json.date = answers[q.id + '_date'] || ''
        if ((q.config?.mode || 'datetime') !== 'date') payload.answer_json.time = answers[q.id + '_time'] || ''
      } else if (q.type === 'time') {
        payload.answer_text = answers[q.id] || ''
      } else if (q.type === 'ranking') {
        payload.answer_json = {}
        const order = rankingOrders[q.id] || q.options
        order.forEach((opt, idx) => {
          payload.answer_json[opt.id] = idx + 1
        })
      }
      if (payload.option || payload.answer_text || payload.answer_number !== undefined || payload.answer_json) {
        answerList.push(payload)
      }
    }
  }

  const duration = Math.floor((Date.now() - startTime) / 1000)
  try {
    await responsesAPI.submit(survey.value.id, {
      answers: answerList,
      duration_seconds: duration,
    })
    router.push('/thankyou')
  } catch (e) {
    const detail = e.response?.data?.detail
    if (detail) {
      alert(typeof detail === 'string' ? detail : `请完成所有必填题目：${detail.missing_questions?.join('、')}`)
    } else {
      alert('提交失败，请重试')
    }
  }
}
</script>

<style scoped>
.display-page {
  min-height: calc(100vh - var(--header-height));
  background: var(--survey-bg);
}
.display-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: var(--spacing-lg);
}
.display-logo { text-align: center; padding: var(--spacing-md); border-radius: var(--radius-md) var(--radius-md) 0 0; }
.display-logo img { max-height: 60px; }
.display-header-img { width: 100%; max-height: 200px; object-fit: cover; border-radius: var(--radius-md) var(--radius-md) 0 0; }
.display-card {
  padding: var(--spacing-lg);
  margin-bottom: var(--spacing-md);
  border-radius: var(--radius-md);
  border-top: 3px solid var(--survey-theme);
}
.display-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
  padding-bottom: var(--spacing-lg);
  border-bottom: 2px solid color-mix(in srgb, var(--survey-theme) 12%, transparent);
}
.display-header h1 {
  font-size: var(--font-size-xl);
  color: var(--survey-theme);
}
.progress-bar {
  height: 6px;
  background: var(--color-border-light);
  border-radius: 3px;
  margin-bottom: var(--spacing-xl);
  position: relative;
}
.progress-fill {
  height: 100%;
  background: var(--survey-progress);
  border-radius: 3px;
  transition: width var(--transition-normal);
}
.progress-text {
  position: absolute;
  right: 0;
  top: -20px;
  font-size: var(--font-size-xs);
  font-weight: 600;
  color: var(--survey-theme);
}
.dq-num { color: var(--survey-theme); }
.btn-primary { background: var(--survey-theme); border-color: var(--survey-theme); }
.btn-primary:hover { background: var(--survey-theme); filter: brightness(0.9); }
input[type="radio"], input[type="checkbox"] { accent-color: var(--survey-theme); }
select { border-color: color-mix(in srgb, var(--survey-theme) 20%, transparent); }
.display-question {
  padding: var(--spacing-lg) 0;
  border-bottom: 1px solid color-mix(in srgb, var(--survey-theme) 10%, transparent);
}
.dq-title {
  font-size: var(--font-size-base);
  font-weight: 500;
  margin-bottom: var(--spacing-md);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  flex-wrap: wrap;
}
.dq-num {
  color: var(--survey-theme);
  font-weight: 600;
}
.dq-required { color: var(--color-danger); font-weight: 600; }
.dq-options { display: flex; flex-direction: column; gap: var(--spacing-sm); }
.dq-option {
  display: flex; align-items: center; gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid color-mix(in srgb, var(--survey-theme) 15%, transparent);
  border-radius: var(--radius-md);
  cursor: pointer; transition: all var(--transition-fast);
}
.dq-option:hover {
  border-color: var(--survey-theme);
  background: color-mix(in srgb, var(--survey-theme) 6%, transparent);
}
.dq-ranking { display: flex; flex-direction: column; gap: var(--spacing-xs); }
.dq-ranking-hint { font-size: 12px; color: var(--color-text-tertiary); margin-bottom: 8px; }
.dq-ranking-item {
  display: flex; align-items: center; gap: var(--spacing-sm);
  padding: 10px 14px;
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  background: var(--color-bg-white);
  transition: all 0.15s ease;
  cursor: default;
}
.dq-ranking-item:hover { border-color: var(--survey-theme); box-shadow: var(--shadow-sm); }
.ranking-drag-handle {
  font-size: 18px; color: var(--color-text-tertiary);
  cursor: grab; flex-shrink: 0; line-height: 1;
  padding: 2px;
}
.ranking-drag-handle:active { cursor: grabbing; }
.ranking-pos {
  width: 26px; height: 26px;
  display: flex; align-items: center; justify-content: center;
  background: var(--survey-theme); color: #fff;
  border-radius: 50%;
  font-size: 12px; font-weight: 700;
  flex-shrink: 0;
}
.ranking-ghost {
  opacity: 0.4;
  background: color-mix(in srgb, var(--survey-theme) 12%, transparent);
  border: 2px dashed var(--survey-theme);
}
.dq-ranking-label { font-size: 14px; font-weight: 500; }
.dq-rating {
  display: flex;
  gap: 4px;
}
.rating-star {
  font-size: 32px;
  color: var(--color-border);
  cursor: pointer;
  transition: color var(--transition-fast);
}
.rating-star.active, .rating-star:hover {
  color: var(--color-warning);
}
.dq-scale {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}
.scale-radio {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  cursor: pointer;
}
.dq-slider {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}
.dq-slider input[type="range"] {
  flex: 1;
  accent-color: var(--survey-theme);
}
.slider-value {
  font-weight: 600;
  font-size: var(--font-size-lg);
  min-width: 60px;
}
.dq-image-options {
  display: flex;
  gap: var(--spacing-md);
  flex-wrap: wrap;
}
.dq-image-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm);
  border: 2px solid var(--color-border-light);
  border-radius: var(--radius-md);
  cursor: pointer;
}
.dq-image-option.selected {
  border-color: var(--survey-theme);
}
.dq-image-option img {
  max-width: 120px;
  height: auto;
}
.section-break-title { text-align: center; font-size: 22px; font-weight: 700; padding: var(--spacing-lg) 0; color: var(--survey-theme); }
.dq-datetime { display: flex; gap: var(--spacing-sm); }
.dt-field {
  flex: 0 1 240px; min-width: 0;
  display: flex; align-items: center;
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  background: var(--color-bg-white);
  overflow: hidden;
  transition: all 0.2s ease;
}
.dt-field:focus-within {
  border-color: var(--survey-theme);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--survey-theme) 15%, transparent);
}
.dt-field-icon {
  font-size: 18px; padding: 0 12px; flex-shrink: 0;
  opacity: 0.7;
}
.dt-field:focus-within .dt-field-icon { opacity: 1; }
.dt-input {
  flex: 1; min-width: 0;
  padding: 10px 10px 10px 0;
  border: none; outline: none;
  font-size: 15px; font-family: var(--font-family);
  color: var(--color-text-primary);
  background: transparent;
}
.dt-input::-webkit-calendar-picker-indicator {
  cursor: pointer; padding: 4px 8px;
  opacity: 0.5; transition: opacity 0.15s;
}
.dt-input::-webkit-calendar-picker-indicator:hover { opacity: 1; }
.display-nav {
  display: flex;
  gap: var(--spacing-md);
  margin-top: var(--spacing-xl);
  justify-content: center;
  align-items: center;
}
.display-nav .btn-primary {
  background: var(--survey-theme) !important;
  border-color: var(--survey-theme) !important;
  color: #fff !important;
}
.display-nav .btn-primary:hover {
  background: var(--survey-theme) !important;
  filter: brightness(0.9);
}
.display-nav .btn-secondary {
  border-color: var(--survey-theme) !important;
  color: var(--survey-theme) !important;
  background: transparent !important;
}
.display-nav .btn-secondary:hover {
  background: color-mix(in srgb, var(--survey-theme) 8%, transparent) !important;
}
.flex-1 { flex: 1; }
</style>
