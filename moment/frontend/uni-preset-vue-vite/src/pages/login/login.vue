<template>
  <view class="login-container" :style="{ paddingTop: topPadding + 'px' }">
    <!-- Logo区域 -->
    <view class="logo-section">
      <view class="logo-circle">
        <text class="logo-icon">👤</text>
      </view>
      <text class="title">欢迎回来</text>
      <text class="subtitle">请登录您的账户</text>
    </view>

    <!-- 成功提示 -->
    <view class="success-message" v-if="showSuccess">登录成功！</view>

    <!-- 登录表单 -->
    <scroll-view class="form-scroll" scroll-y>
      <view class="form-container">
      <view class="form-group" :class="{ error: errors.username }">
        <text class="label">账号</text>
        <view class="input-wrapper">
          <input 
            type="text"
            v-model="formData.username"
            class="form-input" 
            placeholder="请输入账号"
            placeholder-class="input-placeholder"
            placeholder-style="color:#b2b2b2;"
            @blur="validateUsername"
            @input="handleUsernameInput"
            confirm-type="next"
          />
          <text class="input-icon">👤</text>
        </view>
        <text class="error-message" v-if="errors.username">{{ errors.username }}</text>
      </view>

      <view class="form-group" :class="{ error: errors.password }">
        <text class="label">密码</text>
        <view class="input-wrapper">
          <input 
            type="text"
            :password="!showPassword"
            v-model="formData.password"
            class="form-input" 
            placeholder="请输入密码"
            placeholder-class="input-placeholder"
            placeholder-style="color:#b2b2b2;"
            @blur="validatePassword"
            @input="handlePasswordInput"
            confirm-type="done"
          />
          <text class="toggle-password" @tap.stop="togglePassword">
            {{ showPassword ? '🙈' : '👁️' }}
          </text>
        </view>
        <text class="error-message" v-if="errors.password">{{ errors.password }}</text>
      </view>

      <view class="form-options">
        <label class="remember-me">
          <checkbox :checked="formData.rememberMe" @tap="toggleRememberMe" />
          <text>记住密码</text>
        </label>
        <text class="forgot-password" @click="handleForgotPassword">忘记密码？</text>
      </view>

      <button 
        class="login-button" 
        :disabled="loading"
        @click="handleLogin"
      >
        <text v-if="loading" class="button-loading">登录中...</text>
        <text v-else>登录</text>
      </button>
      </view>
    </scroll-view>

    <!-- 跳转到注册页面 -->
    <view class="register-link">
      <text>还没有账户？</text>
      <text class="link" @click="goToRegister">立即注册</text>
    </view>
  </view>
</template>

<script>
import * as api from '../../services/api'

