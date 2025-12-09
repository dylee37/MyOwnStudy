<template>
  <div class="min-h-screen bg-background pb-20">
    <!-- Header -->
    <header class="sticky top-0 bg-white border-b border-[#E0E0E0] z-10">
      <div class="max-w-lg mx-auto px-4 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-[#333333]">BOOKBOOK</h1>
            <p class="text-[#666666] mt-1" style="font-size: 0.875rem">
              TOKTOK으로 나누는 독서 경험
            </p>
          </div>
          <button
            @click="$emit('searchClick')"
            class="p-2 hover:bg-[#FAFAFA] rounded-full transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-[#333333]">
              <circle cx="11" cy="11" r="8"/>
              <path d="m21 21-4.3-4.3"/>
            </svg>
          </button>
        </div>
      </div>
    </header>

    <div class="max-w-lg mx-auto px-4 py-6">
      <div class="mb-6">
        <h2 class="text-[#333333] mb-4" style="font-weight: 700">이번 주 베스트셀러</h2>
        <div class="grid grid-cols-2 gap-4">
          <BookCard
            v-for="book in books.slice(0, 6)"
            :key="book.id"
            :book="book"
            @click="$emit('bookClick', book)"
          />
        </div>
      </div>

      <div>
        <h2 class="text-[#333333] mb-4" style="font-weight: 700">추천 도서</h2>
        <div class="grid grid-cols-2 gap-4">
          <BookCard
            v-for="book in books.slice(6)"
            :key="book.id"
            :book="book"
            @click="$emit('bookClick', book)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import BookCard from './BookCard.vue';

defineProps({
  books: {
    type: Array,
    required: true
  }
});

defineEmits(['bookClick', 'searchClick']);
</script>