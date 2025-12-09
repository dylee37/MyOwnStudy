<template>
  <Teleport to="body">
    <div
      v-if="isOpen"
      class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-start justify-center p-4"
      @click.self="$emit('close')"
    >
      <div class="bg-white rounded-xl w-full max-w-lg mt-20 max-h-[80vh] flex flex-col">
        <!-- Header -->
        <div class="p-4 border-b border-[#E0E0E0]">
          <div class="flex items-center gap-3">
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
                class="text-[#333333]"
              >
                <line x1="18" x2="6" y1="6" y2="18"/>
                <line x1="6" x2="18" y1="6" y2="18"/>
              </svg>
            </button>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="제목 또는 작가로 검색"
              class="flex-1 px-4 py-2 bg-[#FAFAFA] rounded-lg border border-[#E0E0E0] focus:outline-none focus:border-[#f4f2e5]"
              autofocus
            />
          </div>
        </div>

        <!-- Results -->
        <div class="flex-1 overflow-y-auto p-4">
          <div v-if="filteredBooks.length === 0" class="text-center py-8">
            <p class="text-[#666666]">검색 결과가 없습니다</p>
          </div>
          <div v-else class="space-y-3">
            <button
              v-for="book in filteredBooks"
              :key="book.id"
              @click="handleBookClick(book)"
              class="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-[#FAFAFA] transition-colors text-left"
            >
              <div class="w-12 h-16 bg-[#f4f2e5] rounded overflow-hidden flex-shrink-0">
                <img
                  :src="book.cover_url"
                  :alt="book.title"
                  class="w-full h-full object-cover"
                />
              </div>
              <div class="flex-1 min-w-0">
                <h3 class="text-[#333333] truncate" style="font-size: 0.875rem">
                  {{ book.title }}
                </h3>
                <p class="text-[#666666] truncate" style="font-size: 0.75rem">
                  {{ book.author }}
                </p>
                <div class="flex items-center gap-2 mt-1">
                  <StarRating :rating="book.rating" :size="12" />
                  <span class="text-[#666666]" style="font-size: 0.75rem">
                    {{ book.rating.toFixed(1) }}
                  </span>
                </div>
              </div>
            </button>
          </div>
        </div>
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
  },
  books: {
    type: Array,
    required: true
  }
});

const emit = defineEmits(['close', 'bookClick']);

const searchQuery = ref('');

const filteredBooks = computed(() => {
  if (!searchQuery.value.trim()) {
    return props.books;
  }
  const query = searchQuery.value.toLowerCase();
  return props.books.filter(
    book =>
      book.title.toLowerCase().includes(query) ||
      book.author.toLowerCase().includes(query)
  );
});

const handleBookClick = (book) => {
  emit('bookClick', book);
  emit('close');
};
</script>