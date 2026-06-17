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

            <!-- Text / Textarea -->
            <textarea
              v-if="q.type === 'text' || q.type === 'textarea'"
              class="input"
              :rows="q.type === 'textarea' ? (q.config?.rows || 3) : 1"
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
            <input v-if="q.type === 'date'" class="input" type="date" v-model="answers[q.id]" style="max-width:240px" />
            <input v-if="q.type === 'time'" class="input" type="time" v-model="answers[q.id]" style="max-width:240px" />

            <!-- File Upload (basic) -->
            <div v-if="q.type === 'file_upload'">
              <input type="file" @change="e => handleFileUpload(q, e)" />
              <span v-if="fileNames[q.id]" class="text-sm text-secondary">已选择: {{ fileNames[q.id] }}</span>
            </div>

            <!-- Ranking -->
            <div v-if="q.type === 'ranking'" class="dq-options">
              <div v-for="opt in q.options" :key="opt.id" class="dq-option">
                <input type="number" :min="1" :max="q.options.length" v-model="answers[q.id + '_' + opt.id]" style="width:60px" class="input" />
                <span>{{ opt.title }}</span>
              </div>
            </div>

            <!-- Multi text -->
            <div v-if="q.type === 'multi_text'" class="dq-multi-text">
              <div v-for="(field, fi) in (q.config?.fields || [])" :key="fi" class="form-group">
                <label>{{ field.label }}</label>
                <input class="input" :placeholder="field.placeholder" v-model="answers[q.id + '_field_' + fi]" />
              </div>
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

const route = useRoute()
const router = useRouter()

const survey = ref(null)
const answers = reactive({})
const fileNames = reactive({})
const currentPage = ref(0)
const startTime = Date.now()

const style = computed(() => survey.value?.style || {})
const typeLabels = {
  radio: '单选', checkbox: '多选', text: '填空', textarea: '多行文本',
  dropdown: '单选', rating: '评分', ranking: '排序', scale: '量表',
  slider: '滑块', date: '日期', time: '时间', multi_text: '多项填空',
  file_upload: '上传', image_radio: '图片单选', image_checkbox: '图片多选',
}

const pageStyle = computed(() => {
  const s = style.value || {}
  return {
    '--survey-theme': s.theme_color || '#4F46E5',
    '--survey-bg': s.bg_color || '#F9FAFB',
    '--survey-progress': s.progress_color || s.theme_color || '#4F46E5',
    '--survey-logo-bg': s.logo_bg_color || '#FFFFFF',
    backgroundColor: 'var(--survey-bg)',
    backgroundImage: s.bg_image ? `url(${s.bg_image})` : 'none',
    backgroundSize: 'cover',
    backgroundPosition: 'center',
  }
})

onMounted(async () => {
  try {
    const { data } = await surveysAPI.public(route.params.id)
    survey.value = data
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
      } else if (q.type === 'date' || q.type === 'time') {
        payload.answer_text = answers[q.id] || ''
      } else if (q.type === 'multi_text') {
        payload.answer_json = {}
        for (const fi in (q.config?.fields || [])) {
          payload.answer_json[`field_${fi}`] = answers[q.id + '_field_' + fi] || ''
        }
      } else if (q.type === 'ranking') {
        payload.answer_json = {}
        for (const opt of q.options) {
          payload.answer_json[opt.id] = Number(answers[q.id + '_' + opt.id]) || 0
        }
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
}
.display-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
  padding-bottom: var(--spacing-lg);
  border-bottom: 1px solid var(--color-border-light);
}
.display-header h1 {
  font-size: var(--font-size-xl);
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
  color: var(--color-text-secondary);
}
.dq-num { color: var(--survey-theme); }
.btn-primary { background: var(--survey-theme); border-color: var(--survey-theme); }
.btn-primary:hover { background: var(--survey-theme); filter: brightness(0.9); }
.display-question {
  padding: var(--spacing-lg) 0;
  border-bottom: 1px solid var(--color-border-light);
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
  color: var(--color-primary);
  font-weight: 600;
}
.dq-required {
  color: var(--color-danger);
  font-weight: 600;
}
.dq-options {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}
.dq-option {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}
.dq-option:hover {
  border-color: var(--color-primary);
  background: var(--color-primary-light);
}
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
  accent-color: var(--color-primary);
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
  border-color: var(--color-primary);
}
.dq-image-option img {
  max-width: 120px;
  height: auto;
}
.section-break-title { text-align: center; font-size: 22px; font-weight: 700; padding: var(--spacing-lg) 0; color: var(--color-text-primary); }
.dq-multi-text {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}
.display-nav {
  display: flex;
  gap: var(--spacing-md);
  margin-top: var(--spacing-xl);
  justify-content: center;
}
.flex-1 { flex: 1; }
</style>
