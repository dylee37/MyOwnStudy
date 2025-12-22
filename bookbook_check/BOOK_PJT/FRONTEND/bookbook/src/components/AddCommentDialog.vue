<template>
  <Teleport to="body">
    <div v-if="isOpen" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-end sm:items-center justify-center"
      @click.self="$emit('close')">
      <div class="bg-white rounded-t-3xl sm:rounded-3xl w-full max-w-lg p-6 max-h-[90vh] overflow-y-auto">
        <!-- Header -->
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-[#333333]">TOKTOK 작성</h2>
          <button @click="$emit('close')" class="p-1">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
              class="text-[#666666]">
              <line x1="18" x2="6" y1="6" y2="18" />
              <line x1="6" x2="18" y1="6" y2="18" />
            </svg>
          </button>
        </div>

        <!-- Type Selection -->
        <div class="flex gap-2 mb-6">
          <button @click="commentType = 'text'" :class="[
            'flex-1 py-3 rounded-lg transition-colors',
            commentType === 'text'
              ? 'bg-[#f4f2e5] text-[#333333]'
              : 'bg-white text-[#666666] border border-[#E0E0E0]'
          ]">
            텍스트
          </button>
          <button @click="commentType = 'voice'" :class="[
            'flex-1 py-3 rounded-lg transition-colors',
            commentType === 'voice'
              ? 'bg-[#f4f2e5] text-[#333333]'
              : 'bg-white text-[#666666] border border-[#E0E0E0]'
          ]">
            음성
          </button>
        </div>

        <!-- Rating -->
        <div class="mb-6">
          <label class="block text-[#333333] mb-3" style="font-size: 0.875rem">
            평점 ({{ selectedRating.toFixed(0) }}/5)
          </label>
          <div class="flex justify-center">
            <StarRating :rating="selectedRating" :size="32" :onRatingChange="handleRatingChange" />
          </div>
        </div>

        <!-- Text Input -->
        <div v-if="commentType === 'text'" class="mb-6">
          <label class="block text-[#333333] mb-2" style="font-size: 0.875rem">
            댓글 내용
          </label>
          <textarea v-model="commentText" placeholder="책에 대한 생각을 자유롭게 남겨주세요"
            class="w-full px-4 py-3 bg-[#FAFAFA] rounded-lg border border-[#E0E0E0] focus:outline-none focus:border-[#f4f2e5] resize-none"
            rows="5"></textarea>
        </div>

        <!-- Voice Recording -->
        <div v-else class="mb-6">
          <label class="block text-[#333333] mb-3" style="font-size: 0.875rem">
            음성 녹음
          </label>
          <div class="bg-[#FAFAFA] rounded-lg p-6 flex flex-col items-center">
            <button @click="toggleRecording" :class="[
              'w-16 h-16 rounded-full flex items-center justify-center transition-colors mb-3',
              isRecording ? 'bg-red-500 hover:bg-red-600' : 'bg-[#f4f2e5] hover:bg-[#e8e6d9]',
              { 'animate-pulse': isRecording }
            ]">
              <svg v-if="!isRecording" xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24"
                fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                class="text-[#333333]">
                <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
                <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                <line x1="12" x2="12" y1="19" y2="22" />
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="white"
                stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="6" y="4" width="12" height="16" rx="2" />
              </svg>
            </button>

            <p class="text-[#666666]" style="font-size: 0.875rem">
              <span v-if="isRecording" class="text-red-500 font-bold">🎙️ 녹음 중...</span>
              <span v-else-if="sttCompleted" class="text-green-600 font-bold">✅ 인식 완료! (재녹음 가능)</span>
              <span v-else-if="sttError" class="text-red-500 font-bold">❌ 음성 인식 실패</span>
              <span v-else>버튼을 눌러 녹음 시작</span>
            </p>

            <textarea v-model="commentText" placeholder="음성 인식을 시작하거나, 텍스트를 직접 수정하세요." :readonly="isRecording"
              class="w-full mt-4 px-4 py-3 bg-white rounded-lg border border-[#E0E0E0] focus:outline-none focus:border-[#f4f2e5] resize-none"
              rows="3"></textarea>
          </div>
        </div>

        <button @click="handleSubmit"
          :disabled="!canSubmit || isRecording || (commentType === 'voice' && !sttCompleted)"  
          :class="[
            'w-full py-3 rounded-lg transition-colors',
            canSubmit && !isRecording && !(commentType === 'voice' && !sttCompleted) // ⭐️ 활성화 색상 조건 ⭐️
              ? 'bg-[#f4f2e5] text-[#333333] hover:bg-[#e8e6d9]'
              : 'bg-[#E0E0E0] text-[#999999] cursor-not-allowed'
          ]">
          TOKTOK 등록
        </button>
      </div>
    </div>
  </Teleport>
