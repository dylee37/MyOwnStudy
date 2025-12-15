<template>
  <div class="fixed inset-0 bg-background z-50">
    <!-- Header -->
    <header class="sticky top-0 bg-white border-b border-[#E0E0E0]">
      <div class="max-w-lg mx-auto px-4 py-4">
        <div class="flex items-center">
          <button @click="$emit('back')" class="mr-3">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="m15 18-6-6 6-6" />
            </svg>
          </button>
          <h1 class="text-[#333333]">마이페이지</h1>
        </div>
      </div>
    </header>

    <!-- Content -->
    <main class="max-w-lg mx-auto px-4 py-6">
      <!-- Nickname Section -->
      <div class="bg-white rounded-xl p-4 border border-[#E0E0E0] mb-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3 flex-1">
            <div
              class="w-10 h-10 rounded-full bg-[#f4f2e5] flex items-center justify-center"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
                <circle cx="12" cy="7" r="4" />
              </svg>
            </div>
            <input
              v-if="isEditingName"
              v-model="newName"
              type="text"
              class="flex-1 px-3 py-2 bg-[#FAFAFA] rounded-lg border border-[#E0E0E0] focus:outline-none focus:border-[#f4f2e5]"
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
            <div
              class="w-10 h-10 rounded-full bg-[#f4f2e5] flex items-center justify-center"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path
                  d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"
                />
                <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                <line x1="12" x2="12" y1="19" y2="22" />
              </svg>
            </div>
            <span class="text-[#333333]">내 목소리 (TTS)</span>
          </div>
          <span class="text-[#666666]" style="font-size: 0.875rem">
            {{ selectedVoice }}
          </span>
        </button>

        <div v-if="showVoiceSettings" class="mt-4 space-y-2">
          <button
            v-for="voice in voiceOptions"
            :key="voice.id"
            @click="handleVoiceChange(voice.name)"
            :class="[
              'w-full p-3 rounded-lg border transition-colors text-left',
              selectedVoice === voice.name
                ? 'border-[#f4f2e5] bg-[#f4f2e5]'
                : 'border-[#E0E0E0] bg-white hover:bg-[#FAFAFA]',
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
                v-if="selectedVoice === voice.name"
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
        <div
          class="w-10 h-10 rounded-full bg-[#f4f2e5] flex items-center justify-center"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
            <polyline points="16 17 21 12 16 7" />
            <line x1="21" x2="9" y1="12" y2="12" />
          </svg>
        </div>
        <span class="text-[#333333]">로그아웃</span>
      </button>

      <!-- Delete Account Button -->
      <button
        @click="showDeleteConfirm = true"
        class="w-full bg-white rounded-xl p-4 border border-[#E0E0E0] flex items-center gap-3 hover:bg-[#FAFAFA] transition-colors"
      >
        <div
          class="w-10 h-10 rounded-full bg-[#F3D8D8] flex items-center justify-center"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="text-[#666666]"
          >
            <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
            <circle cx="9" cy="7" r="4" />
            <line x1="17" x2="22" y1="8" y2="13" />
            <line x1="22" x2="17" y1="8" y2="13" />
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
</template>

<script setup>
import { ref, nextTick, watch } from "vue";

const props = defineProps({
  userName: {
    type: String,
    required: true,
  },
  profileData: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits(["back", "logout", "deleteAccount", "updateProfile"]);

const selectedVoice = ref(props.profileData?.selected_voice || "여성1");
const showVoiceSettings = ref(false);
const isEditingName = ref(false);
const newName = ref(props.userName);
const showDeleteConfirm = ref(false);
const nameInput = ref(null);

watch(
  () => props.profileData,
  (newProfile) => {
    if (newProfile && newProfile.selected_voice) {
      selectedVoice.value = newProfile.selected_voice;
      newName.value = newProfile.nickname || props.userName;
    }
  },
  { immediate: true }
);

const voiceOptions = [
  { id: "female1", name: "여성1", description: "밝고 명랑한 톤" },
  { id: "female2", name: "여성2", description: "차분하고 부드러운 톤" },
  { id: "male1", name: "남성1", description: "깊고 안정적인 톤" },
  { id: "male2", name: "남성2", description: "경쾌하고 활기찬 톤" },
];

const handleVoiceChange = (voiceName) => {
  selectedVoice.value = voiceName;
  alert(`음성이 "${voiceName}"(으)로 변경되었습니다.`);
};

const startEdit = () => {
  isEditingName.value = true;
  nextTick(() => {
    nameInput.value?.focus();
  });
};

const cancelEdit = () => {
  newName.value = props.userName;
  isEditingName.value = false;
};

// const handleNameUpdate = () => {
//   if (newName.value.trim() && newName.value !== props.userName) {
//     emit('updateProfile', newName.value.trim());
//     isEditingName.value = false;
//     alert('닉네임이 변경되었습니다.');
//   } else {
//     isEditingName.value = false;
//   }
// };

const handleNameUpdate = async () => {
  if (newName.value.trim() && newName.value !== props.userName) {
    const success = await emit("updateProfile", newName.value.trim());

    if (success !== false) {
      isEditingName.value = false;
      alert("닉네임이 변경되었습니다.");
    } else {
      isEditingName.value = false;
    }
  } else {
    isEditingName.value = false;
  }
};

const handleDeleteAccount = () => {
  showDeleteConfirm.value = false;
  emit("deleteAccount");
};
</script>
