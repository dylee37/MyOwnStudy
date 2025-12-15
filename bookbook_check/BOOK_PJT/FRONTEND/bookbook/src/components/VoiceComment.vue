<template>
  <div :class="[
    'flex gap-3 mb-4',
    isMine ? 'flex-row-reverse' : 'flex-row'
  ]">
    <div class="w-10 h-10 rounded-full bg-[#f4f2e5] flex items-center justify-center flex-shrink-0">
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none"
        stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-[#333333]">
        <path d="M19 21v-2a4 4 4 0 0-4-4H9a4 4 4 0 0-4 4v2" />
        <circle cx="12" cy="7" r="4" />
      </svg>
    </div>

    <div :class="['flex-1', isMine ? 'items-end' : 'items-start', 'flex flex-col']">

      <div class="flex flex-col gap-1 mb-1" :class="{ 'items-end': isMine }">
        <span class="text-[#333333] font-semibold" style="font-size: 0.875rem">
          {{ comment.user_name }}
        </span>
        <StarRating :rating="comment.rating" :size="12" />
      </div>

      <div class="flex items-end" :class="{ 'flex-row-reverse': isMine }">

        <div :class="[
          'rounded-2xl px-4 py-3 max-w-xs',
          isMine
            ? 'bg-[#f4f2e5] rounded-br-sm'
            : 'bg-white border border-[#E0E0E0] rounded-bl-sm'
        ]">

          <p class="text-[#333333]" style="font-size: 0.875rem" v-if="comment.content">
            {{ comment.content }}
          </p>

          <div v-if="comment.is_voice" class="mt-2 flex items-center gap-2">
            <button class="p-2 text-white bg-red-500 rounded-full hover:bg-red-600 transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M3 22L21 12L3 2V22Z" />
              </svg>
            </button>
            <span class="text-sm text-[#666666]">
              음성 댓글 ({{ comment.text ? 'STT 변환 텍스트 포함' : '음성만' }})
            </span>
          </div>
        </div>

        <button v-if="comment.content && !comment.is_voice"
          @click="readComment(comment.content, comment.user_voice || 'voice1')"
          class="p-2 text-[#999999] hover:text-[#333333] transition-colors self-end" :class="isMine ? 'mr-1' : 'ml-1'">

          <svg v-if="!isTTSPlaying" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
            fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M11 5L6 9H2v6h4l5 4z" />
            <path d="M15.54 8.46a4.997 4.997 0 0 1 0 7.07" />
          </svg>

          <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor"
            stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="6" y="6" width="12" height="12" rx="2" ry="2"></rect>
          </svg>
        </button>
      </div>

      <div class="flex items-center gap-3 mt-1" :class="isMine ? 'flex-row-reverse justify-start' : 'flex-row justify-start'">
        
        <button v-if="isMyComment" 
          @click="handleDeleteClick"
          class="text-xs text-red-500 hover:text-red-700 transition-colors"
        >
          삭제
        </button>
        
        <span class="text-[#999999]" style="font-size: 0.75rem">
          {{ formatTime(comment.created_at) }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import StarRating from './StarRating.vue';
import { useStore } from 'vuex'

const props = defineProps({
  comment: {
    type: Object,
    required: true
  },
  // ⭐️ [핵심 수정] app.vue에서 전달받는 현재 사용자 ID
  currentUserId: {
    type: [Number, String],
    required: false,
    default: null
  }
});

// emits 정의 (삭제 이벤트)
const emit = defineEmits(['deleteComment']); 

const store = useStore();
// Vuex store에서 사용자 ID 가져오기 (prop이 없을 경우 대비)
const currentUserIdFromStore = computed(() => store.state.user?.id || store.state.user?.userData?.id);


// ⭐️⭐️ [핵심 수정] isMyComment 구현: 현재 로그인 사용자의 댓글인지 확인 ⭐️⭐️
const isMyComment = computed(() => {
    // 1. prop으로 받은 ID 사용 (app.vue에서 userData.id가 전달되는 경우)
    const currentId = props.currentUserId ? parseInt(props.currentUserId, 10) : null;
    if (currentId && props.comment.user_id === currentId) {
      return true;
    }
    
    // 2. prop이 없을 경우 store의 ID 사용 (fallback)
    const loggedInId = parseInt(currentUserIdFromStore.value, 10);
    return props.comment.user_id === loggedInId && loggedInId > 0;
});

// ⭐️⭐️ [핵심 수정] 삭제 버튼 클릭 핸들러: 상위 컴포넌트에 이벤트 발생 ⭐️⭐️
const handleDeleteClick = () => {
    if (confirm('정말로 이 댓글을 삭제하시겠습니까?')) {
        // 댓글 ID를 전달하여 상위 컴포넌트에 삭제를 요청합니다.
        emit('deleteComment', props.comment.id);
    }
};

// 댓글 위치 결정 (기존 로직 유지)
const isMine = computed(() => isMyComment.value); 

// TTS 관련 상태 및 객체
const synth = window.speechSynthesis;
const isTTSPlaying = ref(false);


// 시간 포맷팅 함수 (props.comment.created_at을 사용)
const formatTime = (isoString) => {
  if (!isoString) return '';
  const date = new Date(isoString);
  const now = new Date();

  const getDateKey = (d) => d.toISOString().substring(0, 10);

  if (getDateKey(date) === getDateKey(now)) {
    return date.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', hour12: false });
  } else {
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${month}.${day}`;
  }
};


// TTS 기능 구현 함수 
const readComment = (text, voiceOption) => {
  if (!synth) {
    alert("죄송합니다. 이 브라우저는 음성 합성 기능을 지원하지 않습니다.");
    return;
  }

  if (synth.speaking && isTTSPlaying.value) {
    synth.cancel();
    isTTSPlaying.value = false;
    return;
  }

  synth.cancel();

  const utterance = new SpeechSynthesisUtterance(text);
  isTTSPlaying.value = true;

  utterance.onend = () => {
    isTTSPlaying.value = false;
  };
  utterance.onpause = () => {
    isTTSPlaying.value = false;
  };
  utterance.onerror = () => {
    isTTSPlaying.value = false;
    console.error("TTS 재생 오류 발생");
  };

  const voices = synth.getVoices();
  let selectedVoice = voices.find(voice => voice.lang.startsWith('ko'));
  if (selectedVoice) {
    utterance.voice = selectedVoice;
  }
  utterance.rate = 1.0;
  utterance.pitch = 1.0;

  synth.speak(utterance);
};
</script>