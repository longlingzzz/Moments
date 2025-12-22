<template>
  <view class="page">
    <view class="loading">正在跳转...</view>
  </view>
</template>

<script>
export default {
  onLoad() {
    // 登录态检查：无 token 则跳登录，有 token 进首页
    const token = uni.getStorageSync('auth_token')
    if (!token) {
      uni.reLaunch({
        url: '/pages/login/login'
      })
      return
    }
    uni.switchTab({
      url: '/pages/discover/discover'
    })
  }
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f5f7fb;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading {
  color: #999;
  font-size: 28rpx;
}
</style>