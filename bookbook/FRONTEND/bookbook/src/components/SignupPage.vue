<script setup lang="ts">
import { ref } from 'vue';
import { BookOpen, Volume2, ChevronDown } from 'lucide-vue-next';

// ----------------------------------------------------------------
// 1. Props 및 Emit 정의 (React의 Interface/Props와 동일)
// ----------------------------------------------------------------
// React의 onSignup, onClose, onLoginClick에 해당
const emit = defineEmits<{
  (e: 'signup', email: string, password: string, name: string, voice: string, favoriteBook: string, category: string): void;
  (e: 'close'): void;
  (e: 'loginClick'): void;
}>();

// ----------------------------------------------------------------
// 2. 상수 데이터
// ----------------------------------------------------------------
const VOICE_OPTIONS = [
  { id: 'voice1', name: '목소리 1 (여성, 차분한)', sample: '안녕하세요, 목소리 1번입니다.' },
  { id: 'voice2', name: '목소리 2 (남성, 활기찬)', sample: '안녕하세요, 목소리 2번입니다.' },
  { id: 'voice3', name: '목소리 3 (여성, 밝은)', sample: '안녕하세요, 목소리 3번입니다.' },
  { id: 'voice4', name: '목소리 4 (남성, 따뜻한)', sample: '안녕하세요, 목소리 4번입니다.' },
];

const CATEGORIES = [
  '소설/시/희곡',
  '경제/경영',
  '자기계발',
  '인문/교양',
  '취미/실용',
  '어린이/청소년',
  '과학',
];

// ----------------------------------------------------------------
// 3. 상태 관리 (React의 useState에 해당)
// ----------------------------------------------------------------
const email = ref('');
const password = ref('');
const passwordConfirm = ref('');
const name = ref('');
const selectedVoice = ref(VOICE_OPTIONS[0].id);
const favoriteBook = ref('');
const selectedCategory = ref('');
const showCategorySelector = ref(false);

// ----------------------------------------------------------------
// 4. 메서드/핸들러
// ----------------------------------------------------------------
const handleSubmit = (e: Event) => {
  e.preventDefault();
  if (password.value !== passwordConfirm.value) {
    alert('비밀번호가 일치하지 않습니다.');
    return;
  }
  if (!selectedCategory.value) {
    alert('카테고리를 선택해주세요.');
    return;
  }
  if (email.value && password.value && name.value) {
    emit(
      'signup',
      email.value,
      password.value,
      name.value,
      selectedVoice.value,
      favoriteBook.value,
      selectedCategory.value
    );
  }
};

const playVoiceSample = (voiceId: string) => {
  const voice = VOICE_OPTIONS.find((v) => v.id === voiceId);
  if (voice) {
    // Mock: 실제로는 TTS API를 사용
    alert(`${voice.name} 재생:\n"${voice.sample}"`);
  }
};

const handleCategorySelect = (category: string) => {
  selectedCategory.value = category;
  showCategorySelector.value = false;
};

// React의 onClose와 onLoginClick은 emit('close')와 emit('loginClick')으로 대체
</script>

