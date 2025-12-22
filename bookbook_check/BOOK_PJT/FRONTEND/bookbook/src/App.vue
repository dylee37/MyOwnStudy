<template>
  <div class="min-h-screen bg-background">
    <MyPage v-if="showMyPage" :userName="userName" :profileData="userProfile" @back="showMyPage = false" @logout="handleLogout"
      @deleteAccount="handleDeleteAccount" @updateProfile="handleUpdateProfile" />

    <SignupPage v-else-if="showSignupPage" @signup="handleSignup" @close="showSignupPage = false"
      @loginClick="handleShowLogin" />

    <LoginPage v-else-if="showLoginPage" @login="handleLogin" @close="showLoginPage = false"
      @signupClick="handleShowSignup" />

    <template v-else-if="selectedBook">
      <BookDetailPage 
        :book="selectedBook" 
        :comments="selectedBook.comments || []" 
        :isLoggedIn="isLoggedIn"
        :currentUserId="userData?.id" @back="selectedBook = null" 
        @addComment="handleAddComment" 
        @loginClick="showLoginPage = true"
        @deleteComment="handleDeleteComment" 
      />
      <AddCommentDialog :isOpen="showAddCommentDialog" @close="showAddCommentDialog = false"
        @submit="handleSubmitComment" />
    </template>

    <template v-else>
      <HomePage v-if="activeTab === 'home'" @bookClick="handleBookClick" @searchClick="isSearchOpen = true" />
      <LibraryPage v-else-if="activeTab === 'library'" :books="isLoggedIn ? libraryBooks : []" :isLoggedIn="isLoggedIn"
        @bookClick="handleBookClick" @loginClick="showLoginPage = true" />
      <ProfilePage v-else-if="activeTab === 'profile'" :userName="userName" :stats="stats" :isLoggedIn="isLoggedIn"
        :userData="userData" @loginClick="showLoginPage = true" @myPageClick="handleMyPageClick" @updateBio="handleUpdateBio" @updateProfileField="handleUpdateProfileField"/>
      <SearchDialog :isOpen="isSearchOpen" :books="books" @close="isSearchOpen = false" @bookClick="handleBookClick" />

      <BottomNavigation :activeTab="activeTab" @tabChange="activeTab = $event" />
      <SearchDialog
        :isOpen="isSearchOpen"
        :books="books || []"
        @close="isSearchOpen = false"
        @bookClick="handleBookClick"
      />
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, reactive } from 'vue';
import { useStore } from 'vuex'

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

const store = useStore()

const stats = reactive({
  booksRead: 0,
  comments: 0,
  averageRating: 0.0
});


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

// 헬퍼 함수: 평균 평점 계산 (5점 만점 기준)
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
    alert('로그인 세션이 만료되었습니다. 다시 로그인해주세요.');
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

    alert(`${isVoice ? '음성' : '텍스트'} TOKTOK이 성공적으로 등록되었습니다!`);

    if (selectedBook.value.comments) {
      selectedBook.value.comments.unshift(response.data); 
    } else {
      selectedBook.value.comments = [response.data];
    }


    const newAverageRating = calculateLocalAverage(selectedBook.value.comments);
    const newCommentCount = selectedBook.value.comments.length;

    const bookIndex = books.value.findIndex(book => book.id === selectedBook.value.id);
    if (bookIndex !== -1) {
      // 10점 만점 기준으로 저장 (책 목록 평점 표기 기준)
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

    alert(errorMessage);
  }
};

