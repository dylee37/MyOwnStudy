<template>
  <Transition name="toast">
    <div v-if="show" class="toast-container">
      <div class="toast-content">
        <span class="message">{{ message }}</span>
      </div>
    </div>
  </Transition>
</template>

<script setup>
defineProps({
  show: Boolean,
  message: String
});
</script>

<style scoped>
.toast-container {
  position: fixed;
  bottom: 100px; 
  left: 0;
  right: 0;
  display: flex;
  justify-content: center; 
  z-index: 9999;
  pointer-events: none; 
}

.toast-content {
  background-color: rgba(51, 51, 51, 0.9);
  color: #ffffff;
  padding: 12px 24px;
  border-radius: 50px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
  pointer-events: auto;
}

.message {
  font-size: 0.875rem;
  font-weight: 500;
  white-space: nowrap; 
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); 
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(20px); 
}

.toast-enter-to,
.toast-leave-from {
  opacity: 1;
  transform: translateY(0); 
}
</style>