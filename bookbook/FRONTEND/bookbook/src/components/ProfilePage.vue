<template>
  <div class="min-h-screen bg-background pb-20">
    <!-- Header -->
    <header class="sticky top-0 bg-white border-b border-[#E0E0E0] z-10">
      <div class="max-w-lg mx-auto px-4 py-4">
        <div class="flex items-center justify-between">
          <h1 class="text-[#333333]">프로필</h1>
          <button
            v-if="isLoggedIn"
            @click="$emit('myPageClick')"
            class="p-2 hover:bg-[#FAFAFA] rounded-full transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-[#333333]">
              <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/>
              <circle cx="12" cy="12" r="3"/>
            </svg>
          </button>
        </div>
      </div>
    </header>

    <!-- Content -->
    <div v-if="!isLoggedIn" class="flex flex-col items-center justify-center px-6 py-20">
      <div class="w-20 h-20 rounded-full bg-[#f4f2e5] flex items-center justify-center mb-6">
        <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-[#333333]">
          <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/>
          <circle cx="12" cy="7" r="4"/>
        </svg>
      </div>
      <p class="text-[#333333] mb-6 text-center">로그인을 해주세요</p>
      <button
        @click="$emit('loginClick')"
        class="px-8 py-3 bg-[#f4f2e5] text-[#333333] rounded-lg hover:bg-[#e8e6d9] transition-colors"
      >
        로그인
      </button>
    </div>

    <main v-else class="max-w-lg mx-auto px-4 py-6">
      <!-- Profile Info -->
      <div class="flex flex-col items-center">
        <div class="w-20 h-20 rounded-full bg-[#f4f2e5] flex items-center justify-center mb-3">
          <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-[#333333]">
            <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
        </div>
        <h2 class="text-[#333333] mb-1">{{ userName }}</h2>
      </div>

      <!-- Stats -->
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
          <span class="text-[#333333]">{{ stats.booksRead }}권</span>
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
          <span class="text-[#333333]">{{ stats.comments }}개</span>
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
          <span class="text-[#333333]">{{ stats.averageRating.toFixed(1) }}점</span>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
defineProps({
  userName: String,
  stats: Object,
  isLoggedIn: Boolean
});

defineEmits(['loginClick', 'myPageClick']);
</script>