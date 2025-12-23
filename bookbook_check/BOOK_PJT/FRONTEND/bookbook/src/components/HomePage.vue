<template>
  <div class="min-h-screen bg-background pb-20">
    
    <header class="sticky top-0 bg-white border-b border-[#E0E0E0] z-[100]">
      <div class="max-w-lg mx-auto px-4 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-[#333333]" style="font-size: 1.8rem;">BOOKBOOK</h1>
          </div>
          <button @click="$emit('searchClick')" class="p-2 hover:bg-[#FAFAFA] rounded-full transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
              class="text-[#333333]">
              <circle cx="11" cy="11" r="8" />
              <path d="m21 21-4.3-4.3" />
            </svg>
          </button>
        </div>
      </div>
    </header>

    <main class="max-w-lg mx-auto px-4 py-6">
      <div class="mb-6">
        <h2 class="text-[#333333] mb-4" style="font-size: 1.5rem;font-weight: 700">이번 주 베스트셀러</h2>
        <div v-if="isLoading" class="grid grid-cols-2 gap-4">
          <div v-for="i in 4" :key="'skel-best-' + i" class="skeleton-card">
            <div class="skeleton-image"></div>
            <div class="skeleton-text title"></div>
            <div class="skeleton-text author"></div>
          </div>
        </div>
        <div v-else-if="bestsellers.length" class="grid grid-cols-2 gap-4">
          <BookCard v-for="book in bestsellers" :key="book.id" :book="book"
            @click="$emit('bookClick', book)" />
        </div>
        <div v-else class="text-center py-10">
            <p class="text-sm text-gray-400">베스트셀러 목록을 불러오는 중입니다...</p>
        </div>
      </div>

      <div>
        <h2 class="text-[#333333] mb-4" style="font-weight: 700; font-size: 1.5rem;">
          {{ isLoggedIn ? `${currentUser.name}님을 위한 AI 맞춤 추천 도서` : '추천 도서' }}
        </h2>

        <div v-if="isLoading" class="grid grid-cols-2 gap-4">
          <div v-for="i in 2" :key="'skel-rec-' + i" class="skeleton-card">
            <div class="skeleton-image"></div>
            <div class="skeleton-text title"></div>
            <div class="skeleton-text author"></div>
          </div>
        </div>
        
        <div v-else-if="personalizedRecommendations.length" class="grid grid-cols-2 gap-4">
          <BookCard v-for="rec in personalizedRecommendations" :key="rec.book.id" :book="rec.book"
            @click="$emit('bookClick', rec.book)" />
        </div>
        
        <div v-else class="text-center py-10">
          <p class="text-sm text-gray-400">추천 도서를 불러오는 중이거나, 추천할 도서가 없습니다.</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import BookCard from './BookCard.vue';
import { useStore } from 'vuex';
import { ref, computed, onMounted } from 'vue'

defineEmits(['bookClick', 'searchClick']);

// 1. Store 인스턴스 가져오기
const store = useStore();
const isLoading = ref(true);

// 2. Computed 속성 정의 (Getter 및 State 매핑)
const isLoggedIn = computed(() => store.getters.isLoggedIn);
const currentUser = computed(() => store.getters.currentUser || { name: '독자' }); // 기본값 설정
const bestsellers = computed(() => store.state.bestsellers);
const personalizedRecommendations = computed(() => store.state.personalizedRecommendations);

// 3. Life Cycle Hooks에서 Action 호출
const fetchBestsellers = () => store.dispatch('fetchBestsellers');
const fetchPersonalizedRecommendations = () => store.dispatch('fetchPersonalizedRecommendations');

// onMounted(() => {
//   // 베스트셀러와 추천 도서를 모두 로드
//   fetchBestsellers();
//   fetchPersonalizedRecommendations();
// });
onMounted(async () => {
  isLoading.value = true;
  
  const delay = new Promise(resolve => setTimeout(resolve, 1000));
  await Promise.all([
    store.dispatch('fetchBestsellers'),
    store.dispatch('fetchPersonalizedRecommendations'),
    delay
  ]);

  isLoading.value = false;
});
</script>

<style scoped>
.skeleton-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skeleton-image {
  width: 100%;
  aspect-ratio: 2/3;
  background-color: #f0f0f0;
  border-radius: 12px;
}

.skeleton-text {
  background-color: #f0f0f0;
  border-radius: 4px;
}

.skeleton-text.title {
  width: 80%;
  height: 16px;
}

.skeleton-text.author {
  width: 50%;
  height: 14px;
}

.skeleton-image, .skeleton-text {
  position: relative;
  overflow: hidden;
}

.skeleton-image::after, .skeleton-text::after {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0) 0%,
    rgba(255, 255, 255, 0.5) 50%,
    rgba(255, 255, 255, 0) 100%
  );
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}
</style>