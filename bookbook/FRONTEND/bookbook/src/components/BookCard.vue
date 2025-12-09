<template>
  <div
    @click="$emit('click', book)"
    class="bg-white rounded-lg overflow-hidden cursor-pointer hover:shadow-md transition-shadow border border-[#E0E0E0]"
  >
    <div class="aspect-[3/4] bg-[#f4f2e5] relative overflow-hidden">
      <img
        :src="book.cover_url"
        :alt="book.title"
        class="w-full h-full object-cover"
        @error="handleImageError"
      />
    </div>
    <div class="p-3">
      <h3 class="text-[#333333] mb-1 line-clamp-2" style="font-size: 0.875rem">
        {{ book.title }}
      </h3>
      <p class="text-[#666666] mb-2" style="font-size: 0.75rem">
        {{ book.author }}
      </p>
      <div class="flex items-center justify-between">
        <StarRating :rating="book.rating" :size="14" />
        <div class="flex items-center gap-1">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="text-[#666666]"
          >
            <path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/>
          </svg>
          <span class="text-[#666666]" style="font-size: 0.75rem">
            {{ book.commentCount }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import StarRating from './StarRating.vue';

defineProps({
  book: {
    type: Object,
    required: true
  }
});

defineEmits(['click']);

const handleImageError = (e) => {
  e.target.src = 'https://images.unsplash.com/photo-1723220217551-5b5a8a578758?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=400';
};
</script>