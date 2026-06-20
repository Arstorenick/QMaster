<template>
  <div class="editor-layout">
    <!-- Mode Selector -->
    <div class="mode-bar" v-if="!readonly">
      <div class="mode-tabs">
        <button :class="['mode-tab', { active: !scoringEnabled && !skipEnabled }]" @click="$emit('toggleScoring', false); $emit('toggleSkip', false)">
          <img :src="normalModeImg" alt="normal" class="mode-icon-img" />
          <span>正常模式</span>
        </button>
        <button :class="['mode-tab', { active: scoringEnabled }]" @click="$emit('toggleScoring', true); $emit('toggleSkip', false)">
          <img :src="scoreModeImg" alt="score" class="mode-icon-img" />
          <span>分值模式</span>
        </button>
        <button :class="['mode-tab', { active: skipEnabled }]" @click="$emit('toggleScoring', false); $emit('toggleSkip', true)">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 5l7 7-7 7M5 5l7 7-7 7"/></svg>
          <span>跳转模式</span>
        </button>
      </div>
      <span class="mode-hint" v-if="scoringEnabled">每题可设置分数，提交时自动计算总分</span>
      <span class="mode-hint" v-if="skipEnabled" style="background:linear-gradient(135deg,#EFF6FF,#DBEAFE);border-color:#93C5FD;color:#1D4ED8">为选项设置跳转规则，答题时按选择跳题</span>
    </div>

    <!-- Question Type Toolbar -->
    <div class="type-toolbar" v-if="!readonly">
      <div class="type-group" v-for="group in visibleTypeGroups" :key="group.label">
        <span class="type-group-label">{{ group.label }}</span>
        <div class="type-buttons">
          <button
            v-for="t in group.types" :key="t.value"
            class="type-btn"
            @click="addQuestion(t.value)"
          ><img v-if="t.img" :src="t.img" class="type-btn-icon-img" /><span v-else class="type-btn-icon">{{ t.icon }}</span><span class="type-btn-label">{{ t.label }}</span></button>
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
              <div v-if="scoringEnabled && !readonly" class="score-badge" title="题目分值">
                <input v-model.number="q.score" class="score-input" type="number" min="0" placeholder="0" @blur="updateQuestion(q)" />
                <span class="score-unit">分</span>
              </div>
              <label class="required-toggle" v-if="!readonly">
                <input type="checkbox" v-model="q.is_required" @change="updateQuestion(q)" />
                <span>必填</span>
              </label>
              <button v-if="!readonly" class="btn btn-ghost btn-sm" @click="copyQuestion(q)">复制</button>
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
              <div v-if="scoringEnabled && !readonly" class="score-badge score-badge-sm" title="选项分值">
                <input v-model.number="opt.score" class="score-input score-input-sm" type="number" min="0" placeholder="0" @blur="updateOption(q, opt)" />
                <span class="score-unit">分</span>
              </div>
              <button v-if="!readonly" class="btn btn-ghost btn-sm" @click="deleteOption(q, opt.id)" style="color:var(--color-danger)">×</button>
              <div v-if="skipEnabled && !readonly" class="skip-rule">
                <span class="skip-rule-label">→</span>
                <select class="skip-rule-select" v-model="ensureSkipRules(q)[opt.id]" @change="updateQuestion(q)">
                  <option :value="null">下一题</option>
                  <option v-for="sq in getSkipTargets(q)" :key="sq.id" :value="sq.id">{{ sq.title || '未命名' }}</option>
                  <option :value="-1">结束问卷</option>
                </select>
              </div>
            </div>
            <button v-if="!readonly" class="btn btn-ghost btn-sm add-option-btn" @click="addOption(q)">+ 添加选项</button>

            <!-- Ranking preview -->
            <div v-if="q.type === 'ranking' && q.options?.length" class="ranking-editor-preview">
              <div class="ranking-preview-item" v-for="(opt, ri) in q.options.slice(0, 5)" :key="opt.id">
                <span class="ranking-preview-num">{{ ri + 1 }}</span>
                <span class="ranking-preview-text">{{ opt.title || `选项 ${ri + 1}` }}</span>
                <span class="ranking-preview-arrows">↕</span>
              </div>
            </div>
          </div>

          <!-- Text preview -->
          <div v-else-if="q.type === 'text'">
            <textarea
              class="input"
              :rows="q.config?.rows || 3"
              disabled
              placeholder="文本回答区域"
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

          <!-- Date preview -->
          <div v-else-if="q.type === 'date'" class="date-preview">
            <div class="date-mode-bar">
              <button :class="['date-mode-btn', { active: (q.config?.mode || 'datetime') === 'datetime' }]" @click="q.config.mode = 'datetime'; updateQuestion(q)">日期+时间</button>
              <button :class="['date-mode-btn', { active: q.config?.mode === 'date' }]" @click="q.config.mode = 'date'; updateQuestion(q)">仅日期</button>
              <button :class="['date-mode-btn', { active: q.config?.mode === 'time' }]" @click="q.config.mode = 'time'; updateQuestion(q)">仅时间</button>
            </div>
            <div class="date-preview-row">
              <input v-if="(q.config?.mode || 'datetime') !== 'time'" type="date" class="input" disabled style="flex:1" />
              <input v-if="(q.config?.mode || 'datetime') !== 'date'" type="time" class="input" disabled style="flex:1" />
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
      <img :src="addImg" alt="add" style="width:150px;height:150px;object-fit:contain;margin:0 auto 12px;display:block" />
      <p class="text-secondary">点击上方题型按钮添加题目</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import draggable from 'vuedraggable'
