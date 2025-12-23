<template>
  <view class="register-container" :style="{ paddingTop: statusBarHeight + 'px' }">
    <!-- Logo区域 -->
    <view class="logo-section">
      <view class="logo-circle">
        <text class="logo-icon">✨</text>
      </view>
      <text class="title">创建账户</text>
      <text class="subtitle">填写信息完成注册</text>
    </view>

    <!-- 成功提示 -->
    <view class="success-message" v-if="showSuccess">注册成功！</view>

    <!-- 注册表单 -->
    <scroll-view class="form-scroll" scroll-y>
      <view class="form-container">
        <view class="form-group" :class="{ error: errors.nickname }">
          <text class="label">昵称</text>
          <view class="input-wrapper">
            <input 
              type="text" 
              v-model="formData.nickname"
              class="form-input" 
              placeholder="请输入昵称（2-20个字符）"
            placeholder-style="color:#b2b2b2;"
              @blur="validateNickname"
              @input="clearError('nickname')"
            />
            <text class="input-icon">✏️</text>
          </view>
          <text class="error-message" v-if="errors.nickname">{{ errors.nickname }}</text>
        </view>

        <view class="form-group" :class="{ error: errors.password }">
          <text class="label">密码</text>
          <view class="input-wrapper">
            <input 
            type="text"
            :password="!showPassword"
              v-model="formData.password"
              class="form-input" 
              placeholder="请输入密码（至少6位）"
            placeholder-style="color:#b2b2b2;"
              @blur="validatePassword"
              @input="onPasswordInput"
            />
            <text class="toggle-password" @click="togglePassword('password')">
              {{ showPassword ? '🙈' : '👁️' }}
            </text>
          </view>
          <view class="password-strength" v-if="formData.password.length > 0">
            <view class="strength-bar">
              <view class="strength-fill" :class="passwordStrengthClass"></view>
            </view>
            <text class="strength-text">密码强度：{{ passwordStrengthText }}</text>
          </view>
          <text class="error-message" v-if="errors.password">{{ errors.password }}</text>
        </view>

        <view class="form-group" :class="{ error: errors.confirmPassword }">
          <text class="label">确认密码</text>
          <view class="input-wrapper">
            <input 
            type="text"
            :password="!showConfirmPassword"
              v-model="formData.confirmPassword"
              class="form-input" 
              placeholder="请再次输入密码"
            placeholder-style="color:#b2b2b2;"
              @blur="validateConfirmPassword"
              @input="clearError('confirmPassword')"
            />
            <text class="toggle-password" @click="togglePassword('confirmPassword')">
              {{ showConfirmPassword ? '🙈' : '👁️' }}
            </text>
          </view>
          <text class="error-message" v-if="errors.confirmPassword">{{ errors.confirmPassword }}</text>
        </view>

        <view class="form-group" :class="{ error: errors.gender }">
          <text class="label">性别</text>
          <view class="gender-group">
            <view 
              class="gender-option" 
              :class="{ active: formData.gender === 'male' }"
              @click="selectGender('male')"
            >
              <text class="gender-icon">{{ formData.gender === 'male' ? '🔘' : '⚪' }}</text>
              <text>男</text>
            </view>
            <view 
              class="gender-option" 
              :class="{ active: formData.gender === 'female' }"
              @click="selectGender('female')"
            >
              <text class="gender-icon">{{ formData.gender === 'female' ? '🔘' : '⚪' }}</text>
              <text>女</text>
            </view>
          </view>
          <text class="error-message" v-if="errors.gender">{{ errors.gender }}</text>
        </view>

        <view class="form-group" :class="{ error: errors.age }">
          <text class="label">年龄</text>
          <input 
            type="number" 
            v-model="formData.age"
            class="form-input age-input" 
            placeholder="请输入年龄（18-100岁）"
          placeholder-style="color:#b2b2b2;"
            @blur="validateAge"
            @input="clearError('age')"
          />
          <text class="error-message" v-if="errors.age">{{ errors.age }}</text>
        </view>

        <button 
          class="register-button" 
          :disabled="loading"
          @click="handleRegister"
        >
          <text v-if="loading" class="button-loading">注册中...</text>
          <text v-else>立即注册</text>
        </button>
      </view>
    </scroll-view>

    <!-- 跳转到登录页面 -->
    <view class="login-link">
      <text>已有账户？</text>
      <text class="link" @click="goToLogin">立即登录</text>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      statusBarHeight: 0,
      formData: {
        nickname: '',
        password: '',
        confirmPassword: '',
        gender: '',
        age: ''
      },
      showPassword: false,
      showConfirmPassword: false,
      loading: false,
      showSuccess: false,
      errors: {
        nickname: '',
        password: '',
        confirmPassword: '',
        gender: '',
        age: ''
      }
    }
  },
  computed: {
    passwordStrength() {
      const password = this.formData.password
      if (password.length === 0) return 0
      
      let strength = 0
      if (password.length >= 6) strength++
      if (password.length >= 10) strength++
      if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++
      if (/\d/.test(password)) strength++
      if (/[^a-zA-Z0-9]/.test(password)) strength++
      
      return strength
    },
    passwordStrengthClass() {
      const strength = this.passwordStrength
      if (strength <= 2) return 'weak'
      if (strength <= 3) return 'medium'
      return 'strong'
    },
    passwordStrengthText() {
      const strength = this.passwordStrength
      if (strength <= 2) return '弱'
      if (strength <= 3) return '中'
      return '强'
    }
  },
  onLoad() {
    this.setStatusBar()
  },
  onShow() {
    this.setStatusBar()
  },
  methods: {
    // 切换密码显示/隐藏
    togglePassword(type) {
      if (type === 'password') {
        this.showPassword = !this.showPassword
      } else {
        this.showConfirmPassword = !this.showConfirmPassword
      }
    },
    
    // 选择性别
    selectGender(gender) {
      this.formData.gender = gender
      this.clearError('gender')
    },
    
    // 密码输入
    onPasswordInput() {
      this.clearError('password')
      // 如果确认密码已输入，重新验证
      if (this.formData.confirmPassword) {
        this.validateConfirmPassword()
      }
    },
    
    // 验证昵称
    validateNickname() {
      const nickname = this.formData.nickname.trim()
      if (!nickname) {
        this.errors.nickname = '请输入昵称'
        return false
      }
      if (nickname.length < 2 || nickname.length > 20) {
        this.errors.nickname = '昵称长度应为2-20个字符'
        return false
      }
      this.errors.nickname = ''
      return true
    },
    
    // 验证密码
    validatePassword() {
      const password = this.formData.password
      if (!password) {
        this.errors.password = '请输入密码'
        return false
      }
      if (password.length < 6) {
        this.errors.password = '密码长度至少6位'
        return false
      }
      this.errors.password = ''
      return true
    },
    
    // 验证确认密码
    validateConfirmPassword() {
      const password = this.formData.password
      const confirmPassword = this.formData.confirmPassword
      if (!confirmPassword) {
        this.errors.confirmPassword = '请再次输入密码'
        return false
      }
      if (password !== confirmPassword) {
        this.errors.confirmPassword = '两次输入的密码不一致'
        return false
      }
      this.errors.confirmPassword = ''
      return true
    },
    
    // 验证年龄
    validateAge() {
      const age = parseInt(this.formData.age)
      if (!this.formData.age) {
        this.errors.age = '请输入年龄'
        return false
      }
      if (isNaN(age) || age < 18 || age > 100) {
        this.errors.age = '年龄应在18-100岁之间'
        return false
      }
      this.errors.age = ''
      return true
    },
    
    // 清除错误
    clearError(field) {
      this.errors[field] = ''
    },
    setStatusBar() {
      try {
        const info = uni.getSystemInfoSync()
        this.statusBarHeight = info.statusBarHeight || 0
      } catch (e) {
        this.statusBarHeight = 0
      }
    },
    
    // 表单验证
    validateForm() {
      const nicknameValid = this.validateNickname()
      const passwordValid = this.validatePassword()
      const confirmPasswordValid = this.validateConfirmPassword()
      const ageValid = this.validateAge()
      
      if (!this.formData.gender) {
        this.errors.gender = '请选择性别'
      } else {
        this.errors.gender = ''
      }
      
      return nicknameValid && passwordValid && 
             confirmPasswordValid && ageValid && 
             this.formData.gender
    },
    
    // 处理注册
    handleRegister() {
      if (!this.validateForm()) {
        return
      }
      
      this.loading = true
      
      // 模拟注册请求
      setTimeout(() => {
        this.loading = false
        this.showSuccess = true
        
        // 这里可以添加实际的注册逻辑
        console.log('注册信息:', {
          nickname: this.formData.nickname,
          password: this.formData.password,
          gender: this.formData.gender,
          age: this.formData.age
        })
        
        // 3秒后跳转到登录页面
        setTimeout(() => {
          this.showSuccess = false
          uni.navigateTo({
            url: '/pages/login/login'
          })
        }, 3000)
      }, 1500)
    },
    
    // 跳转到登录页面
    goToLogin() {
      uni.navigateBack()
    }
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  background: #f6f6f6;
  padding: 60rpx 40rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-sizing: border-box;
}

