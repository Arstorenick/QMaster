<template>
  <div class="dept-node">
    <div
      class="dept-node-row"
      :class="{ active: activeId === dept.id }"
      :style="{ paddingLeft: (level * 16 + 8) + 'px' }"
      @click.stop="$emit('select', dept)"
    >
      <span class="dept-expand" @click.stop="expanded = !expanded" v-if="dept.children?.length">
        {{ expanded ? '▾' : '▸' }}
      </span>
      <span v-else class="dept-expand-placeholder"></span>
      <span class="dept-icon">{{ expanded ? '📂' : '📁' }}</span>
      <span class="dept-name">{{ highlightName(dept.name) }}</span>
      <span class="dept-count">{{ dept.member_count }}</span>
      <button
        v-if="$parent.auth?.isCreator"
        class="dept-delete"
        @click.stop="$emit('delete', dept.id)"
        title="删除"
      >×</button>
    </div>
    <div v-if="expanded && dept.children?.length">
      <DeptNode
        v-for="child in dept.children" :key="child.id"
        :dept="child" :level="level + 1"
        :active-id="activeId" :search="search"
        @select="$emit('select', $event)"
        @delete="$emit('delete', $event)"
      />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  dept: Object,
  level: { type: Number, default: 0 },
  activeId: Number,
  search: { type: String, default: '' },
})

defineEmits(['select', 'delete'])

const expanded = ref(props.level < 2)

function highlightName(name) {
  if (!props.search) return name
  const idx = name.toLowerCase().indexOf(props.search.toLowerCase())
  if (idx === -1) return name
  return name.slice(0, idx) + '<mark>' + name.slice(idx, idx + props.search.length) + '</mark>' + name.slice(idx + props.search.length)
}
</script>

<style scoped>
.dept-node-row {
  display: flex; align-items: center; gap: 4px;
  padding: 6px 8px; border-radius: var(--radius-md);
  cursor: pointer; transition: background var(--transition-fast);
}
.dept-node-row:hover { background: var(--color-bg-hover); }
.dept-node-row.active { background: var(--color-primary-light); }
.dept-expand { font-size: 10px; color: var(--color-text-tertiary); width: 12px; flex-shrink: 0; }
.dept-expand-placeholder { width: 12px; flex-shrink: 0; }
.dept-icon { font-size: 14px; flex-shrink: 0; }
.dept-name { flex: 1; font-size: var(--font-size-sm); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.dept-name :deep(mark) { background: #FDE68A; color: var(--color-text-primary); border-radius: 2px; }
.dept-count { font-size: var(--font-size-xs); color: var(--color-text-tertiary); flex-shrink: 0; }
.dept-delete { background: none; border: none; color: var(--color-danger); cursor: pointer; font-size: 14px; padding: 0 4px; opacity: 0; transition: opacity var(--transition-fast); }
.dept-node-row:hover .dept-delete { opacity: 1; }
</style>