import { questionsAPI, optionsAPI } from '../../api'
import addImg from '../../assets/add.png'
import normalModeImg from '../../assets/model_normal.png'
import scoreModeImg from '../../assets/model_score.png'
import singleImg from '../../assets/question_single.png'
import multipleImg from '../../assets/question_multiple.png'
import fillImg from '../../assets/question_fill.png'
import ratingImg from '../../assets/question_rating.png'
import dropdownImg from '../../assets/question_dropdown.png'
import sortImg from '../../assets/question_sort.png'
import scaleImg from '../../assets/question_scale.png'

const props = defineProps({
  survey: Object,
  questions: Array,
  readonly: { type: Boolean, default: false },
  scoringEnabled: { type: Boolean, default: false },
  skipEnabled: { type: Boolean, default: false },
})
const emit = defineEmits(['refresh', 'toggleScoring', 'toggleSkip'])

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
      { value: 'radio', label: '单选', img: singleImg },
      { value: 'checkbox', label: '多选', img: multipleImg },
      { value: 'text', label: '主观', img: fillImg },
      { value: 'dropdown', label: '下拉', img: dropdownImg },
    ],
  },
  {
    label: '高级',
    types: [
      { value: 'rating', label: '评分', img: ratingImg },
      { value: 'ranking', label: '排序', img: sortImg },
      { value: 'scale', label: '量表', img: scaleImg },
      { value: 'slider', label: '滑块', icon: '🎚️' },
    ],
  },
  {
    label: '其他',
    types: [
      { value: 'date', label: '时间', icon: '📅' },
      { value: 'file_upload', label: '上传', icon: '📎' },
      { value: 'image_radio', label: '图单', icon: '🖼️' },
      { value: 'image_checkbox', label: '图多', icon: '🖼️' },
    ],
  },
  {
    label: '结构',
    types: [
      { value: 'page_break', label: '分页', icon: '📄' },
      { value: 'section_break', label: '标题', icon: '📑' },
    ],
  },
]

const skipOnlyTypes = ['radio', 'dropdown', 'image_radio']
const visibleTypeGroups = computed(() => {
  if (!props.skipEnabled) return typeGroups
  return typeGroups.map(g => ({
    ...g,
    types: g.types.filter(t => skipOnlyTypes.includes(t.value))
  })).filter(g => g.types.length)
})

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
    text: { rows: 3 },
    date: { mode: 'datetime' },
  }
  return defaults[type] || {}
}

async function updateQuestion(q) {
  await questionsAPI.update(props.survey.id, q.id, {
    title: q.title,
    is_required: q.is_required,
    type: q.type,
    config: q.config,
    score: q.score || 0,
  })
}

