<template>
  <div class="stats-panel">
    <div class="stats-header">
      <div class="stats-summary">
        <div class="stat-card stat-clickable" style="border-color: var(--color-primary); --hover-bg: var(--color-primary-light)" @click="showDetail('expected')">
          <span class="stat-num">{{ stats?.expected_submissions || 0 }}</span>
          <span class="stat-label" style="color: var(--color-primary)">应提交人数</span>
        </div>
        <div class="stat-card stat-clickable" style="border-color: var(--color-success); --hover-bg: var(--color-success-light)" @click="showDetail('submitted')">
          <span class="stat-num" style="color: var(--color-success)">{{ stats?.total_submissions || 0 }}</span>
          <span class="stat-label" style="color: var(--color-success)">已提交人数</span>
        </div>
        <div class="stat-card stat-clickable" style="border-color: var(--color-danger); --hover-bg: var(--color-danger-light)" @click="showDetail('remaining')">
          <span class="stat-num" style="color: var(--color-danger)">{{ stats?.remaining_submissions || 0 }}</span>
          <span class="stat-label" style="color: var(--color-danger)">未提交人数</span>
        </div>
      </div>
    </div>
    <div class="stats-actions">
      <button class="btn btn-secondary btn-sm" @click="exportExcel">导出 Excel</button>
    </div>

    <div v-if="!stats?.questions?.length" class="stats-empty text-center">
      <p style="font-size:48px;margin-bottom:12px">📊</p>
      <p class="text-secondary">{{ stats?.total_submissions ? '暂无分析数据' : '还没有人提交问卷' }}</p>
    </div>

    <!-- Detail Panel -->
    <div class="detail-panel" v-if="detailDialog">
      <div class="detail-inner">
        <div class="detail-header">
          <h3>{{ detailTitle }}</h3>
          <span class="detail-count">{{ detailList.length }} 人</span>
          <button class="btn btn-ghost btn-sm detail-close" @click="detailDialog = null">✕</button>
        </div>
        <div class="detail-body" v-if="detailList.length">
          <div class="detail-item" v-for="u in detailList" :key="u.id">
            <span class="detail-avatar">{{ (u.display_name || u.username).charAt(0) }}</span>
            <div class="detail-info">
              <span class="detail-name">{{ u.display_name || u.username }}</span>
              <span class="detail-meta">{{ u.employee_id || '无工号' }} · {{ u.department_name || '无部门' }}</span>
            </div>
          </div>
        </div>
        <p v-else class="text-secondary text-center" style="padding:var(--spacing-xl)">暂无数据</p>
      </div>
    </div>

    <div v-for="q in stats?.questions" :key="q.question_id" class="stat-question card">
      <div class="stat-q-header">
        <h4>{{ q.title }}</h4>
        <span class="tag tag-primary">{{ q.total_answers }} 条回答</span>
      </div>

      <!-- Choice / Dropdown / Image choice -->
      <template v-if="q.options">
        <table class="table">
          <thead>
            <tr>
              <th>选项</th>
              <th style="width:100px">数量</th>
              <th style="width:100px">占比</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="opt in q.options" :key="opt.option_id">
              <td>{{ opt.title }}</td>
              <td>{{ opt.count }}</td>
              <td>
                <div class="pct-bar">
                  <div class="pct-fill" :style="{ width: opt.percentage + '%' }"></div>
                  <span>{{ opt.percentage }}%</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Chart toggle -->
        <div class="chart-actions">
          <button
            v-for="ct in chartTypes" :key="ct.value"
            class="btn btn-ghost btn-sm"
            :class="{ active: activeChart[q.question_id] === ct.value }"
            @click="toggleChart(q.question_id, ct.value)"
          >{{ ct.label }}</button>
        </div>
        <div v-if="activeChart[q.question_id]" :ref="el => setChartRef(q.question_id, el)" class="chart-container"></div>
      </template>

      <!-- Rating / Scale / Slider -->
      <template v-else-if="q.avg !== undefined">
        <div class="avg-display">
          <span class="avg-num">{{ q.avg }}</span>
          <span class="text-secondary text-sm">平均分</span>
        </div>
      </template>

      <!-- Text questions -->
      <template v-else>
        <button class="btn btn-ghost btn-sm" @click="loadTextAnswers(q.question_id)">
          查看文本答案 ({{ q.text_count }})
        </button>
        <div v-if="textDialog === q.question_id" class="text-answers mt-md">
          <div v-for="(a, i) in textAnswers" :key="i" class="text-answer-item">
            <span class="text-answer-num">{{ (textPage - 1) * 20 + i + 1 }}.</span>
            <span>{{ a.answer_text }}</span>
            <span class="text-sm text-secondary">{{ a.submit_time?.slice(0, 10) }}</span>
          </div>
        </div>
      </template>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import { responsesAPI } from '../../api'
