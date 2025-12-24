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
            닉네임 <span class="text-red-500">*</span>
          </label>
          <input id="name" type="text" v-model="name" placeholder="닉네임을 입력하세요"
            class="w-full px-4 py-3 bg-[#FAFAFA] rounded-lg border border-[#E0E0E0] focus:outline-none focus:border-[#f4f2e5]"
            required />
        </div>

        <div>
          <label for="email" class="block text-[#333333] mb-2" style="font-size: 0.875rem">
            이메일 <span class="text-red-500">*</span>
          </label>
          <input id="email" type="email" v-model="email" placeholder="example@email.com"
            class="w-full px-4 py-3 bg-[#FAFAFA] rounded-lg border border-[#E0E0E0] focus:outline-none focus:border-[#f4f2e5]"
            required />
        </div>

        <div>
          <label for="password" class="block text-[#333333] mb-2" style="font-size: 0.875rem">
            비밀번호 <span class="text-red-500">*</span>
          </label>
          <input id="password" type="password" v-model="password" placeholder="비밀번호를 입력하세요"
            class="w-full px-4 py-3 bg-[#FAFAFA] rounded-lg border border-[#E0E0E0] focus:outline-none focus:border-[#f4f2e5]"
            required />
        </div>

        <div>
          <label for="password_confirm" class="block text-sm font-medium text-[#666666] mb-1">비밀번호 확인 <span class="text-red-500">*</span></label>
          <input id="password_confirm" v-model="passwordConfirm" type="password" required
            class="w-full px-4 py-3 border border-[#E0E0E0] rounded-lg bg-white placeholder-[#999999] focus:ring-2 focus:ring-[#f4f2e5] focus:border-[#f4f2e5] transition-colors"
            placeholder="비밀번호를 다시 입력하세요" />
        </div>

        <div>
          <label for="voice" class="block text-[#333333] mb-2" style="font-size: 0.875rem">
            선택한 내 목소리 <span class="text-red-500">*</span>
          </label>
          <div class="space-y-2">
            <select id="voice" v-model="selectedVoice"
              class="w-full px-4 py-3 bg-[#FAFAFA] rounded-lg border border-[#E0E0E0] focus:outline-none focus:border-[#f4f2e5]">
              <option v-for="voice in VOICE_OPTIONS" :key="voice.id" :value="voice.id">
                {{ voice.name }}
              </option>
            </select>
            <button type="button" @click="playVoiceSample(selectedVoice)"
              class="w-full py-2 px-4 bg-white rounded-lg border border-[#E0E0E0] hover:bg-[#FAFAFA] transition-colors flex items-center justify-center gap-2 text-[#666666]">
              <Volume2 :size="18" />
              목소리 들어보기
            </button>
          </div>
        </div>

        <div>
          <label for="favoriteBook" class="block text-[#333333] mb-2" style="font-size: 0.875rem">
            좋아하는 도서 (선택)
          </label>
          <input id="favoriteBook" type="text" v-model="favoriteBook" placeholder="좋아하는 책 제목을 입력하세요"
            class="w-full px-4 py-3 bg-[#FAFAFA] rounded-lg border border-[#E0E0E0] focus:outline-none focus:border-[#f4f2e5]" />
        </div>

        <div>
          <label class="block text-[#333333] mb-2" style="font-size: 0.875rem">
            좋아하는 카테고리 <span class="text-red-500">*</span>
          </label>
          <button type="button" @click="showCategorySelector = !showCategorySelector"
            class="w-full px-4 py-3 bg-[#FAFAFA] rounded-lg border border-[#E0E0E0] focus:outline-none focus:border-[#f4f2e5] flex items-center justify-between text-left">
            <span :class="selectedCategory ? 'text-[#333333]' : 'text-[#999999]'">
              {{ selectedCategory || '카테고리를 선택하세요' }}
            </span>
            <ChevronDown :size="20"
              :class="`text-[#666666] transition-transform ${showCategorySelector ? 'rotate-180' : ''}`" />
          </button>

          <div v-if="showCategorySelector" class="mt-2 bg-white rounded-lg border border-[#E0E0E0] overflow-hidden">
            <button v-for="category in CATEGORIES" :key="category" type="button" @click="handleCategorySelect(category)"
              :class="`w-full px-4 py-3 text-left hover:bg-[#f4f2e5] transition-colors ${selectedCategory === category ? 'bg-[#f4f2e5] text-[#333333]' : 'text-[#666666]'
                }`">
              {{ category }}
            </button>
          </div>
        </div>

        <button type="submit"
          class="w-full py-3 bg-[#f4f2e5] text-[#333333] rounded-lg hover:bg-[#e8e6d9] transition-colors">
          회원가입
        </button>

        <div class="flex gap-2">
          <button type="button" @click="emit('close')"
            class="flex-[2] py-3 bg-white text-[#666666] rounded-lg border border-[#E0E0E0] hover:bg-[#FAFAFA] transition-colors">
            돌아가기
          </button>
          <button type="button" @click="emit('loginClick')"
            class="flex-1 py-3 bg-white text-[#666666] rounded-lg border border-[#E0E0E0] hover:bg-[#FAFAFA] transition-colors">
            로그인
          </button>
        </div>
      </form>

    </div>
  </div>

  <div class="toast-container">
    <Transition name="toast">
      <div v-if="toast.show" class="toast-content">
        <span class="message">{{ toast.message }}</span>
      </div>
    </Transition>
  </div>
</template>


<script setup lang="ts">
import { ref, reactive, provide } from 'vue';
import { BookOpen, Volume2, ChevronDown } from 'lucide-vue-next';

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

// ----------------------------------------------------------------
// 1. Props 및 Emit 정의 (React의 Interface/Props와 동일)
// ----------------------------------------------------------------
// ⭐️ emit 구조를 변경: passwordConfirm을 추가하고, 백엔드가 요구하지 않을 수 있는 필드는 임시 제거합니다.
// App.vue의 handleSignup 함수가 받도록 구조를 맞춥니다. (이메일, 비밀번호, 닉네임, 비밀번호확인)
const emit = defineEmits<{
  (e: 'signup', email: string, password: string, name: string, passwordConfirm: string, voice: string, favoriteBook: string, category: string): void;
  // 👆 passwordConfirm 필드 타입을 string으로 추가했습니다.
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
    showToast('비밀번호가 일치하지 않습니다.');
    return;
  }
  if (!selectedCategory.value) {
    showToast('카테고리를 선택해주세요.');
    return;
  }
  if (email.value && password.value && name.value) {
    emit(
      'signup',
      email.value,
      password.value,
      name.value,
      passwordConfirm.value,
      selectedVoice.value,
      favoriteBook.value,
      selectedCategory.value
    );
  }
};

const playVoiceSample = async (voiceId: string) => {
  const voice = VOICE_OPTIONS.find((v) => v.id === voiceId);
  if (!voice) return;

  try {
    const response = await fetch('http://127.0.0.1:8000/api/books/tts/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: voice.sample, 
        voice: voiceId      
      })
    });

    if (!response.ok) throw new Error("음성 샘플 생성 실패");

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const audio = new Audio(url);
    
    await audio.play();

    audio.onended = () => {
      window.URL.revokeObjectURL(url);
    };

  } catch (error) {
    console.error("목소리 샘플 재생 에러:", error);
    showToast("목소리 샘플을 불러오지 못했습니다.");
  }
};

const handleCategorySelect = (category: string) => {
  selectedCategory.value = category;
  showCategorySelector.value = false;
};

// React의 onClose와 onLoginClick은 emit('close')와 emit('loginClick')으로 대체
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