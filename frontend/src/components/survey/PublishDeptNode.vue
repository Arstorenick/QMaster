<template>
  <div>
    <div class="pub-item" :style="{ paddingLeft: (level * 20 + 8) + 'px' }">
      <span class="pub-expand" :class="{ open: expanded }" @click.stop="expanded = !expanded" v-if="dept.children?.length">▸</span>
      <span v-else class="pub-expand-placeholder"></span>
      <input type="checkbox" :checked="isChecked" class="pub-check" @change="$emit('toggle', dept.id)" />
      <span class="pub-name" @click="$emit('toggle', dept.id)">{{ dept.name }}</span>
      <span class="pub-count" v-if="dept.member_count">{{ dept.member_count }}人</span>
    </div>
    <div v-if="expanded && dept.children?.length">
      <PublishDeptNode v-for="c in dept.children" :key="c.id" :dept="c" :level="level + 1" :checked-ids="checkedIds" @toggle="(id) => $emit('toggle', id)" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
const props = defineProps({ dept: Object, level: Number, checkedIds: Array })
defineEmits(['toggle'])
const expanded = ref(false)
const isChecked = computed(() => props.checkedIds.includes(props.dept.id))
</script>

<style scoped>
.pub-item { display: flex; align-items: center; gap: 6px; padding: 5px 8px; border-radius: 4px; }
.pub-item:hover { background: var(--color-bg-hover); }
.pub-expand { width: 20px; height: 20px; font-size: 14px; color: var(--color-text-tertiary); cursor: pointer; flex-shrink: 0; display: flex; align-items: center; justify-content: center; border-radius: 4px; transition: transform 0.15s ease; }
.pub-expand:hover { background: var(--color-border-light); }
.pub-expand.open { transform: rotate(90deg); }
.pub-expand-placeholder { width: 14px; flex-shrink: 0; }
.pub-check { width: 15px; height: 15px; accent-color: var(--color-primary); cursor: pointer; flex-shrink: 0; }
.pub-name { flex: 1; font-size: 13px; cursor: pointer; }
.pub-count { font-size: 11px; color: var(--color-text-tertiary); flex-shrink: 0; }
</style>
