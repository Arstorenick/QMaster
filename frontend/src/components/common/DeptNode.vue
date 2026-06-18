<template>
  <div class="dept-node">
    <div
      class="dept-node-row"
      :class="{ active: activeId === dept.id }"
      :style="{ paddingLeft: (level * 18 + 10) + 'px' }"
      @click.stop="$emit('select', dept)"
      @dblclick.stop="dept.children?.length && (expanded = !expanded)"
    >
      <span class="dept-expand" :class="{ expanded }" @click.stop="expanded = !expanded" v-if="dept.children?.length">{{ expanded ? '▾' : '▸' }}</span>
      <span v-else class="dept-expand-placeholder"></span>
      <img :src="expanded ? folderOpenImg : folderCloseImg" alt="folder" class="dept-icon" />
      <span class="dept-name" v-html="highlightName(dept.name)"></span>
      <span class="dept-count" v-if="dept.member_count > 0">{{ dept.member_count }}</span>
      <button v-if="$parent?.auth?.isCreator" class="dept-delete" @click.stop="$emit('delete', dept.id)">×</button>
    </div>
    <transition name="slide">
      <div v-if="expanded && dept.children?.length">
        <DeptNode
          v-for="child in dept.children" :key="child.id"
          :dept="child" :level="level + 1"
          :active-id="activeId" :search="search"
          @select="$emit('select', $event)"
          @delete="$emit('delete', $event)"
        />
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import folderCloseImg from '../../assets/folder_close.png'
import folderOpenImg from '../../assets/folder_open.png'

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
  const kw = props.search
  const idx = name.toLowerCase().indexOf(kw.toLowerCase())
  if (idx === -1) return name
  return name.slice(0, idx) + '<mark>' + name.slice(idx, idx + kw.length) + '</mark>' + name.slice(idx + kw.length)
}
</script>

<style scoped>
.dept-node-row {
  display: flex; align-items: center; gap: 6px;
  padding: 7px 12px; margin: 1px 4px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.15s ease;
  border-left: 3px solid transparent;
}
.dept-node-row:hover {
  background: var(--color-primary-50);
  border-left-color: var(--color-primary-100);
}
.dept-node-row.active {
  background: var(--color-primary-light);
  border-left-color: var(--color-primary);
}
.dept-expand {
  width: 20px; height: 20px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; color: var(--color-text-tertiary);
  border-radius: 4px; transition: all 0.15s ease;
}
.dept-expand.expanded {
  color: var(--color-text-primary);
}
.dept-expand:hover { background: var(--color-border-light); color: var(--color-text-primary); }
.dept-node-row:hover .dept-expand { transform: none; }
.dept-expand-placeholder { width: 20px; flex-shrink: 0; }
.dept-icon { width: 18px; height: 18px; flex-shrink: 0; object-fit: contain; }
.dept-name {
  flex: 1; font-size: 13px; font-weight: 500;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  color: var(--color-text-primary);
}
.dept-name :deep(mark) { background: #FDE68A; color: #92400E; border-radius: 2px; padding: 0 1px; }
.dept-count {
  font-size: 11px; font-weight: 600; color: var(--color-primary);
  background: var(--color-primary-50); padding: 1px 7px;
  border-radius: 10px; flex-shrink: 0; min-width: 20px; text-align: center;
}
.dept-delete {
  background: none; border: none; color: var(--color-text-tertiary);
  cursor: pointer; font-size: 16px; padding: 0 4px; line-height: 1;
  opacity: 0; transition: all 0.15s ease; border-radius: 4px;
}
.dept-node-row:hover .dept-delete { opacity: 1; }
.dept-delete:hover { color: var(--color-danger); background: var(--color-danger-light); }

.slide-enter-active, .slide-leave-active { transition: all 0.2s ease; }
.slide-enter-from, .slide-leave-to { opacity: 0; transform: translateY(-4px); }
</style>
