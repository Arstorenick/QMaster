<template>
  <div>
    <div
      class="pub-item"
      :class="{ checked: isChecked }"
      :style="{ paddingLeft: (level * 22 + 10) + 'px' }"
      @click="$emit('toggle', dept.id)"
    >
      <span class="pub-expand" :class="{ open: expanded }" @click.stop="expanded = !expanded" v-if="dept.children?.length">▸</span>
      <span v-else class="pub-expand-placeholder"></span>
      <span class="pub-checkbox" :class="{ checked: isChecked }">
        <span v-if="isChecked" class="check-mark">✓</span>
      </span>
      <span class="pub-name">{{ dept.name }}</span>
      <span class="pub-count" v-if="dept.member_count">{{ dept.member_count }} 人</span>
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
const expanded = ref(props.level < 1)
const isChecked = computed(() => props.checkedIds.includes(props.dept.id))
</script>

<style scoped>
.pub-item {
  display: flex; align-items: center; gap: 8px;
  padding: 7px 10px; margin: 1px 0;
  border-radius: var(--radius-md);
  cursor: pointer; user-select: none;
  transition: all 0.15s ease;
  border-left: 3px solid transparent;
}
.pub-item:hover { background: var(--color-bg-hover); }
.pub-item.checked {
  background: var(--color-primary-50);
  border-left-color: var(--color-primary);
}
.pub-expand {
  width: 26px; height: 26px; font-size: 16px;
  color: var(--color-text-tertiary); cursor: pointer; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  border-radius: 4px; transition: transform 0.2s ease;
}
.pub-expand:hover { background: var(--color-border-light); color: var(--color-text-primary); }
.pub-expand.open { transform: rotate(90deg); }
.pub-expand-placeholder { width: 26px; flex-shrink: 0; }
.pub-checkbox {
  width: 18px; height: 18px; flex-shrink: 0;
  border: 2px solid var(--color-border);
  border-radius: 4px;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.15s ease;
}
.pub-checkbox.checked {
  background: var(--color-primary);
  border-color: var(--color-primary);
}
.check-mark { color: #fff; font-size: 11px; font-weight: 700; line-height: 1; }
.pub-name { flex: 1; font-size: 13px; font-weight: 500; }
.pub-count {
  font-size: 11px; font-weight: 500;
  color: var(--color-primary);
  background: var(--color-primary-50);
  padding: 2px 8px; border-radius: 10px;
  flex-shrink: 0;
}
</style>