const fetchUserProfile = async () => {
  const token = localStorage.getItem('authToken');
  if (!token) {
    // 토큰 없으면 로딩 불가
    return;
  }

  const API_URL = "http://127.0.0.1:8000/api/v1/user/profile/update/";

  try {
    const response = await fetch(API_URL, {
      method: "GET", // GET 요청으로 프로필 조회
      headers: {
        Authorization: `Token ${token}`,
      },
    });

    if (response.ok) {
      const data = await response.json();
      userProfile.value = data; // 🚨 프로필 데이터 저장
      // 닉네임도 최신 정보로 업데이트
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

    isLoggedIn.value = true;
    showLoginPage.value = false;
    activeTab.value = 'home';

    await Promise.all([
      fetchUserData(), 
      fetchLibraryBooks() 
    ]);

    alert(`로그인 성공! ${userName.value}님 환영합니다.`);

  } catch (error) {
    console.error('로그인 실패:', error.response?.data || error.message);
    alert('로그인 실패: 이메일 또는 비밀번호를 확인해주세요.');
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
      alert('회원가입 성공! 이제 로그인해주세요.');
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

    alert(errorMessage);
  }
};


const handleLogout = () => {
  localStorage.removeItem('authToken');
  isLoggedIn.value = false;
  showMyPage.value = false;
  userData.value = null;
  userName.value = '복복';
  alert('로그아웃되었습니다.');
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
    alert('회원 탈퇴가 완료되었습니다. 이용해 주셔서 감사합니다.');

  } catch (error) {
    console.error('회원 탈퇴 실패:', error.response?.data || error.message);
    alert('회원 탈퇴 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.');
  }
};


// 댓글 삭제 처리 함수 (VoiceComment -> BookDetailPage -> App.vue로 전달된 이벤트 처리)
const handleDeleteComment = async (commentId) => {
  if (!selectedBook.value) return;

  const token = localStorage.getItem('authToken');
  if (!token) {
    alert('로그인 세션이 만료되었습니다. 다시 로그인해주세요.');
    return;
  }

  try {
    await axios.delete(
      `http://127.0.0.1:8000/api/books/${selectedBook.value.id}/comments/${commentId}/`,
      {
        headers: { Authorization: `Token ${token}` },
      }
    );

    alert('TOKTOK이 성공적으로 삭제되었습니다.');

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
        rating: newAverageRating, // 10점 만점 기준으로 저장
        commentCount: newCommentCount
      };
    }

  } catch (error) {
    console.error('댓글 삭제 실패:', error.response?.data || error.message);
    alert('댓글 삭제에 실패했습니다. (권한 없음 또는 서버 오류)');
  }
};


// const handleUpdateProfile = (newNickname) => {
//   if (userData.value) {
//     userData.value.nickname = newNickname; 
//   }
//   userName.value = newNickname;
//   alert(`닉네임이 ${newNickname}(으)로 변경되었습니다.`);
// };

const handleUpdateProfile = async (data) => {
  const token = localStorage.getItem('authToken');
  if (!token) {
    alert("인증 정보가 없습니다. 다시 로그인 해주세요.");
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

    // 로컬 상태 업데이트
    if (updatedProfile.nickname) {
      userName.value = updatedProfile.nickname;
    }
    if (userProfile.value) {
      // userProfile.value 객체에 최신 데이터를 병합
      Object.assign(userProfile.value, updatedProfile);
    }
    
    // 변경된 필드에 따라 다른 알림 표시
    if (data.nickname) {
      alert("닉네임이 변경되었습니다.");
    } else if (data.selected_voice) {
      alert("목소리가 변경되었습니다.");
    }

    return true; // 성공 반환
  } catch (error) {
    console.error("프로필 업데이트 API 오류:", error);
    alert(`오류: ${error.message}`);
    return false; // 실패 반환
  }
};

const handleUpdateBio = async (newBio) => {
  // 백엔드 API에 bio 필드를 PATCH 요청 보냄
  // 기존 handleUpdateProfile 함수가 { bio: "내용" } 객체를 인자로 받음
  const success = await handleUpdateProfile({ bio: newBio });
  
  if (success) {
    // 서버 저장에 성공하면 로컬 화면 데이터도 즉시 업데이트
    if (userData.value) {
      userData.value.bio = newBio;
    }
    // alert("소개가 업데이트되었습니다."); // handleUpdateProfile 내부에 이미 alert 로직이 있다면 생략 가능
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
  // fieldData는 { favorite_book: '...' } 또는 { selected_category: '...' } 형태
  const success = await handleUpdateProfile(fieldData);
  
  if (success && userData.value) {
    // 성공 시 로컬의 userData를 갱신
    Object.assign(userData.value, fieldData);
    alert("정보가 성공적으로 변경되었습니다.");
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


// onMounted 수정: 토큰이 있을 경우 데이터 로드 시도
onMounted(() => {
  const token = localStorage.getItem('authToken');
  if (token) {
    isLoggedIn.value = true; 
    fetchUserData();
    fetchLibraryBooks();
  }
  fetchBooks();
});
</script>