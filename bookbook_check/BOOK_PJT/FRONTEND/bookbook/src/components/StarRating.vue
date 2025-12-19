<template>
  <div class="flex items-center gap-1">
    <div class="flex items-center gap-0.5">
      <div
        v-for="i in 5"
        :key="i"
        class="relative"
        :class="{ 'cursor-pointer': onRatingChange }"
        :style="{ width: `${size}px`, height: `${size}px` }"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          :width="size"
          :height="size"
          viewBox="0 0 24 24"
          fill="#E0E0E0"
          stroke="#E0E0E0"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
        </svg>

        <div 
          v-if="i <= Math.round(props.rating)"
          class="absolute top-0 left-0 overflow-hidden pointer-events-none"
          :style="{ width: `${size}px` }"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            :width="size"
            :height="size"
            viewBox="0 0 24 24"
            fill="#FFB800"
            stroke="#FFB800"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
          </svg>
        </div>

        <template v-if="onRatingChange">
          <div
            class="absolute inset-0 z-10"
            @click.stop="handleStarClick(i)"
          />
        </template>
      </div>
    </div>
    <span
      v-if="showScore"
      class="text-[#666666] ml-1"
      :style="{ fontSize: `${size * 0.875}px` }"
    >
      {{ Math.round(rating).toFixed(0) }}
    </span>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  rating: { //5점 만점 정수 값(1~5) 또는 소수점 값(평균)
    type: Number,
    required: true
  },
  size: { type: Number, default: 16 },
  showScore: { type: Boolean, default: false },
  onRatingChange: { type: Function, default: null }
});

// 5점 만점 평점 전달
const handleStarClick = (index) => {
  if (props.onRatingChange) {
    // index는 1부터 5까지의 값
    props.onRatingChange(index);
  }
};
</script>