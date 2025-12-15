<template>
  <div class="fixed inset-0 bg-white z-50 flex items-center justify-center">
    <div class="w-full max-w-md px-6">
      <!-- Logo -->
      <div class="flex flex-col items-center mb-8">
        <div class="w-20 h-20 rounded-full bg-[#f4f2e5] flex items-center justify-center mb-4">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="40"
            height="40"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="text-[#333333]"
          >
            <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/>
          </svg>
        </div>
        <h1 class="text-[#333333] mb-2">BOOKBOOK</h1>
        <p class="text-[#666666]" style="font-size: 0.875rem">
          TOKTOK으로 나누는 독서 경험
        </p>
      </div>

      <!-- Login Form -->
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label for="email" class="block text-[#333333] mb-2" style="font-size: 0.875rem">
            이메일
          </label>
          <input
            id="email"
            v-model="email"
            type="email"
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
            v-model="password"
            type="password"
            placeholder="비밀번호를 입력하세요"
            class="w-full px-4 py-3 bg-[#FAFAFA] rounded-lg border border-[#E0E0E0] focus:outline-none focus:border-[#f4f2e5]"
            required
          />
        </div>

        <button
          type="submit"
          class="w-full py-3 bg-[#f4f2e5] text-[#333333] rounded-lg hover:bg-[#e8e6d9] transition-colors"
        >
          로그인
        </button>

        <div class="flex gap-2">
          <button
            type="button"
            @click="$emit('close')"
            class="flex-[2] py-3 bg-white text-[#666666] rounded-lg border border-[#E0E0E0] hover:bg-[#FAFAFA] transition-colors"
          >
            돌아가기
          </button>
          <button
            type="button"
            @click="$emit('signupClick')"
            class="flex-1 py-3 bg-white text-[#666666] rounded-lg border border-[#E0E0E0] hover:bg-[#FAFAFA] transition-colors"
          >
            회원가입
          </button>
        </div>
      </form>


    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const email = ref('');
const password = ref('');

const emit = defineEmits(['login', 'close', 'signupClick']);

const handleSubmit = () => {
  if (email.value && password.value) {
    emit('login', email.value, password.value);
  }
};
</script>