<template>
  <div class="fixed inset-0 bg-background z-50">
    <!-- Header -->
    <header class="sticky top-0 bg-white border-b border-[#E0E0E0]">
      <div class="max-w-lg mx-auto px-4 py-4">
        <div class="flex items-center">
          <button @click="$emit('back')" class="mr-3">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="m15 18-6-6 6-6"/>
            </svg>
          </button>
          <h1 class="text-[#333333]" style="font-size: 1.2rem; font-weight: bold;">내 정보</h1>
        </div>
      </div>
    </header>

    <!-- Content -->
    <main class="max-w-lg mx-auto px-4 py-6">
      <!-- Nickname Section -->
      <div class="bg-white rounded-xl p-4 border border-[#E0E0E0] mb-4">
        <div class="flex items-center justify-bet+ween">
          <div class="flex items-center gap-3 flex-1">
            <div class="w-10 h-10 rounded-full bg-[#f4f2e5] flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
            </div>
            <input
              v-if="isEditingName"
              v-model="newName"
              type="text"
              class="flex-1 px-3 py-2 bg-[#FAFAFA] rounded-lg border border-[#E0E0E0] focus:outline-none focus:border-[#f4f2e5] mr-3"
              ref="nameInput"
            />
            <span v-else class="text-[#333333]">{{ userName }}</span>
          </div>
          
          <div v-if="isEditingName" class="flex gap-2">
            <button
              @click="handleNameUpdate"
              class="px-4 py-2 bg-[#f4f2e5] text-[#333333] rounded-lg hover:bg-[#e8e6d9] transition-colors"
              style="font-size: 0.875rem"
            >
              저장
            </button>
            <button
              @click="cancelEdit"
              class="px-4 py-2 bg-white text-[#666666] rounded-lg border border-[#E0E0E0] hover:bg-[#FAFAFA] transition-colors"
              style="font-size: 0.875rem"
            >
              취소
            </button>
          </div>
          <button
            v-else
            @click="startEdit"
            class="px-4 py-2 text-[#666666] hover:text-[#333333] transition-colors"
            style="font-size: 0.875rem"
          >
            수정
          </button>
        </div>
      </div>

      <!-- Voice Settings -->
      <div class="bg-white rounded-xl p-4 border border-[#E0E0E0] mb-4">
        <button
          @click="showVoiceSettings = !showVoiceSettings"
          class="w-full flex items-center justify-between py-2"
        >
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-[#f4f2e5] flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                <line x1="12" x2="12" y1="19" y2="22"/>
              </svg>
            </div>
            <span class="text-[#333333]">내 목소리 (TTS)</span>
          </div>
          <span class="text-[#666666]" style="font-size: 0.875rem">
            {{ selectedVoiceName }}
          </span>
        </button>

        <div v-if="showVoiceSettings" class="mt-4 space-y-2">
          <button
            v-for="voice in voiceOptions"
            :key="voice.id"
            @click="handleVoiceChange(voice.id)"
            :class="[
              'w-full p-3 rounded-lg border transition-colors text-left',
              selectedVoice === voice.id
                ? 'border-[#f4f2e5] bg-[#f4f2e5]'
                : 'border-[#E0E0E0] bg-white hover:bg-[#FAFAFA]'
            ]"
          >
            <div class="flex items-center justify-between">
              <div>
                <div class="text-[#333333]">{{ voice.name }}</div>
                <div class="text-[#666666]" style="font-size: 0.75rem">
                  {{ voice.description }}
                </div>
              </div>
              <div
                v-if="selectedVoice === voice.id"
                class="w-5 h-5 rounded-full bg-[#333333] flex items-center justify-center"
              >
                <div class="w-2 h-2 rounded-full bg-white" />
              </div>
            </div>
          </button>
        </div>
      </div>

      <!-- Logout Button -->
      <button
        @click="$emit('logout')"
        class="w-full bg-white rounded-xl p-4 border border-[#E0E0E0] mb-4 flex items-center gap-3 hover:bg-[#FAFAFA] transition-colors"
      >
        <div class="w-10 h-10 rounded-full bg-[#f4f2e5] flex items-center justify-center">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
            <polyline points="16 17 21 12 16 7"/>
            <line x1="21" x2="9" y1="12" y2="12"/>
          </svg>
        </div>
        <span class="text-[#333333]">로그아웃</span>
      </button>

      <!-- Delete Account Button -->
      <button
        @click="showDeleteConfirm = true"
        class="w-full bg-white rounded-xl p-4 border border-[#E0E0E0] flex items-center gap-3 hover:bg-[#FAFAFA] transition-colors"
      >
        <div class="w-10 h-10 rounded-full bg-[#F3D8D8] flex items-center justify-center">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-[#666666]">
            <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
            <line x1="17" x2="22" y1="8" y2="13"/>
            <line x1="22" x2="17" y1="8" y2="13"/>
          </svg>
        </div>
        <span class="text-[#666666]">회원 탈퇴</span>
      </button>

      <!-- Delete Confirmation Dialog -->
      <div
        v-if="showDeleteConfirm"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      >
        <div class="bg-white rounded-xl p-6 max-w-sm w-full">
          <h2 class="text-[#333333] mb-2">회원 탈퇴</h2>
          <p class="text-[#666666] mb-6" style="font-size: 0.875rem">
            정말로 탈퇴하시겠습니까?<br />
            모든 데이터가 삭제되며 복구할 수 없습니다.
          </p>
          <div class="flex gap-2">
            <button
              @click="showDeleteConfirm = false"
              class="flex-1 py-3 bg-white text-[#666666] rounded-lg border border-[#E0E0E0] hover:bg-[#FAFAFA] transition-colors"
            >
              취소
            </button>
            <button
              @click="handleDeleteAccount"
              class="flex-1 py-3 bg-[#F3D8D8] text-[#666666] rounded-lg hover:bg-[#f0c9c9] transition-colors"
            >
              탈퇴하기
            </button>
          </div>
        </div>
      </div>
    </main>
  </div>

  <div class="toast-container">
    <Transition name="toast">
      <div v-if="toast.show" class="toast-content">
        <span class="message">{{ toast.message }}</span>
      </div>
    </Transition>
  </div>
</template>


<script setup>
import { ref, nextTick, watch, computed, reactive, provide } from 'vue';
import { useStore } from 'vuex';

const props = defineProps({
  userName: {
    type: String,
    required: true
  },
  profileData: {
    type: Object,
    default: null,
  },
});

const toast = reactive({
  show: false,
  message: ''
});

const showToast = (msg) => {
  toast.message = msg;
  toast.show = true;
  
  setTimeout(() => {
    toast.show = false;
  }, 2500);
};

provide('showToast', showToast);

const emit = defineEmits(['back', 'logout', 'deleteAccount', 'updateProfile']);

const store = useStore();
const selectedVoice = computed(() => store.getters.selectedVoice);

const showVoiceSettings = ref(false);
const isEditingName = ref(false);
const newName = ref(props.userName);
const showDeleteConfirm = ref(false);
const nameInput = ref(null);

watch(
  () => props.profileData,
  (newProfile) => {
    if (newProfile && newProfile.nickname) {
      newName.value = newProfile.nickname;
    }
  },
  { immediate: true, deep: true }
);

const voiceOptions = [
  { id: 'voice1', name: '목소리 1 (여성, 차분한)' },
  { id: 'voice2', name: '목소리 2 (남성, 활기찬)' },
  { id: 'voice3', name: '목소리 3 (여성, 밝은)' },
  { id: 'voice4', name: '목소리 4 (남성, 따뜻한)' },
];

const selectedVoiceName = computed(() => {
  const voice = voiceOptions.find(v => v.id === selectedVoice.value);
  return voice ? voice.name : '';
});

const handleVoiceChange = (voiceId) => {
  if (voiceId !== selectedVoice.value) {
    // 1. API 업데이트를 위해 부모에게 이벤트 전달
    emit("updateProfile", { selected_voice: voiceId });
    // 2. UI 즉각적인 반응을 위해 스토어 상태 변경
    store.commit('SET_SELECTED_VOICE', voiceId);
  }
  showVoiceSettings.value = false;
};

const startEdit = () => {
  isEditingName.value = true;
  nextTick(() => {
    nameInput.value?.focus();
  });
};

const cancelEdit = () => {
  if (props.profileData) {
    newName.value = props.profileData.nickname || props.userName;
  } else {
    newName.value = props.userName;
  }
  isEditingName.value = false;
};

const handleNameUpdate = async () => {
  if (newName.value.trim() && newName.value !== props.userName) {
    const success = await emit("updateProfile", { nickname: newName.value.trim() });
    if (success !== false) {
      isEditingName.value = false;
      showToast("닉네임이 변경되었습니다.");
    }
  } else {
    isEditingName.value = false;
  }
};

const handleDeleteAccount = () => {
  showDeleteConfirm.value = false;
  emit('deleteAccount');
};
</script>

<style scoped>
.toast-container {
  position: fixed;
  bottom: 100px;
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  z-index: 9999;
  pointer-events: none;
}
.toast-content {
  background-color: rgba(51, 51, 51, 0.9);
  color: #ffffff;
  padding: 12px 24px;
  border-radius: 50px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
  pointer-events: auto;
}
.toast-enter-active, .toast-leave-active {
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.toast-enter-from, .toast-leave-to {
  opacity: 0;
  transform: translateY(20px);
}
</style>