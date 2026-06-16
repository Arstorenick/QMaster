<template>
  <div class="editor-layout">
    <!-- Question Type Toolbar -->
    <div class="type-toolbar" v-if="!readonly">
      <div class="type-group" v-for="group in typeGroups" :key="group.label">
        <span class="type-group-label">{{ group.label }}</span>
        <div class="type-buttons">
          <button
            v-for="t in group.types" :key="t.value"
            class="type-btn"
            @click="addQuestion(t.value)"
          ><span class="type-btn-icon">{{ t.icon }}</span><span class="type-btn-label">{{ t.label }}</span></button>
        </div>
      </div>
    </div>

    <!-- Question List -->
    <draggable
      :list="questions"
      class="question-list"
      item-key="id"
      handle=".drag-handle"
      ghost-class="drag-ghost"
      :animation="200"
      @start="dragging = true"
      @end="onDragEnd"
    >
      <template #item="{ element: q, index }">
      <div
        class="question-card card"
        :class="{ 'is-page-break': q.type === 'page_break', 'is-section-break': q.type === 'section_break', 'is-dragging': dragging }"
      >
        <!-- Page Break -->
        <template v-if="q.type === 'page_break'">
          <div class="break-label">
            <span class="drag-handle break-handle">⠿</span>
            ═══ 分页 ═══
            <button v-if="!readonly" class="btn btn-ghost btn-sm" @click="deleteQuestion(q.id)">删除</button>
          </div>
        </template>
        <!-- Section Break -->
        <template v-else-if="q.type === 'section_break'">
          <div class="section-editor">
            <span class="drag-handle break-handle">⠿</span>
            <input
              v-model="q.title"
              class="section-title-input"
              placeholder="输入章节标题"
              :disabled="readonly"
              @blur="updateQuestion(q)"
            />
            <button v-if="!readonly" class="btn btn-ghost btn-sm" @click="deleteQuestion(q.id)">删除</button>
          </div>
        </template>

        <!-- Regular Question -->
        <template v-else>
          <div class="q-header">
            <span class="drag-handle" title="拖拽排序" v-if="!readonly">⠿</span>
            <span class="q-number">{{ getQNumber(index) }}</span>
            <span class="q-type-tag tag tag-primary">{{ getTypeLabel(q.type) }}</span>
            <input
              v-model="q.title"
              class="q-title-input"
              placeholder="请输入题目标题"
              :disabled="readonly"
              @blur="updateQuestion(q)"
            />
            <div class="q-header-actions">
              <label class="required-toggle" v-if="!readonly">
                <input type="checkbox" v-model="q.is_required" @change="updateQuestion(q)" />
                <span>必填</span>
              </label>
              <button v-if="!readonly" class="btn btn-ghost btn-sm" @click="deleteQuestion(q.id)">删除</button>
            </div>
          </div>

          <!-- Options for choice types -->
          <div class="q-options" v-if="hasOptions(q.type)">
            <div v-for="opt in q.options" :key="opt.id" class="option-row">
              <span class="option-marker">{{ q.type === 'checkbox' ? '☐' : '○' }}</span>
              <input
                v-model="opt.title"
                class="input option-input"
                :placeholder="`选项 ${opt.order + 1}`"
                :disabled="readonly"
                @blur="updateOption(q, opt)"
              />
              <button v-if="!readonly" class="btn btn-ghost btn-sm" @click="deleteOption(q, opt.id)" style="color:var(--color-danger)">×</button>
            </div>
            <button v-if="!readonly" class="btn btn-ghost btn-sm add-option-btn" @click="addOption(q)">+ 添加选项</button>
          </div>

          <!-- Text area preview -->
          <div v-else-if="q.type === 'text' || q.type === 'textarea'">
            <textarea
              class="input"
              :rows="q.config?.rows || (q.type === 'textarea' ? 3 : 1)"
              disabled
              :placeholder="`${q.type === 'textarea' ? '多行' : ''}文本回答区域`"
              style="opacity:0.5"
            ></textarea>
          </div>

          <!-- Rating preview -->
          <div v-else-if="q.type === 'rating'" class="rating-preview">
            <span v-for="i in (q.config?.max_score || 5)" :key="i">★</span>
          </div>

          <!-- Slider preview -->
          <div v-else-if="q.type === 'slider'" class="slider-preview">
            <input type="range" :min="q.config?.min || 0" :max="q.config?.max || 100" disabled style="width:100%" />
          </div>

          <!-- Scale preview -->
          <div v-else-if="q.type === 'scale'" class="scale-preview">
            <div class="scale-row">
              <span>{{ q.config?.left_label || '1' }}</span>
              <span v-for="i in (q.config?.scale || 5)" :key="i" class="scale-dot">{{ i }}</span>
              <span>{{ q.config?.right_label || '5' }}</span>
            </div>
          </div>

          <!-- Default preview for other types -->
          <div v-else class="q-preview-placeholder text-secondary text-sm">
            [{{ getTypeLabel(q.type) }}] — 在问卷填写端生效
          </div>
        </template>
      </div>
      </template>
    </draggable>
    <div v-if="!questions.length" class="editor-empty">
      <p style="font-size:40px;margin-bottom:12px">📝</p>
      <p class="text-secondary">点击上方题型按钮添加题目</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import draggable from 'vuedraggable'