export default {
  data() {
    return {
      statusBarHeight: 0, // 状态栏高度
      capsuleHeight: 0,   // 胶囊高度
      topPadding: 0,      // 页面顶部预留边距
      formData: {
        username: '',
        password: '',
        rememberMe: false
      },
      showPassword: false,
      loading: false,
      showSuccess: false,
      errors: {
        username: '',
        password: ''
      }
    };
  },
  onLoad() {
    this.calculateSafeArea();
    // 页面加载时，可以检查是否有保存的登录信息
    this.loadSavedCredentials();
  },
  onShow() {
    this.calculateSafeArea();
  },
  methods: {
    calculateSafeArea() {
      try {
        const systemInfo = uni.getSystemInfoSync();
        // H5/非微信小程序环境没有 wx 对象，使用安全兜底
        const hasWx = typeof wx !== 'undefined' && wx.getMenuButtonBoundingClientRect;
        const menuButtonInfo = hasWx ? wx.getMenuButtonBoundingClientRect() : null;

        const statusBarHeight = systemInfo.statusBarHeight || 0;
        const capsuleHeight = menuButtonInfo?.height || 32;
        const capsuleTop = menuButtonInfo?.top || statusBarHeight;
        const topPadding = capsuleTop + capsuleHeight + 8;

        this.statusBarHeight = statusBarHeight;
        this.capsuleHeight = capsuleHeight;
        this.topPadding = topPadding;
      } catch (e) {
        console.error('获取胶囊信息失败', e);
      }
    },

    // 切换密码显示/隐藏
    togglePassword() {
      this.showPassword = !this.showPassword;
    },
    
    // 切换记住密码
    toggleRememberMe() {
      this.formData.rememberMe = !this.formData.rememberMe;
    },
    
    // 验证账号
    validateUsername() {
      const name = this.formData.username.trim()
      if (!name) {
        this.errors.username = '请输入账号'
        return false;
      }
      // 最低限制 1 个字符，故不再限制长度
      this.clearError('username')
      return true;
    },
    
    // 验证密码
    validatePassword() {
      if (!this.formData.password) {
        this.errors.password = '请输入密码';
        return false;
      }
      if (this.formData.password.length < 6) {
        this.errors.password = '密码长度至少6位';
        return false;
      }
      this.errors.password = '';
      return true;
    },
    
    // 处理账号输入
    handleUsernameInput(e) {
      this.formData.username = e.detail.value;
      this.clearError('username');
    },
    
    // 处理密码输入
    handlePasswordInput(e) {
      this.formData.password = e.detail.value;
      this.clearError('password');
    },
    
    // 清除错误
    clearError(field) {
      this.errors[field] = '';
    },
    
    // 表单验证
    validateForm() {
      const usernameValid = this.validateUsername();
      const passwordValid = this.validatePassword();
      return usernameValid && passwordValid;
    },
    
    // 处理登录
    async handleLogin() {
      if (!this.validateForm()) {
        return;
      }
      this.loading = true;
      try {
        const res = await api.loginApi({
          username: this.formData.username,
          password: this.formData.password
        });
        // 成功：保存 token
        api.saveToken(res.token);
        // 优先拉取带 profile 的最新用户信息
        try {
          const me = await api.fetchMe();
          uni.setStorageSync('current_user', me || res.user || {});
        } catch (e) {
          uni.setStorageSync('current_user', res.user || {});
        }
        this.showSuccess = true;
        // 记住用户名
        if (this.formData.rememberMe) {
          this.saveCredentials();
        } else {
          uni.removeStorageSync('username');
          uni.removeStorageSync('rememberMe');
        }
        // 跳转首页
        uni.switchTab({ url: '/pages/discover/discover' });
      } catch (err) {
        const msg = err?.data?.error || '登录失败，请检查账号密码';
        uni.showToast({ title: msg, icon: 'none' });
      } finally {
        this.loading = false;
      }
    },
    
    // 保存登录信息
    saveCredentials() {
      try {
        uni.setStorageSync('username', this.formData.username);
        uni.setStorageSync('rememberMe', true);
      } catch (e) {
        console.error('保存登录信息失败', e);
      }
    },
    
    // 加载保存的登录信息
    loadSavedCredentials() {
      try {
        const rememberMe = uni.getStorageSync('rememberMe');
        if (rememberMe) {
          const username = uni.getStorageSync('username');
          if (username) {
            this.formData.username = username;
            this.formData.rememberMe = true;
          }
        }
      } catch (e) {
        console.error('加载登录信息失败', e);
      }
    },
    
    // 忘记密码
    handleForgotPassword() {
      uni.showToast({
        title: '忘记密码功能待实现',
        icon: 'none'
      });
    },
    
    // 跳转到注册页面
    goToRegister() {
      uni.navigateTo({
        url: '/pages/register/register'
      });
    }
  }
};
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40rpx 30rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
}

/* Logo区域 */
.logo-section {
  text-align: center;
  margin-bottom: 70rpx;
}

