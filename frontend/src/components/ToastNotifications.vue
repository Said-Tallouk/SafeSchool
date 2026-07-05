<script setup>
import { useNotifStore } from '../stores/notifications'
const notif = useNotifStore()
</script>

<template>
  <Teleport to="body">
    <div class="toast-container">
      <TransitionGroup name="toast">
        <div v-for="t in notif.toasts" :key="t.id"
             :class="['toast', 'toast-' + t.type]"
             @click="notif.remove(t.id)">
          <span class="toast-icon">
            {{ t.type === 'success' ? '✅' : t.type === 'error' ? '❌' : t.type === 'warning' ? '⚠️' : 'ℹ️' }}
          </span>
          <span class="toast-msg">{{ t.message }}</span>
          <button class="toast-close">✕</button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<style scoped>
.toast-container {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 360px;
  width: calc(100vw - 48px);
}

.toast {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 13px 16px;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 600;
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255,255,255,0.2);
}

.toast-success { background: #166534; color: white; }
.toast-error   { background: #991b1b; color: white; }
.toast-info    { background: #1e40af; color: white; }
.toast-warning { background: #92400e; color: white; }

.toast-icon { font-size: 1rem; flex-shrink: 0; }
.toast-msg  { flex: 1; line-height: 1.4; }
.toast-close {
  background: none; border: none;
  color: rgba(255,255,255,0.7);
  cursor: pointer; font-size: 0.85rem;
  padding: 0; flex-shrink: 0;
  transition: color 0.2s;
}
.toast-close:hover { color: white; }

/* Transition */
.toast-enter-active { transition: all 0.3s cubic-bezier(0.34,1.56,0.64,1); }
.toast-leave-active { transition: all 0.25s ease-in; }
.toast-enter-from   { opacity: 0; transform: translateX(60px) scale(0.9); }
.toast-leave-to     { opacity: 0; transform: translateX(60px); }
</style>
