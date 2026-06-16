<template>
  <div class="template-page" v-if="template">
    <div class="container" style="max-width:700px;margin:0 auto;padding:var(--spacing-lg)">
      <div class="card" style="padding:var(--spacing-xl)">
        <h2>{{ template.title }}</h2>
        <p class="text-secondary mt-sm" v-if="template.description">{{ template.description }}</p>
        <div v-for="q in template.questions" :key="q.id" class="tq-item">
          <h4>{{ q.title }} <span class="tag tag-primary">{{ q.type }}</span></h4>
          <div v-if="q.options?.length" class="tq-options">
            <div v-for="opt in q.options" :key="opt.id" class="tq-option">○ {{ opt.title }}</div>
          </div>
        </div>
        <div class="mt-lg" style="display:flex;gap:12px">
          <button class="btn btn-primary" @click="cloneTemplate">使用此模板</button>
          <router-link to="/home" class="btn btn-secondary">返回</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { templatesAPI } from '../api'

const route = useRoute()
const router = useRouter()
const template = ref(null)

onMounted(async () => {
  const { data } = await templatesAPI.get(route.params.id)
  template.value = data
})

async function cloneTemplate() {
  const { data } = await templatesAPI.clone(route.params.id, {})
  router.push('/home')
}
</script>

<style scoped>
.tq-item {
  padding: var(--spacing-md) 0;
  border-bottom: 1px solid var(--color-border-light);
}
.tq-item h4 {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
}
.tq-options {
  padding-left: var(--spacing-lg);
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.tq-option {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}
</style>
