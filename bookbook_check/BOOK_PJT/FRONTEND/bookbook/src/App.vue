<template>
  <div class="min-h-screen bg-background">
    
    <OnboardingPage v-if="showOnboarding" @finish="handleFinishOnboarding" />

    <template v-else-if="showMyPage || showSignupPage || showLoginPage">
      <MyPage 
        v-if="showMyPage" 
        :userName="userName" 
        :profileData="userProfile" 
        @back="showMyPage = false" 
        @logout="handleLogout"
        @deleteAccount="handleDeleteAccount" 
        @updateProfile="handleUpdateProfile" 
      />
      <SignupPage 
        v-else-if="showSignupPage" 
        @signup="handleSignup" 
        @close="showSignupPage = false"
        @loginClick="handleShowLogin" 
      />
      <LoginPage 
        v-else-if="showLoginPage" 
        @login="handleLogin" 
        @close="showLoginPage = false"
        @signupClick="handleShowSignup" 
      />
    </template>

    <template v-else-if="selectedBook">
      <BookDetailPage 
        :book="selectedBook" 
        :comments="selectedBook.comments || []" 
        :isLoggedIn="isLoggedIn"
        :currentUserId="userData?.id" 
        @back="selectedBook = null" 
        @addComment="handleAddComment" 
        @loginClick="showLoginPage = true"
        @deleteComment="handleDeleteComment" 
        @updateComment="handleUpdateComment"
      />
      <AddCommentDialog :isOpen="showAddCommentDialog" @close="showAddCommentDialog = false" @submit="handleSubmitComment" />
    </template>

    <template v-else>
      <HomePage v-if="activeTab === 'home'" @bookClick="handleBookClick" @searchClick="isSearchOpen = true" />
      <LibraryPage v-else-if="activeTab === 'library'" :books="isLoggedIn ? libraryBooks : []" :isLoggedIn="isLoggedIn"
        @bookClick="handleBookClick" @loginClick="showLoginPage = true" />
      <ProfilePage v-else-if="activeTab === 'profile'" :userName="userName" :stats="stats" :isLoggedIn="isLoggedIn"
        :userData="userData" @loginClick="showLoginPage = true" @myPageClick="handleMyPageClick" @updateBio="handleUpdateBio" @updateProfileField="handleUpdateProfileField"/>
      
      <BottomNavigation :activeTab="activeTab" @tabChange="activeTab = $event" />
      
      <SearchDialog :isOpen="isSearchOpen" :books="books" @close="isSearchOpen = false" @bookClick="handleBookClick" />
    </template>

  </div>

  <div id="app">
    <router-view /> <ToastMessage :show="toast.show" :message="toast.message" />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, reactive, provide } from 'vue';
import { useStore } from 'vuex'

import ToastMessage from './components/ToastMessage.vue';
import HomePage from './components/HomePage.vue';
import LibraryPage from './components/LibraryPage.vue';
import ProfilePage from './components/ProfilePage.vue';
import BookDetailPage from './components/BookDetailPage.vue';
import LoginPage from './components/LoginPage.vue';
import SignupPage from './components/SignupPage.vue';
import MyPage from './components/MyPage.vue';
import BottomNavigation from './components/BottomNavigation.vue';
import SearchDialog from './components/SearchDialog.vue';
import AddCommentDialog from './components/AddCommentDialog.vue';
import OnboardingPage from './components/OnboardingPage.vue';

import axios from 'axios'

const activeTab = ref('home');
const selectedBook = ref(null);
const isSearchOpen = ref(false);

const isLoggedIn = ref(false);
const showLoginPage = ref(false);
const showSignupPage = ref(false);
const showMyPage = ref(false);
const showAddCommentDialog = ref(false);
const userData = ref(null);
const userName = ref('복복');
const libraryBooks = ref([]); 
const books = ref([]);
const userProfile = ref(null);
const showOnboarding = ref(false);

const store = useStore()

const stats = reactive({
  booksRead: 0,
  comments: 0,
  averageRating: 0.0
});

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


const handleBookClick = async (book) => {
  try {
    const response = await axios.get(`http://127.0.0.1:8000/api/books/${book.id}/`);
    selectedBook.value = response.data;
  } catch (error) {
    console.error('책 상세 정보를 불러오는 데 실패했습니다:', error);
    selectedBook.value = book;
  }
};

const fetchBooks = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/books/');
    books.value = response.data; 
  } catch (error) {
    console.error('책 목록을 불러오는 데 실패했습니다:', error);
  }
};
onMounted(() => {
  fetchBooks();
});