<template>
  <div class="fixed inset-0 bg-white z-50 flex items-center justify-center overflow-y-auto">
    <div class="w-full max-w-md px-6 py-8 my-auto">
      <div class="flex flex-col items-center mb-8">
        <div class="w-20 h-20 rounded-full bg-[#f4f2e5] flex items-center justify-center mb-4">
          <BookOpen :size="40" class="text-[#333333]" />
        </div>
        <h1 class="text-[#333333] mb-2">BOOKBOOK</h1>
        <p class="text-[#666666]" style="font-size: 0.875rem">
          회원가입하고 TOKTOK 시작하기
        </p>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label for="name" class="block text-[#333333] mb-2" style="font-size: 0.875rem">
            닉네임
          </label>
          <input
            id="name"
            type="text"
            v-model="name"
            placeholder="닉네임을 입력하세요"
            class="w-full px-4 py-3 bg-[#FAFAFA] rounded-lg border border-[#E0E0E0] focus:outline-none focus:border-[#f4f2e5]"
            required
          />
        </div>

        <div>
          <label for="email" class="block text-[#333333] mb-2" style="font-size: 0.875rem">
            이메일
          </label>
          <input
            id="email"
            type="email"
            v-model="email"
            placeholder="example@email.com"
            class="w-full px-4 py-3 bg-[#FAFAFA] rounded-lg border border-[#E0E0E0] focus:outline-none focus:border-[#f4f2e5]"
            required
          />
        </div>

        <div>
          <label for="password" class="block text-[#333333] mb-2" style="font-size: 0.875rem">
            비밀번호
          </label>
          <input
            id="password"
            type="password"
            v-model="password"
            placeholder="비밀번호를 입력하세요"
            class="w-full px-4 py-3 bg-[#FAFAFA] rounded-lg border border-[#E0E0E0] focus:outline-none focus:border-[#f4f2e5]"
            required
          />
        </div>

        <div>
          <label for="passwordConfirm" class="block text-[#333333] mb-2" style="font-size: 0.875rem">
            비밀번호 확인
          </label>
          <input
            id="passwordConfirm"
            type="password"
            v-model="passwordConfirm"
            placeholder="비밀번호를 다시 입력하세요"
            class="w-full px-4 py-3 bg-[#FAFAFA] rounded-lg border border-[#E0E0E0] focus:outline-none focus:border-[#f4f2e5]"
            required
          />
        </div>

        <div>
          <label for="voice" class="block text-[#333333] mb-2" style="font-size: 0.875rem">
            선택한 내 목소리
          </label>
          <div class="space-y-2">
            <select
              id="voice"
              v-model="selectedVoice"
              class="w-full px-4 py-3 bg-[#FAFAFA] rounded-lg border border-[#E0E0E0] focus:outline-none focus:border-[#f4f2e5]"
            >
              <option v-for="voice in VOICE_OPTIONS" :key="voice.id" :value="voice.id">
                {{ voice.name }}
              </option>
            </select>
            <button
              type="button"
              @click="playVoiceSample(selectedVoice)"
              class="w-full py-2 px-4 bg-white rounded-lg border border-[#E0E0E0] hover:bg-[#FAFAFA] transition-colors flex items-center justify-center gap-2 text-[#666666]"
            >
              <Volume2 :size="18" />
              목소리 들어보기
            </button>
          </div>
        </div>

        <div>
          <label for="favoriteBook" class="block text-[#333333] mb-2" style="font-size: 0.875rem">
            좋아하는 도서 (추천을 위한)
          </label>
          <input
            id="favoriteBook"
            type="text"
            v-model="favoriteBook"
            placeholder="좋아하는 책 제목을 입력하세요"
            class="w-full px-4 py-3 bg-[#FAFAFA] rounded-lg border border-[#E0E0E0] focus:outline-none focus:border-[#f4f2e5]"
          />
        </div>

        <div>
          <label class="block text-[#333333] mb-2" style="font-size: 0.875rem">
            좋아하는 카테고리 <span class="text-red-500">*</span>
          </label>
          <button
            type="button"
            @click="showCategorySelector = !showCategorySelector"
            class="w-full px-4 py-3 bg-[#FAFAFA] rounded-lg border border-[#E0E0E0] focus:outline-none focus:border-[#f4f2e5] flex items-center justify-between text-left"
          >
            <span :class="selectedCategory ? 'text-[#333333]' : 'text-[#999999]'">
              {{ selectedCategory || '카테고리를 선택하세요' }}
            </span>
            <ChevronDown :size="20" :class="`text-[#666666] transition-transform ${showCategorySelector ? 'rotate-180' : ''}`" />
          </button>
          
          <div v-if="showCategorySelector" class="mt-2 bg-white rounded-lg border border-[#E0E0E0] overflow-hidden">
            <button
              v-for="category in CATEGORIES"
              :key="category"
              type="button"
              @click="handleCategorySelect(category)"
              :class="`w-full px-4 py-3 text-left hover:bg-[#f4f2e5] transition-colors ${
                selectedCategory === category ? 'bg-[#f4f2e5] text-[#333333]' : 'text-[#666666]'
              }`"
            >
              {{ category }}
            </button>
          </div>
        </div>

        <button
          type="submit"
          class="w-full py-3 bg-[#f4f2e5] text-[#333333] rounded-lg hover:bg-[#e8e6d9] transition-colors"
        >
          회원가입
        </button>

        <div class="flex gap-2">
          <button
            type="button"
            @click="emit('close')"
            class="flex-[2] py-3 bg-white text-[#666666] rounded-lg border border-[#E0E0E0] hover:bg-[#FAFAFA] transition-colors"
          >
            돌아가기
          </button>
          <button
            type="button"
            @click="emit('loginClick')"
            class="flex-1 py-3 bg-white text-[#666666] rounded-lg border border-[#E0E0E0] hover:bg-[#FAFAFA] transition-colors"
          >
            로그인
          </button>
        </div>
      </form>

      <div class="mt-6 p-4 bg-[#F3D8D8] rounded-lg">
        <p class="text-[#666666] text-center" style="font-size: 0.75rem">
          데모 버전: 아무 정보로 회원가입 가능합니다
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 여기에 Vue 컴포넌트 스코프 스타일을 추가할 수 있습니다. 
   현재는 모든 스타일이 Tailwind CSS 클래스로 적용되어 있습니다. */
</style>