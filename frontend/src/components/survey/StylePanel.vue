<template>
  <div class="style-panel">
    <div class="style-grid">
      <!-- 题目标记 -->
      <div class="style-group card">
        <div class="style-group-header">
          <span class="style-group-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 7h16M4 12h10M4 17h6"/></svg></span>
          <div>
            <h4>题目标记</h4>
            <p class="style-desc">控制题目旁边显示哪些辅助信息</p>
          </div>
        </div>
        <div class="style-toggles">
          <label class="toggle-row" :class="{ on: localStyle.show_question_number }">
            <div class="toggle-info">
              <span class="toggle-label">题号</span>
              <span class="toggle-hint">显示 "1. 2. 3." 编号</span>
            </div>
            <div class="toggle-switch">
              <input type="checkbox" v-model="localStyle.show_question_number" @change="save" />
              <span class="toggle-track"></span>
            </div>
          </label>
          <label class="toggle-row" :class="{ on: localStyle.show_question_type }">
            <div class="toggle-info">
              <span class="toggle-label">题型标签</span>
              <span class="toggle-hint">显示 "单选题" "多选题" 等</span>
            </div>
            <div class="toggle-switch">
              <input type="checkbox" v-model="localStyle.show_question_type" @change="save" />
              <span class="toggle-track"></span>
            </div>
          </label>
          <label class="toggle-row" :class="{ on: localStyle.show_question_score }">
            <div class="toggle-info">
              <span class="toggle-label">题目分数</span>
              <span class="toggle-hint">评分模式下显示每题分值</span>
            </div>
            <div class="toggle-switch">
              <input type="checkbox" v-model="localStyle.show_question_score" @change="save" />
              <span class="toggle-track"></span>
            </div>
          </label>
        </div>
      </div>

      <!-- 问卷信息 -->
      <div class="style-group card">
        <div class="style-group-header">
          <span class="style-group-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg></span>
          <div>
            <h4>问卷信息</h4>
            <p class="style-desc">顶部展示的问卷基本信息</p>
          </div>
        </div>
        <div class="style-toggles">
          <label class="toggle-row" :class="{ on: localStyle.show_title }">
            <div class="toggle-info">
              <span class="toggle-label">问卷标题</span>
              <span class="toggle-hint">答题页顶部的大标题</span>
            </div>
            <div class="toggle-switch">
              <input type="checkbox" v-model="localStyle.show_title" @change="save" />
              <span class="toggle-track"></span>
            </div>
          </label>
          <label class="toggle-row" :class="{ on: localStyle.show_description }">
            <div class="toggle-info">
              <span class="toggle-label">问卷说明</span>
              <span class="toggle-hint">标题下方的描述文字</span>
            </div>
            <div class="toggle-switch">
              <input type="checkbox" v-model="localStyle.show_description" @change="save" />
              <span class="toggle-track"></span>
            </div>
          </label>
        </div>
      </div>

      <!-- 答题辅助 -->
      <div class="style-group card">
        <div class="style-group-header">
          <span class="style-group-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="10" rx="2"/><path d="M8 21h8M12 17v4"/></svg></span>
          <div>
            <h4>答题辅助</h4>
            <p class="style-desc">帮助答题人了解进度的功能</p>
          </div>
        </div>
        <div class="style-toggles">
          <label class="toggle-row" :class="{ on: localStyle.show_progress }">
            <div class="toggle-info">
              <span class="toggle-label">进度条</span>
              <span class="toggle-hint">多页问卷显示进度</span>
            </div>
            <div class="toggle-switch">
              <input type="checkbox" v-model="localStyle.show_progress" @change="save" />
              <span class="toggle-track"></span>
            </div>
          </label>
          <label class="toggle-row" :class="{ on: localStyle.mobile_adaptive }">
            <div class="toggle-info">
              <span class="toggle-label">移动端适配</span>
              <span class="toggle-hint">手机浏览器自动调整布局</span>
            </div>
            <div class="toggle-switch">
              <input type="checkbox" v-model="localStyle.mobile_adaptive" @change="save" />
              <span class="toggle-track"></span>
            </div>
          </label>
        </div>
      </div>
    </div>
    <p v-if="saveMsg" class="style-save-msg" :class="{ error: saveMsg === '保存失败' }">{{ saveMsg }}</p>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { surveysAPI } from '../../api'