const fetchUserData = async () => {
  try {
    const token = localStorage.getItem('authToken');
    const response = await axios.get('http://127.0.0.1:8000/api/v1/user/me/', {
      headers: { Authorization: `Token ${token}` }
    });

    userData.value = response.data;
    userName.value = response.data.name;

    stats.booksRead = response.data.stats?.books_read || 0;
    stats.comments = response.data.stats?.comments_count || 0;
    stats.averageRating = response.data.stats?.average_rating || 0;

    store.commit('SET_USER_INFO', response.data);

  } catch (error) {
    console.error('사용자 정보 로드 실패:', error);
    userData.value = null;
    store.commit('LOGOUT'); 
  }
};

const fetchLibraryBooks = async () => {
  try {
    const token = localStorage.getItem('authToken');
    const response = await axios.get('http://127.0.0.1:8000/api/v1/user/library/', {
      headers: { Authorization: `Token ${token}` }
    });
    libraryBooks.value = response.data; 
  } catch (error) {
    console.error('라이브러리 책 목록 로드 실패:', error);
    libraryBooks.value = [];
  }
};

const handleAddComment = () => {
  if (!isLoggedIn.value) {
    showLoginPage.value = true;
    return;
  }
  showAddCommentDialog.value = true;
};

function calculateLocalAverage(comments) {
  if (!comments || comments.length === 0) return 0;
  const validComments = comments.filter(c => c.rating != null && c.rating > 0);
  if (validComments.length === 0) return 0;

  const sumRating = validComments.reduce((sum, comment) => sum + comment.rating, 0);
  return sumRating / validComments.length;
}


const handleSubmitComment = async ({ text, isVoice, rating, voice_choice }) => {
  if (!selectedBook.value) return; 

  const token = localStorage.getItem('authToken');
  if (!token) {
    showToast('로그인 세션이 만료되었습니다. 다시 로그인해주세요.');
    showAddCommentDialog.value = false;
    showLoginPage.value = true;
    return;
  }

  const ratingForDB = rating;

  const commentData = {
    content: text,
    rating: ratingForDB,
    is_voice: isVoice,
    voice_choice: voice_choice,
  };

  try {
    const response = await axios.post(
      `http://127.0.0.1:8000/api/books/${selectedBook.value.id}/comments/`,
      commentData,
      {
        headers: {
          Authorization: `Token ${token}`, 
          'Content-Type': 'application/json',
        },
      }
    );

    showToast(`${isVoice ? '음성' : '텍스트'} TOKTOK이 성공적으로 등록되었습니다!`);

    if (selectedBook.value.comments) {
      selectedBook.value.comments.unshift(response.data); 
    } else {
      selectedBook.value.comments = [response.data];
    }


    const newAverageRating = calculateLocalAverage(selectedBook.value.comments);
    const newCommentCount = selectedBook.value.comments.length;

    const bookIndex = books.value.findIndex(book => book.id === selectedBook.value.id);
    if (bookIndex !== -1) {
      books.value[bookIndex] = {
        ...books.value[bookIndex],
        rating: newAverageRating,
        commentCount: newCommentCount
      };
    }

    showAddCommentDialog.value = false;
    fetchLibraryBooks();

  } catch (error) {
    console.error('댓글 등록 실패:', error.response?.data || error.message);

    let errorMessage = '댓글 등록에 실패했습니다. 잠시 후 다시 시도해 주세요.';
    if (error.response?.status === 401) {
      errorMessage = '인증 오류: 다시 로그인해주세요.';
      handleLogout(); 
    } else if (error.response?.data?.rating) {
      errorMessage = `평점 오류: ${error.response.data.rating[0]}`;
    } else if (error.response?.data?.content) {
      errorMessage = `내용 오류: ${error.response.data.content[0]}`;
    }

    showToast(errorMessage);
  }
};

const fetchUserProfile = async () => {
  const token = localStorage.getItem('authToken');
  if (!token) {
    return;
  }

  const API_URL = "http://127.0.0.1:8000/api/v1/user/profile/update/";

  try {
    const response = await fetch(API_URL, {
      method: "GET", // 프로필 조회
      headers: {
        Authorization: `Token ${token}`,
      },
    });

    if (response.ok) {
      const data = await response.json();
      userProfile.value = data;

      userName.value = data.nickname;
    } else {
      console.error("프로필 로드 실패:", response.status);
      userProfile.value = null;
    }
  } catch (error) {
    console.error("프로필 로드 중 오류 발생:", error);
    userProfile.value = null;
  }
};