/* Logo区域 */
.logo-section {
  text-align: center;
  margin: 40rpx 0 50rpx;
}

.logo-circle {
  width: 140rpx;
  height: 140rpx;
  background: #07c160;
  border-radius: 50%;
  margin: 0 auto 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 12rpx 30rpx rgba(7, 193, 96, 0.25);
}

.logo-icon {
  font-size: 70rpx;
  color: #fff;
}

.title {
  display: block;
  color: #111;
  font-size: 48rpx;
  font-weight: 600;
  margin-bottom: 10rpx;
}

.subtitle {
  display: block;
  color: #808080;
  font-size: 26rpx;
}

/* 滚动容器 */
.form-scroll {
  width: 100%;
  max-width: 820rpx;
  max-height: calc(100vh - 340rpx);
  flex: 1;
}

/* 表单容器 */
.form-container {
  background: #fff;
  border-radius: 20rpx;
  padding: 50rpx 36rpx;
  box-shadow: 0 12rpx 40rpx rgba(0, 0, 0, 0.06);
  box-sizing: border-box;
}

/* 表单样式 */
.form-group {
  margin-bottom: 32rpx;
  position: relative;
}

.form-group.error .form-input,
.form-group.error .age-input {
  border-color: #fa5151;
  background: #fff7f7;
}

