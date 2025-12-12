<template>
  <div class="min-h-screen bg-background">
    <!-- My Page -->
    <MyPage
      v-if="showMyPage"
      :userName="userName"
      @back="showMyPage = false"
      @logout="handleLogout"
      @deleteAccount="handleDeleteAccount"
      @updateProfile="handleUpdateProfile"
    />

    <!-- Signup Page -->
    <SignupPage
      v-else-if="showSignupPage"
      @signup="handleSignup"
      @close="showSignupPage = false"
      @loginClick="handleShowLogin"
    />

    <!-- Login Page -->
    <LoginPage
      v-else-if="showLoginPage"
      @login="handleLogin"
      @close="showLoginPage = false"
      @signupClick="handleShowSignup"
    />

    <!-- Book Detail Page -->
    <template v-else-if="selectedBook">
      <BookDetailPage
        :book="selectedBook"
        :comments="mockComments[selectedBook.id] || []"
        :isLoggedIn="isLoggedIn"
        @back="selectedBook = null"
        @addComment="handleAddComment"
        @loginClick="showLoginPage = true"
      />
      <AddCommentDialog
        :isOpen="showAddCommentDialog"
        @close="showAddCommentDialog = false"
        @submit="handleSubmitComment"
      />
    </template>

    <!-- Main App -->
    <template v-else>
      <HomePage
        v-if="activeTab === 'home'"
        :books="mockBooks"
        @bookClick="handleBookClick"
        @searchClick="isSearchOpen = true"
      />
      <LibraryPage
        v-else-if="activeTab === 'library'"
        :books="isLoggedIn ? mockLibraryBooks : []"
        :isLoggedIn="isLoggedIn"
        @bookClick="handleBookClick"
        @loginClick="showLoginPage = true"
      />
      <ProfilePage
        v-else-if="activeTab === 'profile'"
        :userName="userName"
        :stats="stats"
        :isLoggedIn="isLoggedIn"
        @loginClick="showLoginPage = true"
        @myPageClick="showMyPage = true"
      />

      <BottomNavigation
        :activeTab="activeTab"
        @tabChange="activeTab = $event"
      />

      <SearchDialog
        :isOpen="isSearchOpen"
        :books="mockBooks"
        @close="isSearchOpen = false"
        @bookClick="handleBookClick"
      />
    </template>
  </div>
</template>

<script setup>
import { ref } from "vue";
import HomePage from "./components/HomePage.vue";
import LibraryPage from "./components/LibraryPage.vue";
import ProfilePage from "./components/ProfilePage.vue";
import BookDetailPage from "./components/BookDetailPage.vue";
import LoginPage from "./components/LoginPage.vue";
import SignupPage from "./components/SignupPage.vue";
import MyPage from "./components/MyPage.vue";
import BottomNavigation from "./components/BottomNavigation.vue";
import SearchDialog from "./components/SearchDialog.vue";
import AddCommentDialog from "./components/AddCommentDialog.vue";

const activeTab = ref("home");
const selectedBook = ref(null);
const isSearchOpen = ref(false);
const isLoggedIn = ref(false);
const showLoginPage = ref(false);
const showSignupPage = ref(false);
const showMyPage = ref(false);
const showAddCommentDialog = ref(false);
const userName = ref("독서 애호가");

const stats = {
  booksRead: 24,
  comments: 18,
  averageRating: 8.7,
};

const mockBooks = [
  {
    id: "1",
    title: "달러구트 꿈 백화점",
    author: "이미예",
    category: "판타지",
    cover_url:
      "https://images.unsplash.com/photo-1723220217551-5b5a8a578758?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=400",
    rating: 9.2,
    commentCount: 24,
  },
  {
    id: "2",
    title: "무례한 사람에게 웃으며 대처하는 법",
    author: "정문정",
    category: "자기계발",
    cover_url:
      "https://images.unsplash.com/photo-1660606422784-5a18d4be40fe?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=400",
    rating: 8.8,
    commentCount: 18,
  },
  {
    id: "3",
    title: "트렌드 코리아 2024",
    author: "김난도 외",
    category: "경제/경영",
    cover_url:
      "https://images.unsplash.com/photo-1760120482171-d9d5468f75fd?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=400",
    rating: 8.5,
    commentCount: 12,
  },
  {
    id: "4",
    title: "불편한 편의점",
    author: "김호연",
    category: "소설",
    cover_url:
      "https://images.unsplash.com/photo-1633248382168-031c2a6084e8?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=400",
    rating: 9.5,
    commentCount: 32,
  },
  {
    id: "5",
    title: "1984",
    author: "조지 오웰",
    category: "고전",
    cover_url:
      "https://images.unsplash.com/photo-1723220217551-5b5a8a578758?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=400",
    rating: 9.0,
    commentCount: 28,
  },
  {
    id: "6",
    title: "아몬드",
    author: "손원평",
    category: "소설",
    cover_url:
      "https://images.unsplash.com/photo-1660606422784-5a18d4be40fe?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=400",
    rating: 8.7,
    commentCount: 21,
  },
  {
    id: "7",
    title: "완전한 행복",
    author: "정유정",
    category: "미스터리",
    cover_url:
      "https://images.unsplash.com/photo-1760120482171-d9d5468f75fd?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=400",
    rating: 8.9,
    commentCount: 15,
  },
  {
    id: "8",
    title: "시선으로부터",
    author: "정세랑",
    category: "소설",
    cover_url:
      "https://images.unsplash.com/photo-1633248382168-031c2a6084e8?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=400",
    rating: 8.6,
    commentCount: 19,
  },
];

