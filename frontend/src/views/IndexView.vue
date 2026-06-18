<template>
  <div class="index-page">
    <!-- 未登录 -->
    <template v-if="!auth.isLoggedIn">
      <section class="hero">
        <div class="container text-center">
          <h1 class="hero-title">轻松创建<span class="highlight">专业问卷</span></h1>
          <p class="hero-desc">
            多种题型自由搭配，数据实时分析，一键分享收集
          </p>
          <div class="hero-actions">
            <router-link to="/login" class="btn btn-primary hero-cta">开始使用</router-link>
          </div>
        </div>
      </section>
      <section class="features container">
        <div class="feature-grid">
          <div class="card feature-card" v-for="f in features" :key="f.title">
            <div class="feature-icon">
              <img v-if="f.img" :src="f.img" :alt="f.title" class="feature-img" />
              <span v-else>{{ f.icon }}</span>
            </div>
            <h4>{{ f.title }}</h4>
            <p>{{ f.desc }}</p>
          </div>
        </div>
      </section>
    </template>

    <!-- 答题人登录后 -->
    <template v-else-if="!auth.isCreator">
      <section class="hero">
        <div class="container text-center">
          <p style="font-size:56px;margin-bottom:16px">👋</p>
          <h1 class="hero-title">欢迎，{{ auth.user?.username }}</h1>
          <p class="hero-desc">
            您可以通过管理员分享的问卷链接参与填写
          </p>
          <p class="text-secondary text-sm">
            当前角色：<span class="tag tag-primary">{{ auth.user?.role_label }}</span>
          </p>
        </div>
      </section>
    </template>

    <footer class="footer text-center text-secondary">
      <p>QMaster &copy; {{ new Date().getFullYear() }} · 问卷调查系统 By Zivian</p>
    </footer>
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'
import chartsImg from '../assets/charts.png'
import analysisImg from '../assets/analysis.png'
import customImg from '../assets/custom.png'
import mobileImg from '../assets/mobile.png'
import exportImg from '../assets/export.png'
import safeImg from '../assets/safe.png'

const auth = useAuthStore()

const features = [
  { img: chartsImg, title: '多种题型', desc: '单选、多选、填空...满足一切调研场景' },
  { img: analysisImg, title: '实时分析', desc: '柱状图、饼图、交叉分析，数据一目了然' },
  { img: customImg, title: '自由样式', desc: '评分、跳转、分段、分页，打造专属问卷' },
  { img: mobileImg, title: '移动端适配', desc: '手机端自适用，随时随地填写' },
  { img: exportImg, title: '一键导出', desc: 'Excel格式导出，轻松查看数据' },
  { img: safeImg, title: '数据安全', desc: '私有化部署，数据完全掌握在自己手中' },
]
</script>

<style scoped>
.index-page {
  min-height: calc(100vh - var(--header-height));
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.hero {
  padding: var(--spacing-xl) 0 var(--spacing-md);
}
.hero-title {
  font-size: var(--font-size-3xl);
  margin-bottom: var(--spacing-sm);
}
.highlight {
  background: linear-gradient(135deg, var(--color-primary), #818CF8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.hero-desc {
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
  max-width: 480px;
  margin: 0 auto var(--spacing-lg);
}
.hero-actions {
  display: flex;
  justify-content: center;
}
.hero-cta {
  min-width: 220px;
  padding: 14px 48px;
  font-size: var(--font-size-lg);
  color: #fff !important;
}
.hero-cta:hover {
  color: #fff !important;
}
.features {
  padding: var(--spacing-md) var(--spacing-lg);
}
.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-md);
}
.feature-card {
  padding: var(--spacing-lg);
  text-align: center;
}
.feature-icon {
  font-size: 28px;
  margin-bottom: var(--spacing-sm);
}
.feature-img {
  width: 65px;
  height: 65px;
  object-fit: contain;
}
.feature-card h4 {
  margin-bottom: var(--spacing-xs);
  font-size: var(--font-size-sm);
}
.feature-card p {
  color: var(--color-text-secondary);
  font-size: var(--font-size-xs);
}
.footer {
  padding: var(--spacing-md) 0;
}
@media (max-width: 768px) {
  .feature-grid {
    grid-template-columns: 1fr;
  }
  .hero-title {
    font-size: var(--font-size-2xl);
  }
}
</style>