import { questionsAPI, optionsAPI } from '../../api'

const props = defineProps({
  survey: Object,
  questions: Array,
  readonly: { type: Boolean, default: false },
})
const emit = defineEmits(['refresh'])

const dragging = ref(false)

async function onDragEnd() {
  dragging.value = false
  const ids = props.questions.map(q => q.id)
  await questionsAPI.reorder(props.survey.id, ids)
}

const typeGroups = [
  {
    label: '基础',
    types: [
      { value: 'radio', label: '单选', icon: '⭕' },
      { value: 'checkbox', label: '多选', icon: '☑️' },
      { value: 'text', label: '填空', icon: '✏️' },
      { value: 'textarea', label: '多行文本', icon: '📝' },
      { value: 'dropdown', label: '下拉', icon: '📋' },
    ],
  },
  {
    label: '高级',
    types: [
      { value: 'rating', label: '评分', icon: '⭐' },
      { value: 'ranking', label: '排序', icon: '🔢' },
      { value: 'scale', label: '量表', icon: '📏' },
      { value: 'slider', label: '滑块', icon: '🎚️' },
      { value: 'multi_text', label: '多项填空', icon: '📋' },
    ],
  },
  {
    label: '其他',
    types: [
      { value: 'date', label: '日期', icon: '📅' },
      { value: 'time', label: '时间', icon: '🕐' },
      { value: 'file_upload', label: '上传', icon: '📎' },
      { value: 'image_radio', label: '图片单选', icon: '🖼️' },
      { value: 'image_checkbox', label: '图片多选', icon: '🖼️' },
    ],
  },
  {
    label: '结构',
    types: [
      { value: 'page_break', label: '分页', icon: '📄' },
      { value: 'section_break', label: '章节标题', icon: '📑' },
    ],
  },
]

function getTypeLabel(type) {
  for (const g of typeGroups) {
    const found = g.types.find(t => t.value === type)
    if (found) return found.label
  }
  return type
}

function getQNumber(currentIndex) {
  let count = 0
  for (let i = 0; i <= currentIndex; i++) {
    const t = props.questions[i]?.type
    if (t !== 'page_break' && t !== 'section_break') count++
  }
  return count
}

function hasOptions(type) {
  return ['radio', 'checkbox', 'dropdown', 'image_radio', 'image_checkbox', 'ranking'].includes(type)
}

async function addQuestion(type) {
  try {
    const config = getDefaultConfig(type)
    await questionsAPI.create(props.survey.id, {
      type,
      title: '未命名题目',
      config,
      options: hasOptions(type) ? [{ title: '选项 1', order: 0 }] : [],
    })
    emit('refresh')
  } catch (e) {
    alert('添加题目失败: ' + (e.response?.data?.detail || e.message))
  }
}

function getDefaultConfig(type) {
  const defaults = {
    rating: { max_score: 5 },
    scale: { scale: 5, left_label: '非常不同意', right_label: '非常同意' },
    slider: { min: 0, max: 100, step: 1 },
    textarea: { rows: 3 },
    multi_text: { fields: [{ label: '', placeholder: '' }] },
    date: { format: 'yyyy-mm-dd' },
    time: { format: 'hh:mm' },
  }
  return defaults[type] || {}
}

async function updateQuestion(q) {
  await questionsAPI.update(props.survey.id, q.id, {
    title: q.title,
    is_required: q.is_required,
    type: q.type,
    config: q.config,
  })
}

async function deleteQuestion(qId) {
  if (!confirm('确定删除此题？')) return
  await questionsAPI.delete(props.survey.id, qId)
  emit('refresh')
}