import * as echarts from 'echarts'

const props = defineProps({ survey: Object })
const stats = ref(null)
const chartInstances = {}
const chartRefs = {}
const activeChart = ref({})

const chartTypes = [
  { value: 'bar', label: '柱状图' },
  { value: 'pie', label: '饼图' },
  { value: 'ring', label: '圆环图' },
  { value: 'horizontal', label: '条形图' },
]

const detailDialog = ref(null)
const detailTitle = ref('')
const detailList = ref([])

const textDialog = ref(null)
const textAnswers = ref([])
const textPage = ref(1)

onMounted(loadStats)
watch(() => props.survey?.id, () => { detailDialog.value = null; loadStats() })

async function showDetail(type) {
  detailDialog.value = type
  if (type === 'expected') detailTitle.value = '应提交人员名单'
  else if (type === 'submitted') detailTitle.value = '已提交人员名单'
  else detailTitle.value = '尚未提交人员名单'

  try {
    const { data } = await responsesAPI.statisticsDetail(props.survey.id, type)
    detailList.value = data.users || []
  } catch {
    detailList.value = []
  }
}

async function loadStats() {
  const { data } = await responsesAPI.statistics(props.survey.id)
  stats.value = data
}

function setChartRef(qId, el) {
  if (el) chartRefs[qId] = el
}

async function toggleChart(qId, type) {
  if (activeChart.value[qId] === type) {
    activeChart.value[qId] = null
    return
  }
  activeChart.value[qId] = type
  await nextTick()
  renderChart(qId, type)
}

function renderChart(qId, type) {
  const el = chartRefs[qId]
  if (!el) return

  if (chartInstances[qId]) chartInstances[qId].dispose()

  const chart = echarts.init(el)
  chartInstances[qId] = chart

  const q = stats.value.questions.find(q => q.question_id === qId)
  if (!q?.options) return

  const names = q.options.map(o => o.title)
  const values = q.options.map(o => o.count)

  let option
  if (type === 'pie' || type === 'ring') {
    option = {
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie',
        radius: type === 'ring' ? ['40%', '70%'] : '70%',
        data: names.map((n, i) => ({ name: n, value: values[i] })),
        label: { show: true, formatter: '{b}: {d}%' },
      }],
    }
  } else {
    option = {
      tooltip: { trigger: 'axis' },
      xAxis: type === 'horizontal' ? { type: 'value' } : { type: 'category', data: names, axisLabel: { rotate: 20 } },
      yAxis: type === 'horizontal' ? { type: 'category', data: names } : { type: 'value' },
      series: [{
        type: 'bar',
        data: values,
        itemStyle: { color: '#4F46E5', borderRadius: [4, 4, 0, 0] },
      }],
      grid: { top: 20, right: 20, bottom: 40, left: type === 'horizontal' ? 100 : 40 },
    }
  }

  chart.setOption(option)
  window.addEventListener('resize', () => chart.resize())
}

async function loadTextAnswers(qId) {
  if (textDialog.value === qId) {
    textDialog.value = null
    return
  }
  textDialog.value = qId
  const { data } = await responsesAPI.textAnswers(props.survey.id, qId, textPage.value)
  textAnswers.value = data.answers
}

