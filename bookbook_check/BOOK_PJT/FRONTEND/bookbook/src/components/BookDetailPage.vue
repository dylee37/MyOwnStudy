<template>
  <div class="min-h-screen bg-background">
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

          <div class="flex flex-col gap-2 mb-4">
            <button 
              @click="toggleDocent" 
              :disabled="isDocentLoading"
              class="flex items-center justify-center gap-2 px-4 py-2 bg-[#333333] text-white rounded-xl active:scale-95 transition-all disabled:opacity-50 w-fit"
            >
              <div v-if="isDocentLoading" class="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full"></div>
              
              <svg v-else xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                <path v-if="isDocentPlaying" d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
                <path v-else d="M8 5.14v13.72l11-6.86L8 5.14z"/>
              </svg>
              
              <span style="font-size: 0.875rem; font-weight: 500;">
                {{ isDocentPlaying ? 'AI 도슨트 가이드' : 'AI 도슨트 가이드' }}
              </span>
            </button>

            <!-- <div v-if="isDocentPlaying" class="flex items-center gap-1 h-4 px-2">
              <div v-for="i in 5" :key="i" class="wave-bar bg-red-500 w-1 rounded-full" :style="`animation-delay: ${i * 0.1}s`"></div>
              <span class="text-[10px] text-red-500 font-bold ml-1 uppercase">Listening...</span>
            </div> -->
            <div v-if="isDocentPlaying" class="siri-container">
              <div class="siri-sphere">
                <div class="inner-wave"></div>
                <div class="inner-wave"></div>
              </div>
              <span class="listening-label">AI 도슨트가 읽어주는 중</span>
            </div>
          </div>

          <div class="flex items-center gap-2 mb-2">
            <StarRating :rating="computedRatingForStars" :size="16" showScore />
          </div>
          <div class="inline-block px-3 py-1 bg-[#f4f2e5] rounded-full">
            <span class="text-[#333333]" style="font-size: 0.75rem">
              {{ book.category_name }}
            </span>
          </div>
        </div>
      </div> <br />

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

        <hr />
        <br />

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
    </div> </div>
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

const store = useStore();

const currentUserId = computed(() => {
  return store.state.userInfo?.id || null;
});

const emit = defineEmits(['back', 'addComment', 'loginClick', 'deleteComment']); 

const handleDeleteComment = (commentId) => {
    emit('deleteComment', commentId);
};

// 이미지 로직 추가
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


const displayComments = computed(() => {
  return props.comments.slice().sort((a, b) => {
    return new Date(a.created_at) - new Date(b.created_at);
  });
});

const computedRating = computed(() => {
  const validComments = props.comments.filter(c => c.rating != null && c.rating > 0);

  if (validComments.length === 0) {
    return 0;
  }

  const sumRating = validComments.reduce((sum, comment) => sum + comment.rating, 0);
  const average5Point = sumRating / validComments.length;
  return average5Point * 2;
});

const computedRatingForStars = computed(() => {
    const validComments = props.comments.filter(c => c.rating != null && c.rating > 0);
    
    if (validComments.length === 0) {
        return 0;
    }
    const sumRating = validComments.reduce((sum, comment) => sum + comment.rating, 0);
    const average10Point = sumRating / validComments.length;

    return average10Point;
});

const displayedAverageScore = computed(() => {
    const average = computedRatingForStars.value; // 9.75
    
    if (average === 0) {
        return 0.0;
    }

    return average.toFixed(1); // 9.75 -> 9.8
});

const computedCommentCount = computed(() => {
  return displayComments.value.length;
});

const isDocentLoading = ref(false);
const isDocentPlaying = ref(false);
let docentAudio = null;

const toggleDocent = async () => {
  // 이미 재생 중이면 정지
  if (isDocentPlaying.value && docentAudio) {
    docentAudio.pause();
    isDocentPlaying.value = false;
    return;
  }

  isDocentLoading.value = true;
  
  try {
    const token = localStorage.getItem('authToken');
    const response = await fetch(`http://127.0.0.1:8000/api/books/${props.book.id}/docent/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${token}`
      },
      body: JSON.stringify({
        voice: store.getters.selectedVoice || 'alloy'
      })
    });

    if (!response.ok) throw new Error("도슨트 데이터를 가져오지 못했습니다.");

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    
    if (docentAudio) docentAudio.pause(); // 이전 오디오 정리
    
    docentAudio = new Audio(url);
    docentAudio.play();
    isDocentPlaying.value = true;

    docentAudio.onended = () => {
      isDocentPlaying.value = false;
      window.URL.revokeObjectURL(url);
    };
  } catch (error) {
    console.error("도슨트 에러:", error);
    alert("도슨트 음성을 생성할 수 없습니다.");
  } finally {
    isDocentLoading.value = false;
  }
};

// 컴포넌트 이탈 시 오디오 정지
import { onUnmounted } from 'vue';
onUnmounted(() => {
  if (docentAudio) {
    docentAudio.pause();
    docentAudio = null;
  }
});
</script>
<style scoped>
.siri-container {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}

.siri-sphere {
  position: relative;
  width: 18px;
  height: 18px;
  background: #333;
  border-radius: 50%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.inner-wave {
  position: absolute;
  width: 150%;
  height: 150%;
  background: linear-gradient(45deg, #ff4d4d, #ff8080, #333);
  border-radius: 40%;
  animation: rotate-siri 3s infinite linear;
  opacity: 0.8;
}

.inner-wave:nth-child(2) {
  animation-duration: 2s;
  opacity: 0.5;
  background: linear-gradient(-45deg, #4d94ff, #80b3ff, #333);
}

.listening-label {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

@keyframes rotate-siri {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>