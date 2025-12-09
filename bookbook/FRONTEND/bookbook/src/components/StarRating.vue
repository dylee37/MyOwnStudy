<template>
  <div class="flex items-center gap-1">
    <div class="flex items-center gap-0.5">
      <div
        v-for="(_, index) in 5"
        :key="index"
        class="relative"
        :class="{ 'cursor-pointer': onRatingChange }"
        :style="{ width: `${size}px`, height: `${size}px` }"
      >
        <!-- Background star -->
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

        <!-- Filled star (full or half) -->
        <div
          v-if="isFilled(index) || isHalf(index)"
          class="absolute top-0 left-0 overflow-hidden pointer-events-none"
          :style="{ width: isHalf(index) ? `${size / 2}px` : `${size}px` }"
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

        <!-- Clickable areas for half star support -->
        <template v-if="onRatingChange">
          <div
            class="absolute top-0 left-0 w-1/2 h-full z-10"
            @click.stop="handleStarClick(index, true)"
          />
          <div
            class="absolute top-0 right-0 w-1/2 h-full z-10"
            @click.stop="handleStarClick(index, false)"
          />
        </template>
      </div>
    </div>
    <span
      v-if="showScore"
      class="text-[#666666] ml-1"
      :style="{ fontSize: `${size * 0.875}px` }"
    >
      {{ rating.toFixed(1) }}
    </span>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  rating: {
    type: Number,
    required: true
  },
  size: {
    type: Number,
    default: 16
  },
  showScore: {
    type: Boolean,
    default: false
  },
  onRatingChange: {
    type: Function,
    default: null
  }
});

const normalizedRating = computed(() => props.rating / 2);
const fullStars = computed(() => Math.floor(normalizedRating.value));

const isFilled = (index) => index < fullStars.value;
const isHalf = (index) => index === fullStars.value && (normalizedRating.value % 1) >= 0.5;

const handleStarClick = (index, isHalfClick) => {
  if (props.onRatingChange) {
    const starValue = isHalfClick ? (index + 0.5) * 2 : (index + 1) * 2;
    props.onRatingChange(starValue);
  }
};
</script>