const mockLibraryBooks = [mockBooks[0], mockBooks[3], mockBooks[4]];

const mockComments = {
  1: [
    {
      id: "c1",
      user_name: "독서왕",
      text: "정말 몽환적이고 아름다운 이야기였어요. 꿈에 대한 새로운 시각을 갖게 되었습니다.",
      voice_url: "mock_url",
      created_at: new Date(Date.now() - 3600000).toISOString(),
      is_mine: false,
      rating: 9,
    },
    {
      id: "c2",
      user_name: "나",
      text: "저도 너무 좋아하는 책입니다! 특히 7층이 인상 깊었어요.",
      voice_url: "mock_url",
      created_at: new Date(Date.now() - 1800000).toISOString(),
      is_mine: true,
      rating: 10,
    },
    {
      id: "c3",
      user_name: "책벌레",
      text: "따뜻하면서도 깊이 있는 메시지가 담겨있네요.",
      voice_url: "mock_url",
      created_at: new Date(Date.now() - 900000).toISOString(),
      is_mine: false,
      rating: 8,
    },
  ],
  4: [
    {
      id: "c4",
      user_name: "책읽는사람",
      text: "현대 사회의 외로움과 연대에 대해 생각하게 만드는 소설이에요.",
      voice_url: "mock_url",
      created_at: new Date(Date.now() - 7200000).toISOString(),
      is_mine: false,
      rating: 9,
    },
  ],
};

const handleBookClick = (book) => {
  selectedBook.value = book;
};

const handleAddComment = () => {
  if (!isLoggedIn.value) {
    showLoginPage.value = true;
    return;
  }
  showAddCommentDialog.value = true;
};

const handleSubmitComment = ({ text, isVoice, rating }) => {
  console.log("New comment:", { text, isVoice, rating });
  alert(
    `${
      isVoice ? "음성" : "텍스트"
    } TOKTOK이 등록되었습니다!\n평점: ${rating}/10`
  );
  showAddCommentDialog.value = false;
};

// const handleLogin = ({ email, password }) => {
//   isLoggedIn.value = true;
//   showLoginPage.value = false;
// };

const handleLogin = async ({ email, password }) => {
  const API_URL = "http://127.0.0.1:8000/api/v1/user/login/";

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: email,
        password: password,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      let errorMessage =
        errorData.non_field_errors?.[0] ||
        errorData.detail ||
        "로그인에 실패했습니다. 이메일과 비밀번호를 확인해주세요.";

      throw new Error(errorMessage);
    }

    const userData = await response.json();

    const loggedInUserName = userData.user_name;

    isLoggedIn.value = true;
    userName.value = loggedInUserName;
    showLoginPage.value = false;
    alert(`${userName.value}님, 환영합니다!`);
  } catch (error) {
    console.error("로그인 API 호출 오류:", error);
    alert(`로그인 오류: ${error.message}`);
  }
};

// const handleSignup = ({ email, password, name }) => {
//   console.log('Signup:', { email, name });
//   isLoggedIn.value = true;
//   userName.value = name;
//   showSignupPage.value = false;
//   alert(`${name}님, 회원가입이 완료되었습니다!`);
// };

const handleSignup = async (
  email,
  password,
  name,
  voice,
  favoriteBook,
  category
) => {
  console.log("Sending Signup Data:", { email, name, category });
  const API_URL = "http://127.0.0.1:8000/api/v1/user/signup/";

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: email,
        name: name,
        password: password,
        password_confirm: password,
        selected_voice: voice,
        favorite_book: favoriteBook,
        selected_category: category,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();

      let errorMessage = "회원가입에 실패했습니다. 알 수 없는 오류입니다.";

      if (errorData.email) {
        errorMessage = `이메일 오류: ${errorData.email[0]}`;
      } else if (errorData.name) {
        errorMessage = `닉네임 오류: ${errorData.name[0]}`;
      } else if (errorData.password_confirm) {
        errorMessage = `${errorData.password_confirm[0]}`;
      } else if (errorData.detail) {
        errorMessage = errorData.detail; // DRF 일반 오류
      }

      throw new Error(errorMessage);
    }

    const userData = await response.json(); 

    isLoggedIn.value = true;
    userName.value = name;
    showSignupPage.value = false;
    alert(
      `${name}님, 회원가입이 완료되었습니다! 이제 BOOKBOOK을 시작할 수 있습니다.`
    );
  } catch (error) {
    console.error("회원가입 API 호출 오류:", error);
    alert(`회원가입 중 오류가 발생했습니다: ${error.message}`);
  }
};

const handleLogout = () => {
  isLoggedIn.value = false;
  showMyPage.value = false;
};

const handleDeleteAccount = () => {
  isLoggedIn.value = false;
  showMyPage.value = false;
  alert("회원 탈퇴가 완료되었습니다.");
};

const handleUpdateProfile = (name) => {
  userName.value = name;
};

const handleShowSignup = () => {
  showLoginPage.value = false;
  showSignupPage.value = true;
};

const handleShowLogin = () => {
  showSignupPage.value = false;
  showLoginPage.value = true;
};
</script>
