<template>
  <div class="display-q">
    <div class="dq-title">
      <span v-if="showNumber" class="dq-num">{{ number }}.</span>
      <span>{{ question.title }}</span>
      <span v-if="question.is_required" class="dq-required">*</span>
    </div>

    <!-- Radio -->
    <div v-if="question.type === 'radio'" class="dq-options">
      <label v-for="opt in question.options" :key="opt.id" class="dq-opt">
        <input type="radio" :name="nameKey" :value="opt.id" v-model="answers[question.id]" :disabled="readonly" />
        <span>{{ opt.title }}</span>
      </label>
    </div>

    <!-- Checkbox -->
    <div v-if="question.type === 'checkbox'" class="dq-options">
      <label v-for="opt in question.options" :key="opt.id" class="dq-opt">
        <input type="checkbox" :value="opt.id" v-model="answers[question.id]" :disabled="readonly" />
        <span>{{ opt.title }}</span>
      </label>
    </div>

    <!-- Text / Textarea -->
    <textarea v-if="question.type === 'text' || question.type === 'textarea'" class="input" :rows="question.config?.rows || 3" v-model="answers[question.id]" :placeholder="question.config?.placeholder || '请输入'" :disabled="readonly"></textarea>

    <!-- Rating -->
    <div v-if="question.type === 'rating'" class="dq-rating">
      <span v-for="i in (question.config?.max_score || 5)" :key="i" class="rating-star" :class="{ active: answers[question.id] >= i }" @click="!readonly && (answers[question.id] = i)">★</span>
    </div>

    <!-- Dropdown -->
    <select v-if="question.type === 'dropdown'" class="input" v-model="answers[question.id]" :disabled="readonly" style="max-width:300px">
      <option value="">请选择</option>
      <option v-for="opt in question.options" :key="opt.id" :value="opt.id">{{ opt.title }}</option>
    </select>

    <!-- Scale -->
    <div v-if="question.type === 'scale'" class="dq-scale">
      <span class="text-sm">{{ question.config?.left_label }}</span>
      <label v-for="i in (question.config?.scale || 5)" :key="i" class="scale-radio">
        <input type="radio" :value="i" v-model="answers[question.id]" :disabled="readonly" />
        <span>{{ i }}</span>
      </label>
      <span class="text-sm">{{ question.config?.right_label }}</span>
    </div>

    <!-- Date / Time -->
    <div v-if="question.type === 'date' || question.type === 'time'" class="dq-datetime">
      <div v-if="(question.config?.mode || 'datetime') !== 'time'" class="dt-field">
        <span class="dt-field-icon">📅</span>
        <input type="date" class="dt-input" v-model="answers[question.id + '_date']" :disabled="readonly" />
      </div>
      <div v-if="(question.config?.mode || 'datetime') !== 'date'" class="dt-field">
        <span class="dt-field-icon">🕐</span>
        <input type="time" class="dt-input" v-model="answers[question.id + '_time']" :disabled="readonly" />
      </div>
    </div>

    <!-- Slider -->
    <div v-if="question.type === 'slider'" class="dq-slider">
      <input type="range" :min="question.config?.min || 0" :max="question.config?.max || 100" v-model="answers[question.id]" :disabled="readonly" style="flex:1" />
      <span>{{ answers[question.id] || 0 }}{{ question.config?.unit || '' }}</span>
    </div>

    <!-- Ranking -->
    <div v-if="question.type === 'ranking'" class="dq-ranking">
      <div class="dq-ranking-hint">上下拖拽选项进行排序（越靠上优先级越高）</div>
      <draggable v-if="!readonly" v-model="rankingOrders[question.id]" item-key="id" handle=".ranking-drag-handle" ghost-class="ranking-ghost" :animation="200">
        <template #item="{ element: opt, index }">
          <div class="dq-ranking-item">
            <span class="ranking-drag-handle">⠿</span>
            <span class="ranking-pos">{{ index + 1 }}</span>
            <span class="dq-ranking-label">{{ opt.title }}</span>
          </div>
        </template>
      </draggable>
      <div v-else v-for="(opt, index) in (rankingOrders[question.id] || question.options)" :key="opt.id" class="dq-ranking-item" style="opacity:0.7">
        <span class="ranking-pos">{{ index + 1 }}</span>
        <span class="dq-ranking-label">{{ opt.title }}</span>
      </div>
    </div>

    <!-- File Upload -->
    <div v-if="question.type === 'file_upload'" style="margin-top:4px">
      <input type="file" @change="e => $emit('fileChange', question, e)" :disabled="readonly" />
      <span v-if="fileName" class="text-sm text-secondary" style="margin-left:8px">{{ fileName }}</span>
    </div>

    <!-- Image Radio -->
    <div v-if="question.type === 'image_radio'" class="dq-options">
      <label v-for="opt in question.options" :key="opt.id" class="dq-opt">
        <input type="radio" :name="nameKey" :value="opt.id" v-model="answers[question.id]" :disabled="readonly" />
        <span>{{ opt.title }}</span>
      </label>
    </div>

    <!-- Image Checkbox -->
    <div v-if="question.type === 'image_checkbox'" class="dq-options">
      <label v-for="opt in question.options" :key="opt.id" class="dq-opt">
        <input type="checkbox" :value="opt.id" v-model="answers[question.id]" :disabled="readonly" />
        <span>{{ opt.title }}</span>
      </label>
    </div>
  </div>
