<template>
  <div class="cascade-node">
    <div
      class="cascade-item"
      :class="{ active: activeId === dept.id }"
      :style="{ paddingLeft: (level * 20 + 8) + 'px' }"
    >
      <span
        class="cascade-expand"
        :class="{ expanded: expanded }"
        @click.stop="expanded = !expanded"
        v-if="dept.children?.length"
      >▸</span>
      <span v-else class="cascade-expand-placeholder"></span>
      <label class="cascade-label" @click.stop="toggleCheck">
        <input
          type="checkbox"
          :checked="checked"
          :indeterminate.prop="indeterminate"
          @click.stop
          @change="toggleCheck"
          class="cascade-checkbox"
        />
        <span class="cascade-name">{{ dept.name }}</span>
      </label>
      <span class="cascade-count" v-if="dept.member_count">{{ dept.member_count }}</span>
    </div>
    <template v-if="expanded && dept.children?.length">
      <DeptCascadeNode
        v-for="child in dept.children" :key="child.id"
        :dept="child" :level="level + 1"
        :active-id="activeId"
        :checked-ids="checkedIds"
        @check="(id, val) => $emit('check', id, val)"
        @select="$emit('select', $event)"
      />
    </template>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  dept: Object,
  level: { type: Number, default: 0 },
  activeId: Number,
  checkedIds: { type: Set, default: () => new Set() },
})

const emit = defineEmits(['select', 'check'])
const expanded = ref(false)

const checked = computed(() => props.checkedIds.has(props.dept.id))

const indeterminate = computed(() => {
  if (checked.value) return false
  if (!props.dept.children?.length) return false
  function hasChecked(list) {
    for (const d of list) {
      if (props.checkedIds.has(d.id)) return true
      if (d.children?.length && hasChecked(d.children)) return true
    }
    return false
  }
  return hasChecked(props.dept.children)
})

function toggleCheck() {
  emit('check', props.dept.id, !checked.value)
  emit('select', props.dept)
}
</script>

<style scoped>
.cascade-item {
  display: flex; align-items: center; gap: 4px;
  padding: 6px 10px; border-radius: var(--radius-sm);
  transition: background var(--transition-fast); white-space: nowrap;
}
.cascade-item:hover { background: var(--color-bg-hover); }
.cascade-item.active { background: var(--color-primary-light); }
.cascade-expand {
  width: 16px; height: 16px; flex-shrink: 0; display: flex; align-items: center; justify-content: center;
  font-size: 12px; color: var(--color-text-tertiary); cursor: pointer; border-radius: 3px;
  transition: transform var(--transition-fast);
}
.cascade-expand:hover { background: var(--color-border-light); }
.cascade-expand.expanded { transform: rotate(90deg); }
.cascade-expand-placeholder { width: 16px; flex-shrink: 0; }
.cascade-label { display: flex; align-items: center; gap: 6px; flex: 1; cursor: pointer; min-width: 0; }
.cascade-checkbox { width: 15px; height: 15px; accent-color: var(--color-primary); cursor: pointer; flex-shrink: 0; }
.cascade-name { font-size: var(--font-size-sm); overflow: hidden; text-overflow: ellipsis; }
.cascade-count { font-size: var(--font-size-xs); color: var(--color-text-tertiary); flex-shrink: 0; }
</style>
