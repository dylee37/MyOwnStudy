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
    selectedVoice: localStorage.getItem('selected_voice') || 'voice1',
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
      state.selectedVoice = 'voice1' // ⭐️ 로그아웃 시 기본값으로 ⭐️
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
      try {
        const config = {}
        
        // 토큰이 있을 때만 헤더에 추가 (로그인 상태인 경우)
        if (state.accessToken) {
          config.headers = {
            'Authorization': `Token ${state.accessToken}`
          }
        }

        // 이제 토큰 유무와 상관없이 서버에 요청을 보냅니다.
        // 백엔드 RecommendationView의 if request.user.is_authenticated 로직이 나머지를 처리합니다.
        const response = await axios.get(`${API_URL}/books/main-recommendations/`, config)
        commit('SET_PERSONALIZED_RECOMMENDATIONS', response.data)

      } catch (error) {
        console.error('Error fetching recommendations:', error)
        if (error.response && error.response.status === 401) {
          commit('LOGOUT')
        }
      }
    },
    // 로그인 액션은 단순화하여 삭제했습니다. 필요하다면 추가해 주세요.
  },
  modules: {}
})