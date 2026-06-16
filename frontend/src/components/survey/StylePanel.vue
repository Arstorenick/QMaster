<template>
  <div class="style-panel">
    <div class="style-grid">
      <div class="style-group card">
        <h4>主题设置</h4>
        <div class="form-group">
          <label>主题色</label>
          <div class="color-picker-row">
            <input type="color" v-model="localStyle.theme_color" @change="save" />
            <span class="text-sm text-secondary">{{ localStyle.theme_color }}</span>
          </div>
        </div>
        <div class="form-group">
          <label>背景色</label>
          <input type="color" v-model="localStyle.bg_color" @change="save" />
        </div>
      </div>

      <div class="style-group card">
        <h4>显示设置</h4>
        <label class="toggle-row" v-for="opt in toggles" :key="opt.key">
          <span>{{ opt.label }}</span>
          <input type="checkbox" v-model="localStyle[opt.key]" @change="save" />
        </label>
      </div>

      <div class="style-group card">
        <h4>图片设置</h4>
        <div class="form-group">
          <label>Logo URL</label>
          <input v-model="localStyle.logo_image" class="input" placeholder="https://..." @blur="save" />
        </div>
        <div class="form-group">
          <label>页眉图 URL</label>
          <input v-model="localStyle.header_image" class="input" placeholder="https://..." @blur="save" />
        </div>
        <div class="form-group">
          <label>背景图 URL</label>
          <input v-model="localStyle.bg_image" class="input" placeholder="https://..." @blur="save" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, watch } from 'vue'
import { surveysAPI } from '../../api'

const props = defineProps({ survey: Object })
const emit = defineEmits(['updated'])

const defaults = {
  theme_color: '#4F46E5',
  bg_color: '#F9FAFB',
  logo_image: '',
  header_image: '',
  bg_image: '',
  logo_bg_color: '#FFFFFF',
  progress_color: '#4F46E5',
  show_question_number: true,
  show_progress: true,
  show_title: true,
  show_description: true,
  show_question_type: false,
  show_question_score: false,
  mobile_adaptive: true,
}

const toggles = [
  { key: 'show_question_number', label: '显示题号' },
  { key: 'show_progress', label: '显示进度条' },
  { key: 'show_title', label: '显示标题' },
  { key: 'show_description', label: '显示说明' },
  { key: 'show_question_type', label: '显示题型标签' },
  { key: 'show_question_score', label: '显示分数' },
  { key: 'mobile_adaptive', label: '移动端自适应' },
]

const localStyle = reactive({ ...defaults, ...(props.survey?.style || {}) })

watch(() => props.survey?.style, (val) => {
  Object.assign(localStyle, { ...defaults, ...(val || {}) })
})

async function save() {
  await surveysAPI.style(props.survey.id, { ...localStyle })
  emit('updated')
}
</script>

<style scoped>
.style-panel {
  padding: var(--spacing-lg);
  max-width: 1400px;
  margin: 0 auto;
}
.style-grid {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}
.style-group {
  padding: var(--spacing-lg);
}
.style-group h4 {
  margin-bottom: var(--spacing-md);
  font-size: var(--font-size-sm);
}
.form-group {
  margin-bottom: var(--spacing-md);
}
.form-group label {
  display: block;
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  margin-bottom: 4px;
}
.color-picker-row {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}
.toggle-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0;
  font-size: var(--font-size-sm);
  cursor: pointer;
}
.toggle-row input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: var(--color-primary);
}
</style>
