<template>
  <div class="style-panel">
    <div class="style-grid">
      <!-- 题目标记 -->
      <div class="style-group card">
        <h4>题目标记</h4>
        <p class="style-desc">控制题目旁边显示哪些辅助信息</p>
        <label class="toggle-row">
          <div>
            <span>题号</span>
            <small>显示 "1. 2. 3." 编号</small>
          </div>
          <input type="checkbox" v-model="localStyle.show_question_number" @change="save" />
        </label>
        <label class="toggle-row">
          <div>
            <span>题型标签</span>
            <small>显示 "单选题" "多选题" 等</small>
          </div>
          <input type="checkbox" v-model="localStyle.show_question_type" @change="save" />
        </label>
        <label class="toggle-row">
          <div>
            <span>题目分数</span>
            <small>评分模式下显示每题分值</small>
          </div>
          <input type="checkbox" v-model="localStyle.show_question_score" @change="save" />
        </label>
      </div>

      <!-- 问卷信息 -->
      <div class="style-group card">
        <h4>问卷信息</h4>
        <p class="style-desc">顶部展示的问卷基本信息</p>
        <label class="toggle-row">
          <div>
            <span>问卷标题</span>
            <small>答题页顶部的大标题</small>
          </div>
          <input type="checkbox" v-model="localStyle.show_title" @change="save" />
        </label>
        <label class="toggle-row">
          <div>
            <span>问卷说明</span>
            <small>标题下方的描述文字</small>
          </div>
          <input type="checkbox" v-model="localStyle.show_description" @change="save" />
        </label>
      </div>

      <!-- 答题辅助 -->
      <div class="style-group card">
        <h4>答题辅助</h4>
        <p class="style-desc">帮助答题人了解进度的功能</p>
        <label class="toggle-row">
          <div>
            <span>进度条</span>
            <small>多页问卷显示 "1/3" 进度</small>
          </div>
          <input type="checkbox" v-model="localStyle.show_progress" @change="save" />
        </label>
        <label class="toggle-row">
          <div>
            <span>移动端适配</span>
            <small>手机浏览器自动调整布局</small>
          </div>
          <input type="checkbox" v-model="localStyle.mobile_adaptive" @change="save" />
        </label>
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
  margin-bottom: 2px;
  font-size: 17px;
  font-weight: 600;
}
.style-desc {
  font-size: 13px;
  color: var(--color-text-tertiary);
  margin-bottom: var(--spacing-md);
}
.toggle-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid var(--color-border-light);
  cursor: pointer;
}
.toggle-row:last-child {
  border-bottom: none;
}
.toggle-row span {
  font-size: 16px;
  font-weight: 500;
}
.toggle-row small {
  display: block;
  font-size: 13px;
  color: var(--color-text-tertiary);
  margin-top: 2px;
}
.toggle-row input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: var(--color-primary);
  flex-shrink: 0;
}
</style>
