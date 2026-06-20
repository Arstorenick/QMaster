<template>
  <div class="stats-panel">
    <!-- Top Bar -->
    <div class="stats-topbar">
      <div class="stats-title-row">
        <h2>数据统计</h2>
        <span v-if="stats" class="stats-badge">{{ stats.total_submissions || 0 }} 份提交</span>
      </div>
      <button class="btn btn-secondary" @click="exportExcel">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" style="vertical-align:-3px;margin-right:4px"><path d="M2 10v3a1 1 0 001 1h10a1 1 0 001-1v-3M8 2v10m0 0L5 9m3 3l3-3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
        导出 Excel
      </button>
    </div>

    <!-- Stat Cards -->
    <div class="stats-summary">
      <div class="stat-card stat-card-blue" @click="showDetail('expected')">
        <div class="stat-card-inner">
          <div class="stat-card-left">
            <div class="stat-card-icon stat-icon-blue">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="8" r="4"/><path d="M4 22c0-4.4 3.6-8 8-8s8 3.6 8 8"/></svg>
            </div>
          </div>
          <div class="stat-card-right">
            <span class="stat-num stat-num-blue">{{ stats?.expected_submissions || 0 }}</span>
            <span class="stat-label">应提交人数</span>
          </div>
        </div>
        <div class="stat-card-footer">点击查看名单</div>
      </div>

      <div class="stat-card stat-card-green" @click="showDetail('submitted')">
        <div class="stat-card-inner">
          <div class="stat-card-left">
            <div class="stat-card-icon stat-icon-green">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            </div>
          </div>
          <div class="stat-card-right">
            <span class="stat-num stat-num-green">{{ stats?.total_submissions || 0 }}</span>
            <span class="stat-label">已提交人数</span>
          </div>
        </div>
        <div class="stat-card-footer">{{ completionRate }}% 完成率</div>
      </div>

      <div class="stat-card stat-card-red" @click="showDetail('remaining')">
        <div class="stat-card-inner">
          <div class="stat-card-left">
            <div class="stat-card-icon stat-icon-red">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            </div>
          </div>
          <div class="stat-card-right">
            <span class="stat-num stat-num-red">{{ stats?.remaining_submissions || 0 }}</span>
            <span class="stat-label">未提交人数</span>
          </div>
        </div>
        <div class="stat-card-footer">点击查看名单</div>
      </div>
    </div>

    <!-- Submission Progress Bar -->
    <div v-if="stats" class="stats-overall-bar">
      <div class="overall-bar-track">
        <div class="overall-bar-fill" :style="{ width: completionRate + '%' }"></div>
      </div>
      <span class="overall-bar-text">总完成率 {{ completionRate }}%</span>
    </div>

    <div v-if="!stats?.questions?.length" class="stats-empty text-center">
      <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" style="opacity:0.3;margin-bottom:12px"><path d="M18 20V10M12 20V4M6 20v-6"/></svg>
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
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { responsesAPI } from '../../api'
import * as echarts from 'echarts'

const props = defineProps({ survey: Object })
const stats = ref(null)

const completionRate = computed(() => {
  if (!stats.value || !stats.value.expected_submissions) return 0
  return Math.round((stats.value.total_submissions / stats.value.expected_submissions) * 100)
})
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
        itemStyle: { color: '#2563EB', borderRadius: [4, 4, 0, 0] },
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
.stats-panel { padding: var(--spacing-lg); max-width: 1400px; margin: 0 auto; }

/* ── Top Bar ── */
.stats-topbar {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: var(--spacing-xl);
}
.stats-title-row { display: flex; align-items: center; gap: var(--spacing-md); }
.stats-title-row h2 { font-size: 22px; font-weight: 700; }
.stats-badge {
  font-size: 13px; font-weight: 500;
  color: var(--color-primary); background: var(--color-primary-50);
  padding: 4px 12px; border-radius: 20px;
}