async function copyQuestion(q) {
  const newOpts = q.options.map((opt, i) => ({
    title: opt.title, order: i, score: opt.score, image: opt.image,
  }))
  await questionsAPI.create(props.survey.id, {
    type: q.type,
    title: q.title + ' (副本)',
    is_required: q.is_required,
    config: { ...q.config },
    score: q.score,
    options: newOpts,
  })
  emit('refresh')
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

function ensureSkipRules(q) {
  if (!q.config) q.config = {}
  if (!q.config.skip_rules) q.config.skip_rules = {}
  return q.config.skip_rules
}

function getSkipTargets(currentQ) {
  const idx = props.questions.findIndex(q => q.id === currentQ.id)
  return props.questions.slice(idx + 1).filter(q => skipOnlyTypes.includes(q.type))
}

async function updateOption(q, opt) {
  await optionsAPI.update(props.survey.id, q.id, opt.id, { title: opt.title, score: opt.score || 0 })
}

async function deleteOption(q, optId) {
  await optionsAPI.delete(props.survey.id, q.id, optId)
  emit('refresh')
}
</script>

<style scoped>
.editor-layout { padding: var(--spacing-lg); max-width: 1400px; margin: 0 auto; }
.question-list {
  max-height: calc(100vh - 340px); overflow-y: auto;
  position: relative;
}
.question-list::before {
  content: ''; position: sticky; top: 0; display: block;
  height: 24px;
  background: linear-gradient(to bottom, var(--color-bg), transparent);
  z-index: 5; pointer-events: none;
}

/* ── Mode Bar ── */
.mode-bar {
  display: flex; align-items: center; flex-wrap: wrap; gap: var(--spacing-sm);
  padding: 8px 0; margin-bottom: var(--spacing-sm);
}
.mode-tabs {
  display: inline-flex; gap: 0; position: relative;
  background: var(--color-bg); border-radius: var(--radius-lg);
  padding: 4px; border: 1px solid var(--color-border-light);
}
.mode-tab {
  display: flex; align-items: center; gap: 8px; padding: 8px 24px;
  border: none; background: transparent; border-radius: var(--radius-md);
  cursor: pointer; font-size: 14px; font-family: var(--font-family);
  color: var(--color-text-secondary);
  position: relative; z-index: 1;
  transition: color 0.25s ease, font-weight 0.25s ease;
}
.mode-tab:hover { color: var(--color-text-primary); }
.mode-tab.active {
  color: var(--color-primary); font-weight: 600;
  transition: color 0.15s ease, font-weight 0.15s ease;
}
.mode-tab.active::before {
  content: ''; position: absolute; inset: 0;
  background: var(--color-bg-white); border-radius: var(--radius-md);
  box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 0 0 1px rgba(0,0,0,0.02);
  z-index: -1;
  animation: modeSlideIn 0.25s ease;
}
@keyframes modeSlideIn {
  from { opacity: 0; transform: scale(0.92); }
  to { opacity: 1; transform: scale(1); }
}
.mode-icon-img { width: 22px; height: 22px; object-fit: contain; flex-shrink: 0; }
.mode-hint {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 6px 14px;
  background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
  border: 1px solid #FCD34D; border-radius: var(--radius-md);
  font-size: 13px; font-weight: 500; color: #92400E;
  animation: hintFadeIn 0.35s ease;
}
@keyframes hintFadeIn {
  from { opacity: 0; transform: translateX(-8px); }
  to { opacity: 1; transform: translateX(0); }
}

/* ── Type Toolbar ── */
.type-toolbar {
  display: flex; flex-direction: column; gap: 6px;
  margin-bottom: var(--spacing-lg);
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--color-bg-white); border-radius: var(--radius-lg);
  border: 1px solid var(--color-border-light);
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.type-group { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.type-group-label {
  font-size: 11px; font-weight: 600; color: var(--color-text-tertiary);
  text-transform: uppercase; letter-spacing: 0.05em; flex-shrink: 0;
  min-width: 32px;
}
.type-buttons { display: flex; gap: 4px; flex-wrap: wrap; }
.type-btn {
  display: flex; align-items: center; justify-content: center; gap: 5px;
  padding: 5px 12px; width: 102px;
  border: 1px solid var(--color-border-light);
  background: var(--color-bg-white); border-radius: var(--radius-md);
  cursor: pointer; font-family: var(--font-family);
  transition: all 0.15s ease; white-space: nowrap;
}
.type-btn:hover { border-color: var(--color-primary); background: var(--color-primary-50); transform: translateY(-1px); box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
.type-btn:active { transform: translateY(0); }
.type-btn-icon { font-size: 16px; line-height: 1; }
.type-btn-icon-img { width: 16px; height: 16px; object-fit: contain; }
.type-btn-label { font-size: 12px; color: var(--color-text-secondary); font-weight: 500; }
.type-btn:hover .type-btn-label { color: var(--color-primary); }

/* ── Question Card ── */
.editor-empty { text-align: center; padding: var(--spacing-3xl); }
.drag-handle { cursor: grab; font-size: 18px; color: var(--color-text-tertiary); user-select: none; padding: 0 4px; transition: color 0.15s ease; }
.drag-handle:hover { color: var(--color-primary); }
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
  background: var(--color-primary-50);
  border: 2px dashed var(--color-primary-100);
  border-radius: var(--radius-lg);
}
.question-card.is-section-break {
  text-align: center;
  background: var(--color-bg);
  border: none;
  padding: var(--spacing-sm) var(--spacing-lg);
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
  display: flex; align-items: center; gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
  padding-bottom: var(--spacing-sm);
  border-bottom: 1px solid var(--color-border-light);
}
.q-number {
  width: 28px; height: 28px;
  background: var(--color-primary); color: #fff;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 700; flex-shrink: 0;
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
.score-badge {
  display: inline-flex; align-items: center;
  border: 1px solid #FCD34D;
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
  overflow: hidden;
  transition: all 0.15s ease;
}
.score-badge:focus-within {
  border-color: #F59E0B;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.15);
}
.score-badge-sm { border-radius: var(--radius-sm); }
.score-input {
  width: 44px; padding: 4px 2px 4px 8px;
  border: none; border-radius: 0;
  font-size: 14px; font-weight: 700; text-align: center;
  font-family: var(--font-family); outline: none;
  color: #B45309; background: transparent;
}
.score-input:focus { outline: none; }
.score-input-sm { width: 44px; font-size: 13px; padding: 2px 2px 2px 6px; }
.score-unit {
  font-size: 11px; font-weight: 600; color: #B45309;
  padding-right: 8px; flex-shrink: 0;
}
.score-badge-sm .score-unit { font-size: 10px; padding-right: 6px; }
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
.skip-rule {
  display: flex; align-items: center; gap: 4px;
  margin-left: var(--spacing-sm);
}
.skip-rule-label { font-size: 13px; color: var(--color-primary); font-weight: 600; }
.skip-rule-select {
  padding: 3px 20px 3px 6px; border: 1px solid #93C5FD;
  border-radius: var(--radius-sm); font-size: 12px; font-family: var(--font-family);
  color: #1D4ED8; background: #EFF6FF; cursor: pointer; outline: none;
  appearance: none; -webkit-appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg width='6' height='4' viewBox='0 0 6 4' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1l2 2 2-2' stroke='%233B82F6' fill='none'/%3E%3C/svg%3E");
  background-repeat: no-repeat; background-position: right 4px center;
}
.ranking-editor-preview {
  margin-top: var(--spacing-md);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  overflow: hidden;
}
.ranking-preview-item {
  display: flex; align-items: center; gap: var(--spacing-sm);
  padding: 10px 14px;
  border-bottom: 1px solid var(--color-border-light);
  background: var(--color-bg);
}
.ranking-preview-item:last-child { border-bottom: none; }
.ranking-preview-num {
  width: 26px; height: 26px;
  display: flex; align-items: center; justify-content: center;
  background: var(--color-primary); color: #fff;
  border-radius: 50%;
  font-size: 12px; font-weight: 700;
  flex-shrink: 0;
}
.ranking-preview-text {
  flex: 1; font-size: 13px; color: var(--color-text-primary);
}
.ranking-preview-arrows {
  color: var(--color-text-tertiary); font-size: 16px;
}
.date-preview { margin-top: var(--spacing-md); }
.date-mode-bar { display: flex; gap: 4px; margin-bottom: var(--spacing-sm); }
.date-mode-btn {
  padding: 4px 12px;
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-sm);
  background: var(--color-bg-white);
  font-size: 12px; font-family: var(--font-family);
  cursor: pointer; transition: all 0.15s ease;
  color: var(--color-text-secondary);
}
.date-mode-btn:hover { border-color: var(--color-primary-100); color: var(--color-primary); }
.date-mode-btn.active {
  background: var(--color-primary-light);
  border-color: var(--color-primary);
  color: var(--color-primary);
  font-weight: 500;
}
.date-preview-row { display: flex; gap: var(--spacing-sm); }
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