async function exportExcel() {
  const response = await responsesAPI.exportExcel(props.survey.id)
  const url = URL.createObjectURL(new Blob([response.data]))
  const a = document.createElement('a')
  a.href = url
  a.download = `${props.survey.title}_统计.xlsx`
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.stats-panel {
  padding: var(--spacing-lg);
  max-width: 1400px;
  margin: 0 auto;
}
.stats-summary { display: flex; gap: var(--spacing-md); flex: 1; }
.stats-header {
  margin-bottom: var(--spacing-md);
}
.stats-actions {
  display: flex;
  justify-content: flex-end;
  margin-bottom: var(--spacing-lg);
}
.stat-card {
  flex: 1; text-align: center;
  padding: var(--spacing-lg) var(--spacing-xl);
  background: var(--color-bg-white);
  border-radius: var(--radius-lg);
  border: 2px solid var(--color-border-light);
}
.stat-num {
  font-size: var(--font-size-3xl);
  font-weight: 700;
  line-height: 1.1;
  color: var(--color-primary);
  display: block;
}
.stat-label {
  font-size: var(--font-size-sm);
  font-weight: 500;
  margin-top: 4px;
}
.stat-clickable { cursor: pointer; transition: all var(--transition-fast); }
.stat-clickable:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); background: var(--hover-bg, var(--color-bg-white)); }

.detail-panel {
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  background: var(--color-bg-white);
  overflow: hidden;
  margin-top: var(--spacing-md);
  animation: fadeInUp 0.25s ease;
}
.detail-inner { max-height: 400px; display: flex; flex-direction: column; }
.detail-header {
  display: flex; align-items: center; gap: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--color-border-light);
  background: var(--color-bg);
}
.detail-header h3 { font-size: 15px; flex: 1; }
.detail-count { font-size: 12px; color: var(--color-text-tertiary); background: var(--color-bg-white); padding: 2px 10px; border-radius: 10px; }
.detail-close { font-size: 16px; padding: 4px 8px; }
.detail-body { flex: 1; overflow-y: auto; padding: var(--spacing-sm); }
.detail-item {
  display: flex; align-items: center; gap: var(--spacing-sm);
  padding: 8px 12px; border-radius: var(--radius-md);
  transition: background var(--transition-fast);
}
.detail-item:hover { background: var(--color-bg-hover); }
.detail-avatar {
  width: 36px; height: 36px; border-radius: 50%;
  background: var(--color-primary-light); color: var(--color-primary);
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 700; flex-shrink: 0;
}
.detail-info { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.detail-name { font-size: 14px; font-weight: 500; }
.detail-meta { font-size: 12px; color: var(--color-text-tertiary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
.stats-empty {
  padding: var(--spacing-2xl);
}
.stat-question {
  padding: var(--spacing-lg);
  margin-bottom: var(--spacing-md);
}
.stat-q-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-md);
}
.pct-bar {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  position: relative;
}
.pct-fill {
  height: 6px;
  background: var(--color-primary);
  border-radius: 3px;
  min-width: 2px;
}
.chart-actions {
  display: flex;
  gap: var(--spacing-xs);
  margin-top: var(--spacing-md);
}
.chart-actions .active {
  background: var(--color-primary-light);
  color: var(--color-primary);
}
.chart-container {
  width: 100%;
  height: 300px;
  margin-top: var(--spacing-md);
}
.avg-display {
  text-align: center;
  padding: var(--spacing-lg);
}
.avg-num {
  font-size: var(--font-size-3xl);
  font-weight: 700;
  color: var(--color-primary);
  display: block;
}
.text-answers {
  max-height: 400px;
  overflow-y: auto;
}
.text-answer-item {
  padding: var(--spacing-sm) 0;
  border-bottom: 1px solid var(--color-border-light);
  display: flex;
  gap: var(--spacing-sm);
  font-size: var(--font-size-sm);
}
.text-answer-num {
  color: var(--color-text-tertiary);
  flex-shrink: 0;
}
</style>
