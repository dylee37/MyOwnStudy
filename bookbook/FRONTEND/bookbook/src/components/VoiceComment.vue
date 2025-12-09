<template>
  <div
    :class="[
      'flex gap-3 mb-4',
      comment.is_mine ? 'flex-row-reverse' : 'flex-row'
    ]"
  >
    <!-- Avatar -->
    <div class="w-10 h-10 rounded-full bg-[#f4f2e5] flex items-center justify-center flex-shrink-0">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="text-[#333333]"
      >
        <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/>
        <circle cx="12" cy="7" r="4"/>
      </svg>
    </div>

    <!-- Comment Content -->
    <div :class="['flex-1', comment.is_mine ? 'items-end' : 'items-start', 'flex flex-col']">
      <div class="flex items-center gap-2 mb-1">
        <span class="text-[#333333]" style="font-size: 0.875rem">
          {{ comment.user_name }}
        </span>
        <StarRating :rating="comment.rating" :size="12" />
      </div>

      <!-- Voice/Text Bubble -->
      <div
        :class="[
          'rounded-2xl px-4 py-3 max-w-xs',
          comment.is_mine
            ? 'bg-[#f4f2e5] rounded-br-sm'
            : 'bg-white border border-[#E0E0E0] rounded-bl-sm'
        ]"
      >
        <p class="text-[#333333]" style="font-size: 0.875rem">
          {{ comment.text }}
        </p>

        <!-- Voice Player (if voice comment) -->
        <div v-if="comment.voice_url && comment.voice_url !== 'mock_url'" class="mt-2 flex items-center gap-2">
          <button
            @click="togglePlay"
            class="w-8 h-8 rounded-full bg-[#333333] flex items-center justify-center hover:bg-[#555555] transition-colors"
          >
            <svg
              v-if="!isPlaying"
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="white"
              stroke="white"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <polygon points="5 3 19 12 5 21 5 3"/>
            </svg>
            <svg
              v-else
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="white"
              stroke="white"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <rect x="6" y="4" width="4" height="16"/>
              <rect x="14" y="4" width="4" height="16"/>
            </svg>
          </button>
          <div class="flex-1 h-1 bg-[#E0E0E0] rounded-full overflow-hidden">
            <div class="h-full bg-[#333333]" :style="{ width: '0%' }"></div>
          </div>
        </div>
      </div>

      <span class="text-[#999999] mt-1" style="font-size: 0.75rem">
        {{ formatTime(comment.created_at) }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import StarRating from './StarRating.vue';

defineProps({
  comment: {
    type: Object,
    required: true
  }
});

const isPlaying = ref(false);

const togglePlay = () => {
  isPlaying.value = !isPlaying.value;
  // 실제 음성 재생 로직은 여기에 구현
};

const formatTime = (dateString) => {
  const date = new Date(dateString);
  const now = new Date();
  const diff = Math.floor((now - date) / 1000); // seconds

  if (diff < 60) return '방금 전';
  if (diff < 3600) return `${Math.floor(diff / 60)}분 전`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}시간 전`;
  if (diff < 604800) return `${Math.floor(diff / 86400)}일 전`;
  
  return date.toLocaleDateString('ko-KR', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });
};
</script>