const props = defineProps({ survey: Object })
const emit = defineEmits(['updated'])

const defaults = {
  show_question_number: true,
  show_progress: true,
  show_title: true,
  show_description: true,
  show_question_type: false,
  show_question_score: false,
  mobile_adaptive: true,
}

const localStyle = reactive({ ...defaults, ...(props.survey?.style || {}) })

watch(() => props.survey?.style, (val) => {
  Object.assign(localStyle, { ...defaults, ...(val || {}) })
})

const saveMsg = ref('')

async function save() {
  saveMsg.value = ''
  try {
    await surveysAPI.style(props.survey.id, { ...localStyle })
    saveMsg.value = '已保存'
    setTimeout(() => saveMsg.value = '', 1500)
    emit('updated')
  } catch (e) {
    saveMsg.value = '保存失败'
    console.error('Style save error:', e)
  }
}
</script>

<style scoped>
.style-panel { padding: var(--spacing-lg); max-width: 1400px; margin: 0 auto; }
.style-grid { display: flex; flex-direction: column; gap: var(--spacing-lg); }

/* ── Group Card ── */
.style-group { padding: var(--spacing-xl); border-radius: var(--radius-xl); }
.style-group-header { display: flex; align-items: flex-start; gap: var(--spacing-md); margin-bottom: var(--spacing-lg); }
.style-group-icon {
  width: 44px; height: 44px; border-radius: var(--radius-lg);
  background: var(--color-primary-50); color: var(--color-primary);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.style-group-header h4 { font-size: 17px; font-weight: 700; margin-bottom: 2px; }
.style-desc { font-size: 13px; color: var(--color-text-tertiary); }

/* ── Toggles ── */
.style-toggles { display: flex; flex-direction: column; }
.toggle-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 16px; margin: 0 -16px;
  border-radius: var(--radius-md);
  cursor: pointer; user-select: none;
  transition: background 0.15s ease;
}
.toggle-row:hover { background: var(--color-bg-hover); }
.toggle-row.on { background: var(--color-primary-50); }
.toggle-info { display: flex; flex-direction: column; gap: 2px; }
.toggle-label { font-size: 15px; font-weight: 600; color: var(--color-text-primary); }
.toggle-hint { font-size: 12px; color: var(--color-text-tertiary); }

/* ── Custom Switch ── */
.toggle-switch { position: relative; width: 44px; height: 26px; flex-shrink: 0; }
.toggle-switch input {
  position: absolute; inset: 0; width: 100%; height: 100%;
  opacity: 0; cursor: pointer; z-index: 1; margin: 0;
}
.toggle-track {
  position: absolute; inset: 0;
  background: var(--color-border);
  border-radius: 13px;
  transition: background 0.2s ease;
}
.toggle-track::after {
  content: ''; position: absolute;
  top: 3px; left: 3px;
  width: 20px; height: 20px;
  background: #fff; border-radius: 50%;
  box-shadow: 0 1px 4px rgba(0,0,0,0.15);
  transition: transform 0.2s ease;
}
.toggle-switch input:checked + .toggle-track {
  background: var(--color-primary);
}
.toggle-switch input:checked + .toggle-track::after {
  transform: translateX(18px);
}
.toggle-switch input:focus-visible + .toggle-track {
  box-shadow: 0 0 0 3px var(--color-primary-100);
}
.style-save-msg {
  text-align: center; margin-top: var(--spacing-md);
  font-size: 13px; font-weight: 500; color: var(--color-success);
}
.style-save-msg.error { color: var(--color-danger); }
</style>
