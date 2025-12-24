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
        <div v-if="!isEditing">
          <StarRating :rating="comment.rating" :size="12" />
        </div>
        <div v-else class="flex items-center gap-1">
          <button 
            v-for="star in 5" :key="star" 
            @click="editRating = star"
            class="focus:outline-none"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" 
              :fill="star <= editRating ? '#FFD700' : 'none'" 
              stroke="#FFD700" stroke-width="2" viewBox="0 0 24 24">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
            </svg>
          </button>
          <span class="text-[10px] text-[#999999] ml-1">{{ editRating }}점</span>
        </div>
      </div>

      <div class="flex items-end" :class="{ 'flex-row-reverse': isMine }">
        <div v-if="!isEditing" :class="['rounded-2xl px-4 py-3 max-w-xs', isMine ? 'bg-[#f4f2e5] rounded-br-sm' : 'bg-white border border-[#E0E0E0] rounded-bl-sm']">
            <p class="text-[#333333]" style="font-size: 0.875rem">
              {{ comment.content || (comment.is_voice ? '음성 메시지' : '내용 없음') }}
            </p>
          </div>
        
        <div v-else class="max-w-xs w-full">
          <textarea 
            v-model="editText"
            class="w-full p-3 text-sm border border-[#e8e6d9] rounded-xl focus:outline-none bg-white"
            rows="2"
          ></textarea>
          <div class="flex gap-2 mt-1" :class="isMine ? 'justify-end' : 'justify-start'">
            <button @click="handleUpdate" class="text-[10px] text-blue-500 font-bold">저장</button>
            <button @click="isEditing = false" class="text-[10px] text-gray-400">취소</button>
          </div>
        </div>

        <button 
          v-if="!isEditing"
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
        
        <div v-if="isMyComment && !isEditing" class="flex gap-2">
          <button @click="startEdit" class="text-xs text-blue-500">수정</button> <button @click="handleDeleteClick" class="text-xs text-red-500">삭제</button>
        </div>
        
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

const emit = defineEmits(['deleteComment', 'updateComment']); 

const store = useStore();
const currentUserIdFromStore = computed(() => store.getters.currentUser?.id);
const selectedVoice = computed(() => store.getters.selectedVoice);

const isEditing = ref(false);
const editText = ref('');
const editRating = ref(0);

const startEdit = () => {
  editText.value = props.comment.content;
  editRating.value = props.comment.rating;
  isEditing.value = true;
};

const handleUpdate = () => {
  if (!editText.value.trim()) return;
  // 부모 컴포넌트로 데이터 전달
  emit('updateComment', { id: props.comment.id, content: editText.value, rating: editRating.value });
  isEditing.value = false;
};

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