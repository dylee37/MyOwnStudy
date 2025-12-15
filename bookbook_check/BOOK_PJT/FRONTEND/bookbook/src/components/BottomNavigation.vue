<template>
  <nav class="fixed bottom-0 left-0 right-0 bg-white border-t border-[#E0E0E0] z-20">
    <div class="max-w-lg mx-auto px-4">
      <div class="flex items-center justify-around py-3">
        <button
          @click="$emit('tabChange', 'home')"
          :class="[
            'flex flex-col items-center gap-1 px-4 py-2 transition-colors',
            activeTab === 'home' ? 'text-[#333333]' : 'text-[#999999]'
          ]"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            :fill="activeTab === 'home' ? 'currentColor' : 'none'"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
            <polyline points="9 22 9 12 15 12 15 22"/>
          </svg>
          <span style="font-size: 0.75rem">홈</span>
        </button>

        <button
          @click="$emit('tabChange', 'library')"
          :class="[
            'flex flex-col items-center gap-1 px-4 py-2 transition-colors',
            activeTab === 'library' ? 'text-[#333333]' : 'text-[#999999]'
          ]"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            :fill="activeTab === 'library' ? 'currentColor' : 'none'"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/>
          </svg>
          <span style="font-size: 0.75rem">나의 북북</span>
        </button>

        <button
          @click="$emit('tabChange', 'profile')"
          :class="[
            'flex flex-col items-center gap-1 px-4 py-2 transition-colors',
            activeTab === 'profile' ? 'text-[#333333]' : 'text-[#999999]'
          ]"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            :fill="activeTab === 'profile' ? 'currentColor' : 'none'"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
          <span style="font-size: 0.75rem">프로필</span>
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup>
defineProps({
  activeTab: {
    type: String,
    required: true
  }
});

defineEmits(['tabChange']);
</script>