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
    accessToken: localStorage.getItem('access_token') || null,
    userInfo: JSON.parse(localStorage.getItem('user_info')) || null, // 사용자 정보
  },
  
  getters: {
    isLoggedIn: state => !!state.accessToken,
    bestsellers: state => state.bestsellers,
    personalizedRecommendations: state => state.personalizedRecommendations,
    currentUser: state => state.userInfo,
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
      localStorage.setItem('access_token', access)
      localStorage.setItem('refresh_token', refresh)
    },
    SET_USER_INFO(state, user) {
      state.userInfo = user
      localStorage.setItem('user_info', JSON.stringify(user))
    },
    LOGOUT(state) {
      state.accessToken = null
      state.userInfo = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user_info')
      state.personalizedRecommendations = []
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

    // 2. 사용자 맞춤 추천 2권 가져오기 (공통)
    async fetchPersonalizedRecommendations({ commit, getters }) {
      let config = {}
      if (getters.isLoggedIn) {
        config = {
          headers: {
            'Authorization': `Bearer ${getters.accessToken}`
          }
        }
      }

      try {
        const response = await axios.get(`${API_URL}/books/main-recommendations/`, config)
        commit('SET_PERSONALIZED_RECOMMENDATIONS', response.data)
      } catch (error) {
        console.error('Error fetching personalized recommendations:', error.response ? error.response.data : error)
        if (error.response && error.response.status === 401) {
            commit('LOGOUT') 
            alert('인증이 만료되었습니다. 다시 로그인해주세요.')
        }
      }
    },
    // 로그인 액션은 단순화하여 삭제했습니다. 필요하다면 추가해 주세요.
  },
  modules: {}
})