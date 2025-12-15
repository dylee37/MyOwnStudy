<template>
  <div class="min-h-screen bg-background">
    <!-- Header -->
    <header class="sticky top-0 bg-white border-b border-[#E0E0E0] z-10">
      <div class="max-w-lg mx-auto px-4 py-4">
        <div class="flex items-center">
          <button @click="$emit('back')" class="mr-3">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
              class="text-[#333333]">
              <path d="m15 18-6-6 6-6" />
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
          <img :src="currentCoverUrl" :alt="book.title" class="w-full h-full object-cover" @error="handleImageError" />
        </div>
        <div class="flex-1">
          <h2 class="text-[#333333] mb-2">{{ book.title }}</h2>
          <p class="text-[#666666] mb-3" style="font-size: 0.875rem">
            {{ book.author }}
          </p>
          <div class="flex items-center gap-2 mb-2">
            <StarRating :rating="computedRatingForStars" :size="16" showScore />
          </div>
          <div class="inline-block px-3 py-1 bg-[#f4f2e5] rounded-full">
            <span class="text-[#333333]" style="font-size: 0.75rem">
              {{ book.category_name }}
            </span>
          </div>
        </div>
      </div>

      <br></br>
      <!-- TOKTOK Section -->
      <div class="mb-20">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-[#333333]">
            TOKTOK <span class="text-[#666666]">({{ displayComments.length }})</span>
          </h3>
          <button v-if="isLoggedIn" @click="$emit('addComment')"
            class="px-4 py-2 bg-[#f4f2e5] text-[#333333] rounded-lg hover:bg-[#e8e6d9] transition-colors"
            style="font-size: 0.875rem">
            TOKTOK 작성
          </button>
          <button v-else @click="$emit('loginClick')"
            class="px-4 py-2 bg-[#f4f2e5] text-[#333333] rounded-lg hover:bg-[#e8e6d9] transition-colors"
            style="font-size: 0.875rem">
            로그인하고 작성하기
          </button>
        </div>

        <hr>
        <br>
        <!-- Login Required Message -->
        <div v-if="!isLoggedIn" class="bg-[#F3D8D8] rounded-lg p-4 mb-4">
          <p class="text-[#666666] text-center" style="font-size: 0.875rem">
            TOKTOK을 보려면 로그인이 필요합니다
          </p>
          <button @click="$emit('loginClick')"
            class="w-full mt-3 py-2 bg-white text-[#333333] rounded-lg hover:bg-[#FAFAFA] transition-colors"
            style="font-size: 0.875rem">
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
          <VoiceComment v-for="comment in displayComments" :key="comment.id" :comment="comment"
            :currentUserId="currentUserId" @deleteComment="handleDeleteComment" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import StarRating from './StarRating.vue';
import VoiceComment from './VoiceComment.vue';
import dummy from '../assets/ex_img.jpeg'; //
import { useStore } from 'vuex';

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

// ⭐️⭐️ 수정된 부분: Vuex Store 인스턴스를 가져와 appStore 변수에 할당 ⭐️⭐️
const store = useStore();

// ⭐️⭐️ 수정된 currentUserId computed 속성 ⭐️⭐️
const currentUserId = computed(() => {
  // Vuex Store의 state.userInfo 객체에서 id를 가져오거나, 없으면 null을 반환합니다.
  // userInfo는 객체이므로?. (옵셔널 체이닝)을 사용하여 안전하게 접근합니다.
  // 만약 백엔드가 'pk' 필드를 사용한다면: store.state.userInfo?.pk
  // 현재는 'id' 필드가 있다고 가정합니다.
  return store.state.userInfo?.id || null;
});

const emit = defineEmits(['back', 'addComment', 'loginClick', 'deleteComment']); 

// ⭐️⭐️ 추가 2: VoiceComment에서 받은 이벤트를 App.vue로 전달하는 함수 ⭐️⭐️
const handleDeleteComment = (commentId) => {
    // 댓글 ID를 받아서 상위 컴포넌트(App.vue)로 전달
    emit('deleteComment', commentId);
};

// ⭐️⭐️ 1. 이미지 로직 추가 (BookCard.vue와 동일) ⭐️⭐️
const currentCoverUrl = ref(props.book.cover);
const DEFAULT_COVER = dummy;

const handleImageError = () => {
  if (currentCoverUrl.value !== DEFAULT_COVER) {
    currentCoverUrl.value = DEFAULT_COVER;
  }
};

watch(() => props.book.cover, (newCover) => {
  currentCoverUrl.value = newCover;
}, { immediate: true });
// ⭐️⭐️ -------------------------------------------- ⭐️⭐️


// ⭐️⭐️ 1. displayComments computed 속성 수정 (날짜 기준 정렬 추가) ⭐️⭐️
const displayComments = computed(() => {
  // comments prop을 created_at (ISO String) 기준으로 내림차순 정렬합니다.
  // .slice()를 사용하여 원본 배열을 복사한 후 정렬해야 Vue의 반응성이 깨지지 않습니다.
  return props.comments.slice().sort((a, b) => {
    // ISO string을 Date 객체로 변환하여 비교합니다. (가장 최신 댓글이 위로)
    return new Date(a.created_at) - new Date(b.created_at);
  });
});

const computedRating = computed(() => {
  // 1. TOKTOK 댓글 목록에서 평점(5점 만점)을 가진 댓글만 필터링합니다.
  const validComments = props.comments.filter(c => c.rating != null && c.rating > 0);

  if (validComments.length === 0) {
    // 2. 댓글이 없으면, 평점은 0으로 처리합니다. (알라딘 평점 사용 안 함)
    return 0; // StarRating 컴포넌트가 10점 만점 기준으로 작동하므로 0을 반환합니다.
  }

  // 3. 댓글이 있으면, 댓글 평점(5점 만점)의 평균을 계산합니다.
  const sumRating = validComments.reduce((sum, comment) => sum + comment.rating, 0);
  const average5Point = sumRating / validComments.length;

  // 4. StarRating 컴포넌트가 10점 만점을 기준으로 표시하므로, 2배로 변환하여 전달합니다.
  return average5Point * 2;
});



// ⭐️⭐️ 1. StarRating 컴포넌트에 전달할 평점 (10점 만점, 소수점 유지) ⭐️⭐️
const computedRatingForStars = computed(() => {
    // TOKTOK 댓글 목록에서 평점(10점 만점)을 가진 댓글만 필터링합니다.
    const validComments = props.comments.filter(c => c.rating != null && c.rating > 0);
    
    if (validComments.length === 0) {
        return 0;
    }

    // 10점 만점 평점의 평균을 계산
    const sumRating = validComments.reduce((sum, comment) => sum + comment.rating, 0);
    const average10Point = sumRating / validComments.length;
    
    // StarRating 컴포넌트가 필요로 하는 10점 만점의 정확한 평균값(9.75)을 반환
    return average10Point;
});


// ⭐️⭐️ 2. 표기용 평점 (소수점 둘째 자리에서 반올림, 9.8 표기용) ⭐️⭐️
const displayedAverageScore = computed(() => {
    const average = computedRatingForStars.value; // 9.75
    
    if (average === 0) {
        return 0.0;
    }
    
    // 소수점 둘째 자리에서 반올림하여 첫째 자리까지 표기 (toFixed(1)은 반올림 기능 포함)
    return average.toFixed(1); // 9.75 -> 9.8
});


// ⭐️ 3. 댓글 수 계산 (displayComments.value.length 사용)
const computedCommentCount = computed(() => {
  return displayComments.value.length; // ⭐️ 정의된 computed 속성을 사용
});
</script>