async function addOption(q) {
  await optionsAPI.create(props.survey.id, q.id, { title: '新选项' })
  emit('refresh')
}

async function updateOption(q, opt) {
  await optionsAPI.update(props.survey.id, q.id, opt.id, { title: opt.title })
}

async function deleteOption(q, optId) {
  await optionsAPI.delete(props.survey.id, q.id, optId)
  emit('refresh')
}
</script>

<style scoped>
.editor-layout {
  padding: var(--spacing-lg);
  max-width: 1400px;
  margin: 0 auto;
}
.type-toolbar {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-lg);
  padding: var(--spacing-md);
  background: var(--color-bg-white);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border-light);
}
.type-group {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}
.type-group-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  width: 40px;
  flex-shrink: 0;
}
.type-buttons {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}
.type-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  width: 110px;
  border: 1px solid var(--color-border-light);
  background: var(--color-bg-white);
  border-radius: var(--radius-md);
  cursor: pointer;
  font-family: var(--font-family);
  transition: all var(--transition-fast);
  white-space: nowrap;
}
.type-btn:hover {
  border-color: var(--color-primary);
  background: var(--color-primary-light);
}
.type-btn-icon {
  font-size: 18px;
  line-height: 1;
}
.type-btn-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}
.editor-empty {
  text-align: center;
  padding: var(--spacing-2xl);
}
.drag-handle {
  cursor: grab;
  font-size: 18px;
  color: var(--color-text-tertiary);
  user-select: none;
  padding: 0 4px;
  transition: color var(--transition-fast);
}
.drag-handle:hover {
  color: var(--color-primary);
}
.drag-handle:active {
  cursor: grabbing;
}
.break-handle {
  font-size: 14px;
}
.drag-ghost {
  opacity: 0.4;
  background: var(--color-primary-light);
  border: 2px dashed var(--color-primary);
}
.question-card {
  padding: var(--spacing-lg);
  margin-bottom: var(--spacing-md);
}
.question-card.is-dragging {
  cursor: grabbing;
}
.question-card.is-page-break {
  text-align: center;
  background: var(--color-bg);
  border: 1px dashed var(--color-border);
}
.question-card.is-section-break {
  text-align: center;
  background: var(--color-bg);
  border: none;
}
.section-editor {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}
.section-title-input {
  flex: 1;
  border: none;
  text-align: center;
  font-size: 20px;
  font-weight: 700;
  font-family: var(--font-family);
  color: var(--color-text-primary);
  padding: 8px 16px;
  outline: none;
  border-bottom: 2px solid transparent;
  transition: border-color var(--transition-fast);
}
.section-title-input:focus {
  border-bottom-color: var(--color-primary);
}
.section-title-input::placeholder {
  color: var(--color-text-placeholder);
  font-weight: 400;
}
.break-label {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-md);
}
.q-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
}
.q-number {
  width: 28px;
  height: 28px;
  background: var(--color-primary);
  color: #fff;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-xs);
  font-weight: 600;
  flex-shrink: 0;
}
.q-type-tag {
  flex-shrink: 0;
}
.q-title-input {
  flex: 1;
  border: none;
  font-size: var(--font-size-base);
  font-family: var(--font-family);
  color: var(--color-text-primary);
  padding: 4px 8px;
  outline: none;
  border-bottom: 2px solid transparent;
  transition: border-color var(--transition-fast);
}
.q-title-input:focus {
  border-bottom-color: var(--color-primary);
}
.q-title-input:disabled {
  background: transparent;
  color: var(--color-text-primary);
  cursor: default;
  opacity: 1;
}
.q-header-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  flex-shrink: 0;
}
.required-toggle {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  cursor: pointer;
}
.q-options {
  padding-left: 40px;
}
.option-row {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
}
.option-marker {
  font-size: 18px;
  color: var(--color-text-tertiary);
}
.option-input {
  flex: 1;
  max-width: 400px;
}
.add-option-btn {
  margin-left: 38px;
  margin-top: var(--spacing-xs);
}
.rating-preview {
  padding-left: 40px;
  font-size: 24px;
  color: var(--color-warning);
}
.slider-preview {
  padding: var(--spacing-md) 40px;
}
.scale-preview {
  padding-left: 40px;
}
.scale-row {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}
.scale-dot {
  width: 24px;
  height: 24px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}
.q-preview-placeholder {
  padding-left: 40px;
  padding-bottom: var(--spacing-sm);
}
</style>