</template>




<script setup>
import { ref, computed } from 'vue';
import { useStore } from 'vuex';
import StarRating from './StarRating.vue';
import axios from 'axios';

const props = defineProps({
    isOpen: {
        type: Boolean,
        required: true
    }
});

const emit = defineEmits(['close', 'submit']);
const store = useStore();

const commentType = ref('text');
const commentText = ref('');
const selectedRating = ref(5);
const isRecording = ref(false);

const sttCompleted = ref(false);
const sttError = ref(false);

// MediaRecorder 관련 refs
const mediaRecorder = ref(null);
const audioChunks = ref([]);

const canSubmit = computed(() => {
  if (commentType.value === 'text') {
    return commentText.value.trim().length > 0 && !isRecording.value;
  }
  if (commentType.value === 'voice') {
    return !isRecording.value && sttCompleted.value && commentText.value.trim().length > 0;
  }
  return false;
});

const handleRatingChange = (rating) => {
  selectedRating.value = rating;
};

const startRecording = async () => {
  if (isRecording.value) return;

  sttCompleted.value = false;
  sttError.value = false;
  commentText.value = '';
  audioChunks.value = [];

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    
    // 1. Recorder 생성
    const recorder = new MediaRecorder(stream);
    mediaRecorder.value = recorder;
    
    // 2. 데이터 수집 이벤트
    recorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.value.push(event.data);
      }
    };

    // 3. ⭐️ 녹음이 실제로 멈췄을 때 실행될 로직 ⭐️
    recorder.onstop = async () => {
      console.log("MediaRecorder가 실제로 멈췄습니다. STT를 시작합니다.");
      await stopRecordingAndProcessSTT();
      
      // 마이크 사용 종료 (브라우저 마이크 아이콘 끄기)
      stream.getTracks().forEach(track => track.stop());
    };

    // 4. 녹음 시작
    recorder.start();
    isRecording.value = true; // 실제 시작 후 상태 변경
    console.log("녹음 시작됨...");
  } catch (error) {
    console.error("마이크 접근 오류:", error);
    sttError.value = true;
    commentText.value = "마이크를 사용할 수 없습니다.";
    isRecording.value = false;
  }
};

const stopRecording = () => {
  if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') {
    console.log("녹음 중지 요청 중...");
    mediaRecorder.value.stop(); 
  } else {
    console.warn("중지할 녹음 프로세스가 없습니다.");
    isRecording.value = false;
  }
};

const toggleRecording = () => {
  console.log("현재 isRecording 상태:", isRecording.value);
  if (!isRecording.value) {
    startRecording();
  } else {
    stopRecording();
  }
};

const stopRecordingAndProcessSTT = async () => {
  // 녹음 종료 시 UI 상태 업데이트
  isRecording.value = false; 

  if (audioChunks.value.length === 0) {
    console.warn("녹음된 데이터가 없습니다.");
    return;
  }

  console.log("STT 서버 전송 시작...");
  const audioBlob = new Blob(audioChunks.value, { type: 'audio/webm' });
  const formData = new FormData();
  formData.append('audio', audioBlob, 'recording.webm');

  try {
    const response = await axios.post('http://127.0.0.1:8000/api/books/transcribe/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    
    commentText.value = response.data.text;
    sttCompleted.value = true;
    sttError.value = false;
    console.log("STT 성공:", response.data.text);
  } catch (error) {
    console.error("STT API 오류:", error);
    sttError.value = true;
    sttCompleted.value = false;
    commentText.value = "음성 인식에 실패했습니다. 다시 시도해주세요.";
  }
};

const handleSubmit = () => {
  if (!canSubmit.value) return;

  if (commentType.value === 'voice' && !sttCompleted.value) {
    alert('음성 녹음을 먼저 완료해주세요.');
    return;
  }

  emit('submit', {
    text: commentText.value,
    isVoice: commentType.value === 'voice',
    rating: selectedRating.value,
    voice_choice: store.getters.selectedVoice
  });

  // Reset
  commentText.value = '';
  selectedRating.value = 5; // Default to 5
  commentType.value = 'text';
  isRecording.value = false;
  sttCompleted.value = false;
  sttError.value = false;
};
</script>