.logo-circle {
  width: 160rpx;
  height: 160rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  margin: 0 auto 30rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 16rpx 40rpx rgba(102, 126, 234, 0.4);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

.logo-icon {
  font-size: 80rpx;
}

.title {
  display: block;
  color: #333;
  font-size: 56rpx;
  font-weight: 600;
  margin-bottom: 16rpx;
}

.subtitle {
  display: block;
  color: #999;
  font-size: 28rpx;
}

/* 表单容器 */
:global(html),
:global(body) {
  -webkit-user-select: text !important;
  user-select: text !important;
}

:global(input),
:global(textarea) {
  -webkit-user-select: text !important;
  user-select: text !important;
  pointer-events: auto !important;
}

/* 兼容 H5：uni-input 内部真实 input/placeholder 解锁交互 */
:global(.uni-input) {
  pointer-events: auto !important;
}
:global(.uni-input-wrapper) {
  pointer-events: auto !important;
}
:global(.uni-input-input) {
  -webkit-user-select: text !important;
  user-select: text !important;
  pointer-events: auto !important;
  caret-color: #333;
  background: transparent;
  width: 100%;
  height: 100%;
  display: block;
  line-height: inherit;
  border: none;
  outline: none;
}
:global(.uni-input-placeholder),
:global(.input-placeholder) {
  pointer-events: none !important;
  -webkit-user-select: none !important;
  user-select: none !important;
  line-height: inherit;
}

.form-scroll {
  width: 100%;
  max-width: 820rpx;
  max-height: calc(100vh - 340rpx);
  overflow: hidden;
  border-radius: 48rpx;
  padding: 60rpx 40rpx;
  box-shadow: 0 40rpx 120rpx rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  animation: slideUp 0.5s ease-out;
  z-index: 1;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(60rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 表单样式 */
.form-group {
  margin-bottom: 40rpx;
  position: relative;
}

.input-wrapper {
  position: relative;
  pointer-events: auto;
}

.form-group.error .form-input {
  border-color: #ff4757;
}

.label {
  display: block;
  color: #555;
  font-size: 28rpx;
  font-weight: 500;
  margin-bottom: 16rpx;
}

.input-wrapper {
  position: relative;
}

.form-input {
  width: 100%;
  height: 88rpx;
  line-height: 88rpx;
  padding: 0 90rpx 0 30rpx;
  border: 4rpx solid #e0e0e0;
  border-radius: 20rpx;
  font-size: 32rpx;
  transition: all 0.3s ease;
  background: #f8f9fa;
  color: #333;
  box-sizing: border-box;
  pointer-events: auto;
  position: relative;
  z-index: 5;
}

.form-input:focus {
  border-color: #667eea;
  background: #fff;
  box-shadow: 0 0 0 8rpx rgba(102, 126, 234, 0.1);
}

.input-icon {
  position: absolute;
  right: 30rpx;
  top: 50%;
  transform: translateY(-50%);
  color: #999;
  font-size: 36rpx;
  pointer-events: none;
  z-index: 1;
}

.toggle-password {
  position: absolute;
  right: 30rpx;
  top: 50%;
  transform: translateY(-50%);
  color: #999;
  font-size: 36rpx;
  padding: 10rpx;
  z-index: 3;
  pointer-events: auto;
}

.error-message {
  display: block;
  color: #ff4757;
  font-size: 26rpx;
  margin-top: 10rpx;
  animation: shake 0.3s;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-10rpx); }
  75% { transform: translateX(10rpx); }
}

/* 记住密码和忘记密码 */
.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 50rpx;
  font-size: 28rpx;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 16rpx;
  color: #666;
}

.forgot-password {
  color: #667eea;
  font-weight: 500;
}

/* 登录按钮 */
.login-button {
  width: 100%;
  padding: 32rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 24rpx;
  font-size: 32rpx;
  font-weight: 600;
  box-shadow: 0 8rpx 30rpx rgba(102, 126, 234, 0.4);
  transition: all 0.3s ease;
}

.login-button:active {
  transform: translateY(2rpx);
  box-shadow: 0 4rpx 15rpx rgba(102, 126, 234, 0.3);
}

.login-button[disabled] {
  opacity: 0.6;
}

.button-loading {
  display: inline-block;
}

/* 成功提示 */
.success-message {
  background: #2ed573;
  color: white;
  padding: 24rpx;
  border-radius: 16rpx;
  text-align: center;
  margin-bottom: 40rpx;
  animation: slideDown 0.3s;
  width: 100%;
  max-width: 800rpx;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 注册链接 */
.register-link {
  text-align: center;
  margin-top: 30rpx;
  color: rgba(255, 255, 255, 0.9);
  font-size: 28rpx;
}

.register-link .link {
  color: #fff;
  font-weight: 600;
  text-decoration: underline;
  margin-left: 10rpx;
}
</style>
