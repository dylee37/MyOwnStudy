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
            isMine ? 'bg-[#f4f2e5] rounded-br-sm' : 'bg-white border border-[#E0E0E0] rounded-bl-sm'
          ]">
            <p class="text-[#333333]" style="font-size: 0.875rem">
              {{ comment.content || (comment.is_voice ? '음성 메시지' : '내용 없음') }}
            </p>
          </div>

        <button 
          @click="readComment(comment.content)"
          class="p-2 transition-colors self-end"
          :class="[
            isMine ? 'mr-1' : 'ml-1',
            comment.is_voice = 'text-[#999999]' 
          ]"
        >
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
import { ref, computed, onMounted } from 'vue';
import StarRating from './StarRating.vue';
import { useStore } from 'vuex';

const props = defineProps({
  comment: {
    type: Object,
    required: true
  },
  currentUserId: {
    type: [Number, String],
    required: false,
    default: null
  }
});

const emit = defineEmits(['deleteComment']); 

const store = useStore();
const currentUserIdFromStore = computed(() => store.getters.currentUser?.id);
const selectedVoice = computed(() => store.getters.selectedVoice);

const isMyComment = computed(() => {
    const currentId = props.currentUserId ? parseInt(props.currentUserId, 10) : null;
    if (currentId && props.comment.user_id === currentId) {
      return true;
    }
    const loggedInId = parseInt(currentUserIdFromStore.value, 10);
    return props.comment.user_id === loggedInId && loggedInId > 0;
});

const handleDeleteClick = () => {
    if (confirm('정말로 이 댓글을 삭제하시겠습니까?')) {
        emit('deleteComment', props.comment.id);
    }
};

const isMine = computed(() => isMyComment.value); 

const synth = window.speechSynthesis;
const isTTSPlaying = ref(false);
let audioPlayer = null;
const koreanVoices = ref([]);

const loadVoices = () => {
  const voices = synth.getVoices();
  koreanVoices.value = voices.filter(voice => voice.lang.startsWith('ko'));
};

onMounted(() => {
  loadVoices();
  if (synth.onvoiceschanged !== undefined) {
    synth.onvoiceschanged = loadVoices;
  }
});

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
const readComment = async (text) => {
  if (isTTSPlaying.value && audioPlayer) {
    audioPlayer.pause();
    isTTSPlaying.value = false;
    return;
  }
  try {
    isTTSPlaying.value = true;
    // 백엔드 API 호출
    const response = await fetch('http://localhost:8000/api/books/tts/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // 필요한 경우 인증 토큰 추가
        //'Authorization': `Bearer ${store.state.accessToken}` 
      },
      body: JSON.stringify({
        text: text,
        voice: props.comment.voice_choice || 'voice1' // props에서 직접 음성 정보 사용
      })
    });

    if (!response.ok) throw new Error("TTS 생성 실패");

    // 바이너리 데이터를 Blob으로 변환
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    
    // 오디오 재생
    audioPlayer = new Audio(url);
    audioPlayer.play();
    
    audioPlayer.onended = () => {
      isTTSPlaying.value = false;
      window.URL.revokeObjectURL(url); // 메모리 해제
    };

  } catch (error) {
    console.error("TTS 에러:", error);
    alert("음성 생성 중 오류가 발생했습니다.");
    isTTSPlaying.value = false;
  }
};
import { onUnmounted } from 'vue';
onUnmounted(() => {
  if (synth.speaking) {
    synth.cancel();
  }
});
</script>