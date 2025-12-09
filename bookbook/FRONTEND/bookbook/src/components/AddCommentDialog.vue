<template>
  <Teleport to="body">
    <div
      v-if="isOpen"
      class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-end sm:items-center justify-center"
      @click.self="$emit('close')"
    >
      <div class="bg-white rounded-t-3xl sm:rounded-3xl w-full max-w-lg p-6 max-h-[90vh] overflow-y-auto">
        <!-- Header -->
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-[#333333]">TOKTOK 작성</h2>
          <button @click="$emit('close')" class="p-1">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="text-[#666666]"
            >
              <line x1="18" x2="6" y1="6" y2="18"/>
              <line x1="6" x2="18" y1="6" y2="18"/>
            </svg>
          </button>
        </div>

        <!-- Type Selection -->
        <div class="flex gap-2 mb-6">
          <button
            @click="commentType = 'text'"
            :class="[
              'flex-1 py-3 rounded-lg transition-colors',
              commentType === 'text'
                ? 'bg-[#f4f2e5] text-[#333333]'
                : 'bg-white text-[#666666] border border-[#E0E0E0]'
            ]"
          >
            텍스트
          </button>
          <button
            @click="commentType = 'voice'"
            :class="[
              'flex-1 py-3 rounded-lg transition-colors',
              commentType === 'voice'
                ? 'bg-[#f4f2e5] text-[#333333]'
                : 'bg-white text-[#666666] border border-[#E0E0E0]'
            ]"
          >
            음성
          </button>
        </div>

        <!-- Rating -->
        <div class="mb-6">
          <label class="block text-[#333333] mb-3" style="font-size: 0.875rem">
            평점 ({{ selectedRating }}/10)
          </label>
          <div class="flex justify-center">
            <StarRating
              :rating="selectedRating"
              :size="32"
              :onRatingChange="handleRatingChange"
            />
          </div>
        </div>

        <!-- Text Input -->
        <div v-if="commentType === 'text'" class="mb-6">
          <label class="block text-[#333333] mb-2" style="font-size: 0.875rem">
            댓글 내용
          </label>
          <textarea
            v-model="commentText"
            placeholder="책에 대한 생각을 자유롭게 남겨주세요"
            class="w-full px-4 py-3 bg-[#FAFAFA] rounded-lg border border-[#E0E0E0] focus:outline-none focus:border-[#f4f2e5] resize-none"
            rows="5"
          ></textarea>
        </div>

        <!-- Voice Recording -->
        <div v-else class="mb-6">
          <label class="block text-[#333333] mb-3" style="font-size: 0.875rem">
            음성 녹음
          </label>
          <div class="bg-[#FAFAFA] rounded-lg p-6 flex flex-col items-center">
            <button
              @click="toggleRecording"
              :class="[
                'w-16 h-16 rounded-full flex items-center justify-center transition-colors mb-3',
                isRecording ? 'bg-red-500 hover:bg-red-600' : 'bg-[#f4f2e5] hover:bg-[#e8e6d9]'
              ]"
            >
              <svg
                v-if="!isRecording"
                xmlns="http://www.w3.org/2000/svg"
                width="32"
                height="32"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="text-[#333333]"
              >
                <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                <line x1="12" x2="12" y1="19" y2="22"/>
              </svg>
              <svg
                v-else
                xmlns="http://www.w3.org/2000/svg"
                width="32"
                height="32"
                viewBox="0 0 24 24"
                fill="white"
                stroke="white"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <rect x="6" y="4" width="12" height="16" rx="2"/>
              </svg>
            </button>
            <p class="text-[#666666]" style="font-size: 0.875rem">
              {{ isRecording ? '녹음 중...' : '버튼을 눌러 녹음 시작' }}
            </p>
            <textarea
              v-model="commentText"
              placeholder="음성 댓글의 텍스트 버전을 입력하세요 (선택사항)"
              class="w-full mt-4 px-4 py-3 bg-white rounded-lg border border-[#E0E0E0] focus:outline-none focus:border-[#f4f2e5] resize-none"
              rows="3"
            ></textarea>
          </div>
        </div>

        <!-- Submit Button -->
        <button
          @click="handleSubmit"
          :disabled="!canSubmit"
          :class="[
            'w-full py-3 rounded-lg transition-colors',
            canSubmit
              ? 'bg-[#f4f2e5] text-[#333333] hover:bg-[#e8e6d9]'
              : 'bg-[#E0E0E0] text-[#999999] cursor-not-allowed'
          ]"
        >
          TOKTOK 등록
        </button>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed } from 'vue';
import StarRating from './StarRating.vue';

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true
  }
});

const emit = defineEmits(['close', 'submit']);

const commentType = ref('text');
const commentText = ref('');
const selectedRating = ref(8);
const isRecording = ref(false);

const canSubmit = computed(() => {
  if (commentType.value === 'text') {
    return commentText.value.trim().length > 0;
  }
  return true; // 음성은 녹음만 있으면 OK
});

const handleRatingChange = (rating) => {
  selectedRating.value = rating;
};

const toggleRecording = () => {
  isRecording.value = !isRecording.value;
  // 실제 녹음 로직은 여기에 구현
};

const handleSubmit = () => {
  if (!canSubmit.value) return;
  
  emit('submit', {
    text: commentText.value,
    isVoice: commentType.value === 'voice',
    rating: selectedRating.value
  });
  
  // Reset
  commentText.value = '';
  selectedRating.value = 8;
  commentType.value = 'text';
  isRecording.value = false;
};
</script>