.label {
  display: block;
  color: #333;
  font-size: 28rpx;
  font-weight: 500;
  margin-bottom: 12rpx;
}

.input-wrapper {
  position: relative;
}

.form-input,
.age-input {
  width: 100%;
  height: 88rpx;
  line-height: 88rpx;
  padding: 0 90rpx 0 26rpx;
  border: 2rpx solid #e5e5e5;
  border-radius: 14rpx;
  font-size: 30rpx;
  background: #fafafa;
  color: #111;
  box-sizing: border-box;
}

.form-input:focus,
.age-input:focus {
  border-color: #07c160;
  background: #fff;
  box-shadow: 0 0 0 8rpx rgba(7, 193, 96, 0.12);
}

.input-icon {
  position: absolute;
  right: 24rpx;
  top: 50%;
  transform: translateY(-50%);
  color: #b2b2b2;
  font-size: 34rpx;
}

.toggle-password {
  position: absolute;
  right: 24rpx;
  top: 50%;
  transform: translateY(-50%);
  color: #07c160;
  font-size: 34rpx;
  padding: 12rpx;
  z-index: 10;
}

/* 密码强度 */
.password-strength {
  margin-top: 12rpx;
}

.strength-bar {
  height: 8rpx;
  background: #e5e5e5;
  border-radius: 4rpx;
  overflow: hidden;
  margin-bottom: 10rpx;
}

.strength-fill {
  height: 100%;
  transition: all 0.3s ease;
  border-radius: 4rpx;
}

.strength-fill.weak {
  width: 33%;
  background: #fa5151;
}

.strength-fill.medium {
  width: 66%;
  background: #ffa502;
}

.strength-fill.strong {
  width: 100%;
  background: #07c160;
}

.strength-text {
  font-size: 24rpx;
  color: #999;
}

/* 性别选择 */
.gender-group {
  display: flex;
  gap: 24rpx;
  margin-top: 12rpx;
}

.gender-option {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 26rpx 32rpx;
  border: 2rpx solid #e5e5e5;
  border-radius: 14rpx;
  background: #fafafa;
  font-size: 30rpx;
  color: #555;
  font-weight: 500;
  transition: all 0.2s ease;
}

.gender-option.active {
  border-color: #07c160;
  background: #e9f8f0;
  color: #07c160;
  box-shadow: 0 0 0 8rpx rgba(7, 193, 96, 0.12);
}

.gender-icon {
  margin-right: 14rpx;
  font-size: 34rpx;
}

.link {
  color: #07c160;
  text-decoration: underline;
}

.error-message {
  display: block;
  color: #fa5151;
  font-size: 24rpx;
  margin-top: 8rpx;
}

/* 注册按钮 */
.register-button {
  width: 100%;
  padding: 30rpx;
  background: #07c160;
  color: white;
  border: none;
  border-radius: 16rpx;
  font-size: 32rpx;
  font-weight: 600;
  box-shadow: 0 12rpx 30rpx rgba(7, 193, 96, 0.25);
  transition: opacity 0.2s ease;
}

.register-button:active {
  opacity: 0.86;
}

.register-button[disabled] {
  opacity: 0.6;
}

.button-loading {
  display: inline-block;
}

/* 成功提示 */
.success-message {
  background: #07c160;
  color: white;
  padding: 24rpx;
  border-radius: 14rpx;
  text-align: center;
  margin-bottom: 32rpx;
  width: 100%;
  max-width: 820rpx;
  box-shadow: 0 8rpx 24rpx rgba(7, 193, 96, 0.18);
}

/* 登录链接 */
.login-link {
  text-align: center;
  margin-top: 28rpx;
  color: #808080;
  font-size: 26rpx;
}

.login-link .link {
  color: #07c160;
  font-weight: 600;
  margin-left: 10rpx;
}
</style>
