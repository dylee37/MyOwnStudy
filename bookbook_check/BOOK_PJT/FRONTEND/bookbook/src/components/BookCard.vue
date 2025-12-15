<template>
  <div @click="$emit('click', book)"
    class="bg-white rounded-lg overflow-hidden cursor-pointer hover:shadow-md transition-shadow border border-[#E0E0E0]">
    <div class="aspect-[3/4] bg-[#f4f2e5] relative overflow-hidden">
      <img :src="book.cover" :alt="book.title" v-if="book.cover" />
      <div v-else>
      </div>
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
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
            class="text-[#666666]">
            <path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z" />
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
import { ref, computed, watch } from 'vue';
import StarRating from './StarRating.vue';
// import dummy from '../assets/ex_img.jpeg'

const props = defineProps({
  book: {
    type: Object,
    required: true
  }
});

defineEmits(['click']);

// // ⭐️ currentCoverUrl 초기화: 백엔드에서 받은 props.book.cover를 사용합니다.
// const currentCoverUrl = ref(props.book.cover);
// // ⭐️ 대체 이미지 URL: 외부 URL 대신 로컬 더미 이미지를 사용합니다. (가장 확실한 방법)
// const DEFAULT_COVER = dummy;


// ⭐️ 에러 핸들러: 이미지가 로드 실패하면 로컬 더미 이미지로 변경합니다.
// const handleImageError = () => {
//   // 이미 기본 이미지라면 무한 루프 방지
//   if (currentCoverUrl.value !== DEFAULT_COVER) {
//     currentCoverUrl.value = DEFAULT_COVER;
//   }
// };

// ⭐️ prop이 변경될 때마다 URL을 초기화합니다.
// watch(() => props.book.cover, (newCover) => {
//   currentCoverUrl.value = newCover;
// }, { immediate: true });


// ⭐️ 별점 계산 로직 (0으로 기본값 설정) ⭐️
// ⭐️⭐️ computedRating 수정: 오직 사용자 TOKTOK 평균 평점만 반영 ⭐️⭐️
const computedRating = computed(() => {
    // 1. TOKTOK 사용자 평균 평점 필드(예: user_average_rating)를 사용합니다.
    // 이 필드는 10점 만점 기준으로 백엔드에서 계산되어 온다고 가정합니다.
    const userRating = props.book.rating; 
    
    // 2. 평점 값이 null 또는 undefined가 아니라면 해당 값을 사용합니다.
    if (userRating != null) {
        return userRating;
    }

    // 3. 사용자 평균 평점 데이터가 없다면 0으로 처리합니다. (알라딘 평점 사용 안 함)
    return 0;
});

// ⭐️ 댓글 수 계산 로직 (0으로 기본값 설정) ⭐️
const computedCommentCount = computed(() => {
  // book.comment_count가 있으면 사용하고, 없으면 book.comments 배열의 길이를 사용합니다.
  // 두 필드 모두 없으면 최종적으로 0을 반환합니다.
  return props.book.comment_count || (props.book.comments ? props.book.comments.length : 0);
});
</script>