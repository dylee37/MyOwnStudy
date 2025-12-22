<template>
  <div class="fixed inset-0 bg-white z-[100] flex flex-col items-center justify-between px-8 py-16">
    <button @click="$emit('finish')" class="absolute top-10 right-8 text-[#999999] font-medium">
      건너뛰기
    </button>

    <div :key="currentStep" class="flex-1 flex flex-col items-center justify-center text-center animate-in">
      <div class="w-64 h-64 bg-[#f4f2e5] rounded-full flex items-center justify-center mb-12 shadow-sm">
        <component :is="steps[currentStep].icon" :size="100" stroke-width="1.5" class="text-[#333333]" />
      </div>
      
      <h2 class="text-2xl font-bold text-[#333333] mb-5 leading-tight whitespace-pre-line">
        {{ steps[currentStep].title }}
      </h2>
      <p class="text-[#666666] leading-relaxed break-keep">
        {{ steps[currentStep].description }}
      </p>
    </div>

    <div class="w-full max-w-xs mx-auto">
      <div class="flex justify-center gap-2 mb-10">
        <div 
          v-for="(_, index) in steps" :key="index"
          class="h-1.5 transition-all duration-300 rounded-full"
          :class="[currentStep === index ? 'w-8 bg-[#333333]' : 'w-2 bg-[#E0E0E0]']"
        ></div>
      </div>

      <button 
        @click="nextStep"
        class="w-full py-4 bg-[#333333] text-white rounded-2xl font-bold text-lg shadow-lg active:scale-95 transition-all"
      >
        {{ currentStep === steps.length - 1 ? 'BOOKBOOK 시작하기' : '다음으로' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { BookOpen, Mic, Heart } from 'lucide-vue-next';

const emit = defineEmits(['finish']);
const currentStep = ref(0);

const steps = [
  {
    icon: BookOpen,
    title: "당신만을 위한\n인생 도서 큐레이션",
    description: "취향 분석을 통해 매일 새로운\n독서 경험을 선물해 드립니다."
  },
  {
    icon: Mic,
    title: "생생하게 나누는\n음성 톡톡(TOKTOK)",
    description: "글자로는 다 전하지 못할 감동을\n나만의 목소리로 기록해보세요."
  },
  {
    icon: Heart,
    title: "나만의 기록을\n한눈에 확인하세요",
    description: "읽은 책의 통계와 기록들을\n아름답게 수집하고 관리할 수 있습니다."
  }
];

const nextStep = () => {
  if (currentStep.value < steps.length - 1) {
    currentStep.value++;
  } else {
    emit('finish');
  }
};
</script>

<style scoped>
.animate-in {
  animation: slideUp 0.6s cubic-bezier(0.23, 1, 0.32, 1);
}
@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>