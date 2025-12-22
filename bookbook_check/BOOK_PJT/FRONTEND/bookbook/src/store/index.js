// src/store/index.js (Vue 3 / Vuex 4 표준)

import { createStore } from 'vuex' // ⭐️ createStore 임포트 ⭐️
import axios from 'axios'

const API_URL = 'http://127.0.0.1:8000/api'

// ⭐️ Vuex Store 생성 (createStore 사용) ⭐️
export default createStore({
  state: {
    // 1. 베스트셀러 20권
    bestsellers: [],
    // 2. 맞춤 추천 2권
    personalizedRecommendations: [],
    // 사용자 인증 상태 (토큰 유무로 판단)
    accessToken: localStorage.getItem('authToken') || null,
    userInfo: JSON.parse(localStorage.getItem('user_info')) || null, // 사용자 정보
    // ⭐️ 3. 사용자 선택 TTS 목소리 ⭐️
    selectedVoice: localStorage.getItem('selected_voice') || 'alloy',
  },
  
  getters: {
    isLoggedIn: state => !!state.accessToken,
    bestsellers: state => state.bestsellers,
    personalizedRecommendations: state => state.personalizedRecommendations,
    currentUser: state => state.userInfo,
    // ⭐️ 선택된 목소리 getter 추가 ⭐️
    selectedVoice: state => state.selectedVoice,
  },

  mutations: {
    // 데이터 저장
    SET_BESTSELLERS(state, books) {
      state.bestsellers = books
    },
    SET_PERSONALIZED_RECOMMENDATIONS(state, books) {
      state.personalizedRecommendations = books
    },
    // 인증 상태 관리
    SET_AUTH_TOKENS(state, { access, refresh }) {
      state.accessToken = access
      localStorage.setItem('authToken', access)
      localStorage.setItem('refresh_token', refresh)
    },
    SET_USER_INFO(state, user) {
      state.userInfo = user
      localStorage.setItem('user_info', JSON.stringify(user))
      // ⭐️ 사용자 정보 설정 시 목소리 설정도 함께 업데이트 ⭐️
      if (user && user.selected_voice) {
        state.selectedVoice = user.selected_voice
        localStorage.setItem('selected_voice', user.selected_voice)
      }
    },
    LOGOUT(state) {
      state.accessToken = null
      state.userInfo = null
      state.selectedVoice = 'alloy' // ⭐️ 로그아웃 시 기본값으로 ⭐️
      localStorage.removeItem('authToken')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user_info')
      localStorage.removeItem('selected_voice') // ⭐️ 로컬 스토리지에서도 삭제 ⭐️
      state.personalizedRecommendations = []
    },
    // ⭐️ 목소리 설정 변경 뮤테이션 ⭐️
    SET_SELECTED_VOICE(state, voiceId) {
      state.selectedVoice = voiceId
      localStorage.setItem('selected_voice', voiceId)
    },
  },

  actions: {
    // 1. 베스트셀러 20권 목록 가져오기 (공통)
    async fetchBestsellers({ commit }) {
      try {
        const response = await axios.get(`${API_URL}/books/bestsellers/`)
        commit('SET_BESTSELLERS', response.data)
      } catch (error) {
        console.error('Error fetching bestsellers:', error)
      }
    },


    // 2. 사용자 맞춤 추천 2권 가져오기 (인증 필요)
    async fetchPersonalizedRecommendations({ commit, state }) {
      if (state.personalizedRecommendations.length > 0) {
        return;
      }
      try {
        // 1. state뿐만 아니라 localStorage에서도 직접 확인 (안전장치)
        const token = state.accessToken || localStorage.getItem('authToken')
        
        const config = {}
        if (token) {
          config.headers = {
            'Authorization': `Token ${token}`
          }
        }

        const response = await axios.get(`${API_URL}/books/main-recommendations/`, config)
        commit('SET_PERSONALIZED_RECOMMENDATIONS', response.data)
      } catch (error) {
        console.error('Error fetching recommendations:', error)
        commit('SET_PERSONALIZED_RECOMMENDATIONS', [])
      }
    },
  },
  modules: {}
})