/* ── Stat Cards ── */
.stats-summary {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}
.stat-card {
  background: var(--color-bg-white);
  border-radius: var(--radius-xl);
  padding: var(--spacing-lg);
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid var(--color-border-light);
  overflow: hidden;
}
.stat-card:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0,0,0,0.08); }
.stat-card-inner { display: flex; align-items: center; gap: var(--spacing-md); margin-bottom: var(--spacing-md); }
.stat-card-left { flex-shrink: 0; }
.stat-card-right { flex: 1; min-width: 0; }
.stat-card-icon {
  width: 48px; height: 48px; border-radius: var(--radius-lg);
  display: flex; align-items: center; justify-content: center;
}
.stat-icon-blue { background: #EFF6FF; color: #2563EB; }
.stat-icon-green { background: #ECFDF5; color: #059669; }
.stat-icon-red { background: #FEF2F2; color: #DC2626; }
.stat-num { font-size: 28px; font-weight: 800; line-height: 1; display: block; }
.stat-num-blue { color: #2563EB; }
.stat-num-green { color: #059669; }
.stat-num-red { color: #DC2626; }
.stat-label { font-size: 13px; font-weight: 500; color: var(--color-text-secondary); }
.stat-card-footer {
  font-size: 12px; color: var(--color-text-tertiary);
  padding-top: var(--spacing-sm);
  border-top: 1px solid var(--color-border-light);
}

/* ── Overall Progress Bar ── */
.stats-overall-bar {
  display: flex; align-items: center; gap: var(--spacing-md);
  padding: var(--spacing-md) var(--spacing-lg);
  background: var(--color-bg-white);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border-light);
  margin-bottom: var(--spacing-xl);
}
.overall-bar-track {
  flex: 1; height: 10px;
  background: var(--color-border-light);
  border-radius: 5px; overflow: hidden;
}
.overall-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #2563EB, #3B82F6);
  border-radius: 5px;
  transition: width 0.6s ease;
  min-width: 2px;
}
.overall-bar-text {
  font-size: 14px; font-weight: 600; color: var(--color-primary);
  white-space: nowrap;
}

/* ── Empty State ── */
.stats-empty { padding: var(--spacing-3xl); }
.stats-empty-icon { font-size: 56px; margin-bottom: var(--spacing-md); opacity: 0.4; }

/* ── Detail Panel ── */
.detail-panel {
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-xl);
  background: var(--color-bg-white);
  overflow: hidden;
  margin-bottom: var(--spacing-lg);
  animation: fadeInUp 0.3s ease;
}
.detail-inner { max-height: 400px; display: flex; flex-direction: column; }
.detail-header {
  display: flex; align-items: center; gap: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--color-border-light);
  background: var(--color-bg);
}
.detail-header h3 { font-size: 16px; font-weight: 600; flex: 1; }
.detail-count { font-size: 12px; color: var(--color-primary); background: var(--color-primary-50); padding: 3px 12px; border-radius: 12px; font-weight: 600; }
.detail-close { font-size: 18px; padding: 4px 10px; border-radius: 8px; }
.detail-close:hover { background: var(--color-border-light); }
.detail-body { flex: 1; overflow-y: auto; padding: var(--spacing-sm); }
.detail-item {
  display: flex; align-items: center; gap: var(--spacing-sm);
  padding: 10px 14px; border-radius: var(--radius-md);
  transition: background 0.15s ease;
}
.detail-item:hover { background: var(--color-bg-hover); }
.detail-avatar {
  width: 40px; height: 40px; border-radius: 50%;
  background: var(--color-primary-100); color: var(--color-primary);
  display: flex; align-items: center; justify-content: center;
  font-size: 15px; font-weight: 700; flex-shrink: 0;
}
.detail-info { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.detail-name { font-size: 14px; font-weight: 600; }
.detail-meta { font-size: 12px; color: var(--color-text-tertiary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ── Question Stats Card ── */
.stat-question {
  padding: var(--spacing-xl);
  margin-bottom: var(--spacing-md);
  border-radius: var(--radius-xl);
}
.stat-q-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: var(--spacing-lg);
}
.stat-q-header h4 { font-size: 16px; font-weight: 600; }

/* ── Option Table ── */
.pct-bar { display: flex; align-items: center; gap: var(--spacing-sm); }
.pct-fill {
  height: 8px;
  background: linear-gradient(90deg, #2563EB, #60A5FA);
  border-radius: 4px;
  min-width: 2px;
  transition: width 0.4s ease;
}
.chart-actions {
  display: flex; gap: 6px; margin-top: var(--spacing-lg);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--color-border-light);
}
.chart-actions button {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.15s ease;
}
.chart-actions .active {
  background: var(--color-primary) !important;
  color: #fff !important;
}
.chart-container { width: 100%; height: 320px; margin-top: var(--spacing-md); }

/* ── Average Display ── */
.avg-display {
  text-align: center; padding: var(--spacing-2xl);
  background: linear-gradient(135deg, var(--color-primary-50), #EEF2FF);
  border-radius: var(--radius-lg);
}
.avg-num { font-size: 48px; font-weight: 800; color: var(--color-primary); display: block; line-height: 1; }

/* ── Text Answers ── */
.text-answers { max-height: 400px; overflow-y: auto; }
.text-answer-item {
  padding: var(--spacing-sm) var(--spacing-md);
  border-bottom: 1px solid var(--color-border-light);
  display: flex; gap: var(--spacing-md); font-size: 14px;
  transition: background 0.15s;
}
.text-answer-item:hover { background: var(--color-bg); }
.text-answer-num { color: var(--color-text-tertiary); flex-shrink: 0; min-width: 30px; }

@media (max-width: 768px) {
  .stats-summary { grid-template-columns: 1fr; }
}
</style>