const handleLogin = async (email, password) => {
  try {
    const loginUrl = 'http://127.0.0.1:8000/api/v1/user/login/';

    const response = await axios.post(loginUrl, {
      email: email,
      password: password
    });

    const token = response.data.token;
    localStorage.setItem('authToken', token);

    
    await Promise.all([
      fetchUserData(), 
      fetchLibraryBooks() 
    ]);
    
    isLoggedIn.value = true;
    showLoginPage.value = false;
    activeTab.value = 'home';
    
    showToast(`로그인 성공! ${userName.value}님 환영합니다.`);

  } catch (error) {
    console.error('로그인 실패:', error.response?.data || error.message);
    showToast('로그인 실패: 이메일 또는 비밀번호를 확인해주세요.');
    isLoggedIn.value = false;
  }
};

const handleSignup = async (email, password, name, passwordConfirm, voice, favoriteBook, category) => {
  try {
    const signupUrl = 'http://127.0.0.1:8000/api/v1/user/signup/';

    const response = await axios.post(signupUrl, {
      email: email,
      password: password,
      name: name,
      password_confirm: passwordConfirm,
      selected_category: category,
      selected_voice: voice,
      favorite_book: favoriteBook,

    });

    if (response.status === 201) {
      showToast('회원가입 성공! 이제 로그인해주세요.');
      showSignupPage.value = false;
      showLoginPage.value = true;
    }
  } catch (error) {
    console.error('Signup failed:', error.response?.data || error.message);

    let errorMessage = '회원가입 실패: 서버 오류가 발생했습니다.';
    if (error.response && error.response.data) {
      if (error.response.data.email) {
        errorMessage = `이메일 오류: ${error.response.data.email[0]}`;
      } else if (error.response.data.nickname) {
        errorMessage = `닉네임 오류: ${error.response.data.nickname[0]}`;
      } else if (error.response.status === 400) {
        errorMessage = '입력 정보를 확인해 주세요.';
      }
    }

    showToast(errorMessage);
  }
};


const handleLogout = () => {
  localStorage.removeItem('authToken');
  isLoggedIn.value = false;
  showMyPage.value = false;
  userData.value = null;
  userName.value = '복복';
  showToast('로그아웃되었습니다.');
};

const handleDeleteAccount = async () => {
  if (!confirm('정말로 회원 탈퇴를 진행하시겠습니까? 모든 데이터가 삭제됩니다.')) {
    return;
  }

  try {
    const token = localStorage.getItem('authToken');
    const deleteUrl = 'http://127.0.0.1:8000/api/v1/user/delete/';

    await axios.delete(deleteUrl, {
      headers: { Authorization: `Token ${token}` }
    });

    localStorage.removeItem('authToken');
    isLoggedIn.value = false;
    showMyPage.value = false;
    userData.value = null;
    userName.value = '복복';
    showToast('회원 탈퇴가 완료되었습니다. 이용해 주셔서 감사합니다.');

  } catch (error) {
    console.error('회원 탈퇴 실패:', error.response?.data || error.message);
    showToast('회원 탈퇴 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.');
  }
};

const handleUpdateComment = async ({ id, content, rating }) => {
  if (!selectedBook.value) return;

  const token = localStorage.getItem('authToken');
  try {
    const response = await axios.patch(
      `http://127.0.0.1:8000/api/books/${selectedBook.value.id}/comments/${id}/`,
      { content: content, rating: rating },
      { headers: { Authorization: `Token ${token}` } }
    );

    const commentIndex = selectedBook.value.comments.findIndex(c => c.id === id);
    if (commentIndex !== -1) {
      selectedBook.value.comments[commentIndex].content = response.data.content;
      selectedBook.value.comments[commentIndex].rating = response.data.rating;
    }
    const newAverage = calculateLocalAverage(selectedBook.value.comments);
    const bookIndex = books.value.findIndex(b => b.id === selectedBook.value.id);
    if (bookIndex !== -1) {
      books.value[bookIndex].rating = newAverage;
    }
    showToast('댓글이 수정되었습니다.');
  } catch (error) {
    console.error('댓글 수정 실패:', error);
    showToast('댓글 수정에 실패했습니다.');
  }
};