</template>

<script setup>
import draggable from 'vuedraggable'

const props = defineProps({
  question: { type: Object, required: true },
  answers: { type: Object, required: true },
  rankingOrders: { type: Object, default: () => ({}) },
  number: { type: Number, default: 1 },
  showNumber: { type: Boolean, default: true },
  readonly: { type: Boolean, default: false },
  fileName: { type: String, default: '' },
})

defineEmits(['fileChange'])

const nameKey = 'q-' + props.question.id
</script>

<style scoped>
.display-q { padding: var(--spacing-lg) 0; border-bottom: 1px solid var(--color-border-light); }
.dq-title { font-weight: 500; margin-bottom: var(--spacing-sm); }
.dq-num { color: var(--color-primary); font-weight: 600; }
.dq-required { color: var(--color-danger); font-weight: 600; }
.dq-options { display: flex; flex-direction: column; gap: var(--spacing-sm); }
.dq-opt {
  display: flex; align-items: center; gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  cursor: pointer; transition: all var(--transition-fast);
}
.dq-opt:hover { border-color: var(--color-primary); background: var(--color-primary-light); }
.dq-rating { display: flex; gap: 4px; }
.rating-star { font-size: 32px; color: var(--color-border); cursor: pointer; transition: color 0.15s; }
.rating-star.active, .rating-star:hover { color: var(--color-warning); }
.dq-scale { display: flex; align-items: center; gap: var(--spacing-sm); }
.scale-radio { display: flex; flex-direction: column; align-items: center; gap: 2px; cursor: pointer; }
.scale-radio span { font-size: 11px; }
.dq-datetime { display: flex; gap: var(--spacing-sm); }
.dt-field {
  flex: 0 1 220px; min-width: 0;
  display: flex; align-items: center;
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  background: var(--color-bg-white);
  overflow: hidden; transition: all 0.2s ease;
}
.dt-field:focus-within { border-color: var(--color-primary); box-shadow: 0 0 0 3px var(--color-primary-100); }
.dt-field-icon { font-size: 18px; padding: 0 12px; flex-shrink: 0; opacity: 0.7; }
.dt-field:focus-within .dt-field-icon { opacity: 1; }
.dt-input { flex: 1; min-width: 0; padding: 10px 10px 10px 0; border: none; outline: none; font-size: 15px; font-family: var(--font-family); color: var(--color-text-primary); background: transparent; }
.dt-input::-webkit-calendar-picker-indicator { cursor: pointer; padding: 4px 8px; opacity: 0.5; transition: opacity 0.15s; }
.dt-input::-webkit-calendar-picker-indicator:hover { opacity: 1; }
.dq-slider { display: flex; align-items: center; gap: var(--spacing-md); }
.dq-ranking { display: flex; flex-direction: column; gap: var(--spacing-xs); }
.dq-ranking-hint { font-size: 12px; color: var(--color-text-tertiary); margin-bottom: 8px; }
.dq-ranking-item {
  display: flex; align-items: center; gap: var(--spacing-sm);
  padding: 10px 14px; border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md); background: var(--color-bg-white);
  transition: all 0.15s ease; cursor: default;
}
.dq-ranking-item:hover { border-color: var(--color-primary-100); box-shadow: var(--shadow-sm); }
.ranking-drag-handle { font-size: 18px; color: var(--color-text-tertiary); cursor: grab; flex-shrink: 0; line-height: 1; padding: 2px; }
.ranking-drag-handle:active { cursor: grabbing; }
.ranking-pos {
  width: 26px; height: 26px; display: flex; align-items: center; justify-content: center;
  background: var(--color-primary); color: #fff; border-radius: 50%;
  font-size: 12px; font-weight: 700; flex-shrink: 0;
}
.ranking-ghost { opacity: 0.4; background: var(--color-primary-light); border: 2px dashed var(--color-primary); }
.dq-ranking-label { font-size: 14px; font-weight: 500; }
</style>
