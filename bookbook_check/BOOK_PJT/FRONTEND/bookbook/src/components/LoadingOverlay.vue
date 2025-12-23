<template>
  <div class="fixed inset-0 bg-white z-[200] flex flex-col items-center justify-center">
    <div class="relative">
      <div class="animate-bounce">
        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
          <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
        </svg>
      </div>
      <div class="w-10 h-1 bg-black/10 rounded-full mx-auto mt-4 animate-pulse"></div>
    </div>
    <p class="mt-6 text-[#333] font-medium tracking-tight animate-pulse">책장을 넘기고 있어요...</p>
  </div>
</template>