<template>
  <div class="min-h-screen bg-background pb-20">
    <!-- Header -->
    <header class="sticky top-0 bg-white border-b border-[#E0E0E0] z-10">
      <div class="max-w-lg mx-auto px-4 py-4">
        <h1 class="text-[#333333]" style="font-size: 1.8rem; font-weight: bold;">나의 북북</h1>
      </div>
    </header>

    <!-- Content -->
    <div v-if="!isLoggedIn" class="flex flex-col items-center justify-center px-6 py-20">
      <div class="w-20 h-20 rounded-full bg-[#f4f2e5] flex items-center justify-center mb-6">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="40"
          height="40"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="text-[#333333]"
        >
          <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/>
        </svg>
      </div>
      <p class="text-[#333333] mb-6 text-center">
        로그인하고 내 서재를 확인하세요
      </p>
      <button
        @click="$emit('loginClick')"
        class="px-8 py-3 bg-[#f4f2e5] text-[#333333] rounded-lg hover:bg-[#e8e6d9] transition-colors"
      >
        로그인
      </button>
    </div>

    <main v-else class="max-w-lg mx-auto px-4 py-6">
      <div v-if="books.length === 0" class="text-center py-20">
        <p class="text-[#666666]">아직 추가된 책이 없습니다</p>
      </div>
      <div v-else class="grid grid-cols-2 gap-4">
        <BookCard
          v-for="book in books"
          :key="book.id"
          :book="book"
          @click="$emit('bookClick', book)"
        />
      </div>
    </main>
  </div>
</template>

<script setup>
import BookCard from './BookCard.vue';

defineProps({
  books: {
    type: Array,
    required: true
  },
  isLoggedIn: {
    type: Boolean,
    required: true
  }
});

defineEmits(['bookClick', 'loginClick']);
</script>