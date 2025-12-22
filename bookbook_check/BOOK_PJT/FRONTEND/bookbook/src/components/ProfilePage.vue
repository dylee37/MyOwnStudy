<template>
  <div class="min-h-screen bg-background pb-20">
    <header class="sticky top-0 bg-white border-b border-[#E0E0E0] z-10">
      <div class="max-w-lg mx-auto px-4 py-4">
        <div class="flex items-center justify-between">
          <h1 class="text-[#333333]" style="font-size: 1.8rem; font-weight: bold;">내 기록</h1>
          <button v-if="isLoggedIn" @click="$emit('myPageClick')" class="p-2 hover:bg-[#FAFAFA] rounded-full transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-[#333333]">
              <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/>
              <circle cx="12" cy="12" r="3"/>
            </svg>
          </button>
        </div>
      </div>
    </header>

    <div v-if="!isLoggedIn" class="flex flex-col items-center justify-center px-6 py-20">
      <div class="w-20 h-20 rounded-full bg-[#f4f2e5] flex items-center justify-center mb-6">
        <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-[#333333]">
          <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/>
          <circle cx="12" cy="7" r="4"/>
        </svg>
      </div>
      <p class="text-[#333333] mb-6 text-center">로그인을 해주세요</p>
      <button @click="$emit('loginClick')" class="px-8 py-3 bg-[#f4f2e5] text-[#333333] rounded-lg hover:bg-[#e8e6d9] transition-colors">
        로그인
      </button>
    </div>

    <main v-else class="max-w-lg mx-auto px-4 py-6">
      <div class="flex flex-col items-center mb-8">
        <div class="w-20 h-20 rounded-full bg-[#f4f2e5] flex items-center justify-center mb-3">
          <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-[#333333]">
            <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
        </div>
        <h2 class="text-[#333333] mb-1 font-bold text-lg">{{ userName }}</h2>
        
        <div class="w-full text-center px-4 mt-2">
          <div v-if="!isEditingBio" @click="startEditBio" class="cursor-pointer group">
            <p class="text-[#666666] italic text-sm">
              {{ userData?.bio || '한 줄 소개가 없습니다. 클릭하여 추가해보세요.' }}
              <span class="ml-1 opacity-0 group-hover:opacity-100 text-xs text-blue-500">수정</span>
            </p>
          </div>
          <div v-else class="flex flex-col items-center gap-2">
            <input 
              v-model="editBioText" 
              class="w-full max-w-xs border-b border-[#f4f2e5] text-center text-sm py-1 focus:outline-none focus:border-[#e8e6d9]"
              placeholder="자신을 소개해주세요"
              @keyup.enter="saveBio"
            />
            <div class="flex gap-2">
              <button @click="saveBio" class="text-xs text-blue-500">저장</button>
              <button @click="isEditingBio = false" class="text-xs text-gray-400">취소</button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="stats" class="mt-8 bg-white rounded-xl p-4 border border-[#E0E0E0]">
        <div class="flex items-center justify-between py-3 border-b border-[#E0E0E0]">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-[#f4f2e5] flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-[#333333]">
                <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/>
              </svg>
            </div>
            <span class="text-[#333333]">읽은 책</span>
          </div>

          <span class="text-[#333333]">{{ userInfo.stats.books_read }}권</span>
        </div>
        <div class="flex items-center justify-between py-3 border-b border-[#E0E0E0]">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-[#f4f2e5] flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-[#333333]">
                <path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/>
              </svg>
            </div>
            <span class="text-[#333333]">작성한 댓글</span>
          </div>

          <span class="text-[#333333]">{{ userInfo.stats.comments_count }}개</span>
        </div>
        <div class="flex items-center justify-between py-3">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-[#f4f2e5] flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-[#333333]">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
              </svg>
            </div>
            <span class="text-[#333333]">평균 평점</span>
          </div>

          <span class="text-[#333333]">{{ userInfo.stats.average_rating }}점</span>
        </div>
      </div>

      <div class="mt-8 space-y-4">
        <h3 class="text-[#333333] font-bold text-md px-1">취향 북북</h3>
        <div class="bg-white rounded-xl p-5 border border-[#E0E0E0]">
          <div class="mb-5">
            <label class="block text-xs text-[#999999] mb-1">인생 도서</label>
            <div v-if="!isEditingBook" @click="isEditingBook = true" class="cursor-pointer group">
              <p class="text-[#333333] text-sm font-medium">
                {{ userData?.favorite_book || '아직 등록된 책이 없어요' }}
                <span class="ml-1 opacity-0 group-hover:opacity-100 text-xs text-blue-500 font-normal">수정</span>
              </p>
            </div>
            <div v-else class="flex gap-2 mt-1">
              <input 
                v-model="editBookText" 
                class="flex-1 border-b border-[#f4f2e5] text-sm py-1 focus:outline-none focus:border-[#e8e6d9]"
                @keyup.enter="saveBook"
              />
              <button @click="saveBook" class="text-xs text-blue-500">저장</button>
              <button @click="isEditingBook = false" class="text-xs text-gray-400">취소</button>
            </div>
          </div>

          <div>
            <label class="block text-xs text-[#999999] mb-1">선호 카테고리</label>
            <div v-if="!isEditingCategory" @click="isEditingCategory = true" class="cursor-pointer group flex flex-wrap gap-2 mt-1">
              <span v-if="userData?.selected_category" class="px-3 py-1 bg-[#f4f2e5] text-[#333333] text-xs rounded-full border border-[#e8e6d9]">
                {{ userData.selected_category }}
              </span>
              <span v-else class="text-[#999999] text-sm">관심 분야를 등록해보세요</span>
              <span class="opacity-0 group-hover:opacity-100 text-xs text-blue-500 self-center">수정</span>
            </div>
            <div v-else class="mt-2">
              <select v-model="editCategory" class="w-full text-sm border p-1 rounded focus:outline-none focus:border-[#f4f2e5]">
                <option v-for="cat in CATEGORIES" :key="cat" :value="cat">{{ cat }}</option>
              </select>
              <div class="flex justify-end gap-2 mt-2">
                <button @click="saveCategory" class="text-xs text-blue-500">저장</button>
                <button @click="isEditingCategory = false" class="text-xs text-gray-400">취소</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue';
import { useStore } from 'vuex';

const store = useStore();
const userInfo = computed(() => store.getters.currentUser);

// 페이지 마운트 시 최신 정보를 가져오도록 호출 (선택 사항)
onMounted(() => {
  // 만약 user/me 정보를 새로고침하는 action이 있다면 호출해주세요.
  store.dispatch('fetchUserInfo');
});

const props = defineProps({
  userName: String,
  stats: Object,
  isLoggedIn: Boolean,
  userData: {
    type: [Object, null],
    default: null
  }
});

const emit = defineEmits(['loginClick', 'myPageClick', 'updateBio', 'updateProfileField']);

const CATEGORIES = ['소설/시/희곡', '경제/경영', '자기계발', '인문/교양', '취미/실용', '어린이/청소년', '과학'];

// 상태 관리
const isEditingBio = ref(false);
const editBioText = ref('');
const isEditingBook = ref(false);
const editBookText = ref('');
const isEditingCategory = ref(false);
const editCategory = ref('');

// 초기값 설정 (userData 변경 시 감시)
watch(() => props.userData, (newVal) => {
  if (newVal) {
    editBioText.value = newVal.bio || '';
    editBookText.value = newVal.favorite_book || '';
    editCategory.value = newVal.selected_category || '';
  }
}, { immediate: true });

const startEditBio = () => { isEditingBio.value = true; };
const saveBio = () => { emit('updateBio', editBioText.value); isEditingBio.value = false; };

const saveBook = () => {
  emit('updateProfileField', { favorite_book: editBookText.value });
  isEditingBook.value = false;
};

const saveCategory = () => {
  emit('updateProfileField', { selected_category: editCategory.value });
  isEditingCategory.value = false;
};
</script>