<template>
  <div class="min-h-screen bg-background">
    <!-- Header -->
    <header class="sticky top-0 bg-white border-b border-[#E0E0E0] z-10">
      <div class="max-w-lg mx-auto px-4 py-4">
        <div class="flex items-center">
          <button @click="$emit('back')" class="mr-3">
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
              class="text-[#333333]"
            >
              <path d="m15 18-6-6 6-6"/>
            </svg>
          </button>
          <h1 class="text-[#333333]">도서 상세</h1>
        </div>
      </div>
    </header>

    <!-- Book Info -->
    <div class="max-w-lg mx-auto px-4 py-6">
      <div class="flex gap-4 mb-6">
        <div class="w-32 h-44 bg-[#f4f2e5] rounded-lg overflow-hidden flex-shrink-0">
          <img
            :src="book.cover_url"
            :alt="book.title"
            class="w-full h-full object-cover"
          />
        </div>
        <div class="flex-1">
          <h2 class="text-[#333333] mb-2">{{ book.title }}</h2>
          <p class="text-[#666666] mb-3" style="font-size: 0.875rem">
            {{ book.author }}
          </p>
          <div class="flex items-center gap-2 mb-2">
            <StarRating :rating="book.rating" :size="16" showScore />
          </div>
          <div class="inline-block px-3 py-1 bg-[#f4f2e5] rounded-full">
            <span class="text-[#333333]" style="font-size: 0.75rem">
              {{ book.category }}
            </span>
          </div>
        </div>
      </div>

      <!-- TOKTOK Section -->
      <div class="mb-20">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-[#333333]">
            TOKTOK <span class="text-[#666666]">({{ displayComments.length }})</span>
          </h3>
          <button
            v-if="isLoggedIn"
            @click="$emit('addComment')"
            class="px-4 py-2 bg-[#f4f2e5] text-[#333333] rounded-lg hover:bg-[#e8e6d9] transition-colors"
            style="font-size: 0.875rem"
          >
            TOKTOK 작성
          </button>
          <button
            v-else
            @click="$emit('loginClick')"
            class="px-4 py-2 bg-[#f4f2e5] text-[#333333] rounded-lg hover:bg-[#e8e6d9] transition-colors"
            style="font-size: 0.875rem"
          >
            로그인하고 작성하기
          </button>
        </div>

        <!-- Login Required Message -->
        <div v-if="!isLoggedIn" class="bg-[#F3D8D8] rounded-lg p-4 mb-4">
          <p class="text-[#666666] text-center" style="font-size: 0.875rem">
            TOKTOK을 보려면 로그인이 필요합니다
          </p>
          <button
            @click="$emit('loginClick')"
            class="w-full mt-3 py-2 bg-white text-[#333333] rounded-lg hover:bg-[#FAFAFA] transition-colors"
            style="font-size: 0.875rem"
          >
            로그인
          </button>
        </div>

        <!-- Comments List -->
        <div v-else-if="displayComments.length === 0" class="text-center py-8">
          <p class="text-[#666666]">아직 TOKTOK이 없습니다</p>
          <p class="text-[#999999] mt-2" style="font-size: 0.875rem">
            첫 번째 TOKTOK을 남겨보세요!
          </p>
        </div>
        <div v-else>
          <VoiceComment
            v-for="comment in displayComments"
            :key="comment.id"
            :comment="comment"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import StarRating from './StarRating.vue';
import VoiceComment from './VoiceComment.vue';

const props = defineProps({
  book: {
    type: Object,
    required: true
  },
  comments: {
    type: Array,
    default: () => []
  },
  isLoggedIn: {
    type: Boolean,
    required: true
  }
});

defineEmits(['back', 'addComment', 'loginClick']);

const displayComments = computed(() => {
  return props.isLoggedIn ? props.comments : [];
});
</script>