// 댓글 삭제 처리 함수 (VoiceComment -> BookDetailPage -> App.vue로 전달된 이벤트 처리)
const handleDeleteComment = async (commentId) => {
  if (!selectedBook.value) return;

  const token = localStorage.getItem('authToken');
  if (!token) {
    showToast('로그인 세션이 만료되었습니다. 다시 로그인해주세요.');
    return;
  }

  try {
    await axios.delete(
      `http://127.0.0.1:8000/api/books/${selectedBook.value.id}/comments/${commentId}/`,
      {
        headers: { Authorization: `Token ${token}` },
      }
    );

    showToast('TOKTOK이 성공적으로 삭제되었습니다.');

    const commentIndex = selectedBook.value.comments.findIndex(c => c.id === commentId);
    if (commentIndex !== -1) {
      selectedBook.value.comments.splice(commentIndex, 1);
    }

    // 3. 전체 책 목록 (books) 데이터 업데이트 (평점 및 댓글 수 갱신)
    const newAverageRating = calculateLocalAverage(selectedBook.value.comments);
    const newCommentCount = selectedBook.value.comments.length;

    const bookIndex = books.value.findIndex(book => book.id === selectedBook.value.id);
    if (bookIndex !== -1) {
      books.value[bookIndex] = {
        ...books.value[bookIndex],
        rating: newAverageRating,
        commentCount: newCommentCount
      };
    }

  } catch (error) {
    console.error('댓글 삭제 실패:', error.response?.data || error.message);
    showToast('댓글 삭제에 실패했습니다. (권한 없음 또는 서버 오류)');
  }
};

const handleUpdateProfile = async (data) => {
  const token = localStorage.getItem('authToken');
  if (!token) {
    showToast("인증 정보가 없습니다. 다시 로그인 해주세요.");
    return false;
  }

  const API_URL = "http://127.0.0.1:8000/api/v1/user/profile/update/";

  try {
    const response = await fetch(API_URL, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Token ${token}`,
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json();
      const errorMessage =
        errorData.nickname?.[0] ||
        errorData.selected_voice?.[0] ||
        "프로필 업데이트에 실패했습니다.";
      throw new Error(errorMessage);
    }

    const updatedProfile = await response.json();

    if (updatedProfile.nickname) {
      userName.value = updatedProfile.nickname;
    }
    if (userProfile.value) {
      Object.assign(userProfile.value, updatedProfile);
    }

    if (data.nickname) {
      showToast("닉네임이 변경되었습니다.");
    } else if (data.selected_voice) {
      showToast("목소리가 변경되었습니다.");
    }

    return true;
  } catch (error) {
    console.error("프로필 업데이트 API 오류:", error);
    showToast(`오류: ${error.message}`);
    return false;
  }
};

const handleUpdateBio = async (newBio) => {
  const success = await handleUpdateProfile({ bio: newBio });
  
  if (success) {
    if (userData.value) {
      userData.value.bio = newBio;
    }
  }
};

const handleMyPageClick = async () => {
    console.log('handleMyPageClick called, isLoggedIn:', isLoggedIn.value);
    if (isLoggedIn.value) {
        await fetchUserProfile();
        showMyPage.value = true;
    } else {
        showLoginPage.value = true;
    }
};

const handleUpdateProfileField = async (fieldData) => {
  const success = await handleUpdateProfile(fieldData);
  
  if (success && userData.value) {
    Object.assign(userData.value, fieldData);
    showToast("정보가 성공적으로 변경되었습니다.");
  }
};

const handleShowSignup = () => {
  showLoginPage.value = false;
  showSignupPage.value = true;
};

const handleShowLogin = () => {
  showSignupPage.value = false;
  showLoginPage.value = true;
};

const isAppLoading = ref(false);

const fetchBooksWithLoading = async () => {
  isAppLoading.value = true;
  
  const delay = new Promise(resolve => setTimeout(resolve, 1000));
  
  try {
    const [response] = await Promise.all([
      axios.get('http://127.0.0.1:8000/api/books/'),
      delay
    ]);
    books.value = response.data;
  } catch (error) {
    console.error('로드 실패:', error);
  } finally {
    isAppLoading.value = false;
  }
};


onMounted(() => {
  fetchBooksWithLoading();
  const token = localStorage.getItem('authToken');
  const hasSeenOnboarding = localStorage.getItem('hasSeenOnboarding');
  if (token) {
    isLoggedIn.value = true; 
    fetchUserData();
    fetchLibraryBooks();
  }else if (!hasSeenOnboarding) {
    showOnboarding.value = true;
  }
  fetchBooks();
});

const handleFinishOnboarding = (mode) => {
  showOnboarding.value = false;
  localStorage.setItem('hasSeenOnboarding', 'true');

  if (mode === 'login') {
    showLoginPage.value = true;
  } else {
    activeTab.value = 'home';
    showLoginPage.value = false;
    showSignupPage.value = false;
  }
};
</script>
<style>
  html {
    overflow-y: scroll;
  }
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