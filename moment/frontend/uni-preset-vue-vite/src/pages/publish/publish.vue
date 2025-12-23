<template>
  <view class="publish-container">
    <!-- 自定义导航栏 -->
    <view class="custom-navbar">
      <view class="navbar-content">
        <text class="navbar-back" @tap="handleCancel">取消</text>
        <text class="navbar-title">发动态</text>
        <text class="navbar-placeholder"></text>
      </view>
    </view>

    <scroll-view scroll-y class="content-scroll">
      <!-- 文字编辑区域 -->
      <view class="editor-section">
        <textarea
          class="text-editor"
          v-model="content"
          placeholder="分享你的生活..."
          :maxlength="500"
          :auto-height="true"
          :show-confirm-bar="false"
        />
        <text class="char-count">{{ content.length }}/500</text>
      </view>

      <!-- 标签区域 -->
      <view class="tag-section">
        <view class="tag-header">
          <text class="tag-title">标签</text>
          <text class="tag-add-btn" @tap="showTagSelector">+ 添加标签</text>
        </view>
        <view class="selected-tags" v-if="selectedTags.length > 0">
          <view class="tag-item" v-for="(tag, index) in selectedTags" :key="index">
            <text class="tag-text">{{ tag }}</text>
            <text class="tag-remove" @tap="removeTag(index)">×</text>
          </view>
        </view>
        <view class="no-tags" v-else>
          <text class="no-tags-text">未添加标签</text>
        </view>
      </view>

      <!-- 媒体预览区域 -->
      <view class="media-section" v-if="images.length > 0 || video">
        <!-- 图片预览 -->
        <view class="media-grid" v-if="images.length > 0">
          <view class="media-item" v-for="(img, index) in images" :key="index">
            <image class="media-preview" :src="img" mode="aspectFill" @tap="previewImage(index)" />
            <text class="media-delete" @tap="removeImage(index)">×</text>
          </view>
        </view>

        <!-- 视频预览 -->
        <view class="video-preview" v-if="video">
          <video
            class="video-player"
            :src="video"
            :poster="videoPoster"
            controls
            object-fit="cover"
          />
          <text class="media-delete video-delete" @tap="removeVideo">×</text>
        </view>
      </view>

      <!-- 添加媒体按钮 -->
      <view class="action-section">
        <view class="action-btn" @tap="chooseImage">
          <text class="action-icon">📷</text>
          <text class="action-text">照片</text>
        </view>
        <view class="action-btn" @tap="chooseVideo">
          <text class="action-icon">🎬</text>
          <text class="action-text">视频</text>
        </view>
      </view>
    </scroll-view>

    <!-- 底部发布按钮 -->
    <view class="bottom-publish-bar">
      <button 
        class="publish-btn" 
        :class="{ disabled: !canPublish }" 
        @tap="handlePublish"
      >
        发布
      </button>
    </view>

    <!-- 标签选择弹窗 -->
    <view class="tag-modal" v-if="showTagModal" @tap="hideTagSelector">
      <view class="tag-modal-content" @tap.stop>
        <view class="tag-modal-header">
          <text class="tag-modal-title">选择或新建标签</text>
          <text class="tag-modal-close" @tap="hideTagSelector">×</text>
        </view>
        <view class="tag-modal-body">
          <!-- 新建标签输入 -->
          <view class="new-tag-input-wrapper">
            <input
              class="new-tag-input"
              v-model="newTagName"
              placeholder="输入新标签名称"
              :maxlength="10"
              @confirm="createNewTag"
            />
            <button class="create-tag-btn" @tap="createNewTag">创建</button>
          </view>

          <!-- 常用标签列表 -->
          <view class="common-tags-section">
            <text class="common-tags-title">常用标签</text>
            <view class="common-tags-list">
              <view
                class="common-tag-item"
                v-for="(tag, index) in commonTags"
                :key="index"
                :class="{ selected: selectedTags.includes(tag) }"
                @tap="toggleTag(tag)"
              >
                <text class="common-tag-text">{{ tag }}</text>
                <text class="common-tag-check" v-if="selectedTags.includes(tag)">✓</text>
              </view>
            </view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { publishPost } from '../../services/api.js'

export default {
  data() {
    return {
      currentUser: {
        avatar: 'https://picsum.photos/200',
        nickname: '小程序用户'
      },
      content: '',
      images: [],
      video: '',
      videoPoster: '',
      selectedTags: [],
      showTagModal: false,
      newTagName: '',
      commonTags: ['户外', '日常', '美食', '旅行', '运动', '摄影', '读书', '音乐', '电影', '宠物', '工作', '学习']
    }
  },
  computed: {
    canPublish() {
      // 有文字内容，或者有图片/视频就可以发布
      return this.content.trim().length > 0 || this.images.length > 0 || this.video
    }
  },
  onLoad() {
    // 监听个人资料更新
    this.__profileUpdatedHandler = (payload = {}) => {
      const { avatar, nickname } = payload
      if (avatar) this.currentUser.avatar = avatar
      if (nickname) this.currentUser.nickname = nickname
    }
    uni.$on('profileUpdated', this.__profileUpdatedHandler)
  },
  onUnload() {
    if (this.__profileUpdatedHandler) {
      uni.$off('profileUpdated', this.__profileUpdatedHandler)
      this.__profileUpdatedHandler = null
    }
  },
  methods: {
    handleCancel() {
      // 如果有内容，提示确认
      if (this.content.trim() || this.images.length > 0 || this.video) {
        uni.showModal({
          title: '提示',
          content: '确定要放弃此次编辑吗？',
          success: (res) => {
            if (res.confirm) {
              uni.navigateBack()
            }
          }
        })
      } else {
        uni.navigateBack()
      }
    },
    chooseImage() {
      const maxCount = 9 - this.images.length
      if (maxCount <= 0) {
        uni.showToast({ title: '最多只能添加9张图片', icon: 'none' })
        return
      }

      uni.chooseImage({
        count: maxCount,
        sizeType: ['compressed'],
        sourceType: ['album', 'camera'],
        success: (res) => {
          this.images = this.images.concat(res.tempFilePaths)
        },
        fail: (err) => {
          console.error('选择图片失败', err)
          uni.showToast({ title: '选择图片失败', icon: 'none' })
        }
      })
    },
    chooseVideo() {
      if (this.video) {
        uni.showToast({ title: '只能添加一个视频', icon: 'none' })
        return
      }

      uni.chooseVideo({
        sourceType: ['album', 'camera'],
        maxDuration: 60,
        camera: 'back',
        success: (res) => {
          this.video = res.tempFilePath
          this.videoPoster = res.thumbTempFilePath
        },
        fail: (err) => {
          console.error('选择视频失败', err)
          uni.showToast({ title: '选择视频失败', icon: 'none' })
        }
      })
    },
    removeImage(index) {
      this.images.splice(index, 1)
    },
    removeVideo() {
      this.video = ''
      this.videoPoster = ''
    },
    previewImage(index) {
      uni.previewImage({
        current: index,
        urls: this.images
      })
    },
    showTagSelector() {
      this.showTagModal = true
    },
    hideTagSelector() {
      this.showTagModal = false
      this.newTagName = ''
    },
    toggleTag(tag) {
      const index = this.selectedTags.indexOf(tag)
      if (index > -1) {
        // 如果已选中，则取消选择
        this.selectedTags.splice(index, 1)
      } else {
        // 如果未选中，则添加
        if (this.selectedTags.length >= 5) {
          uni.showToast({ title: '最多只能添加5个标签', icon: 'none' })
          return
        }
        this.selectedTags.push(tag)
      }
    },
    createNewTag() {
      const tagName = this.newTagName.trim()
      if (!tagName) {
        uni.showToast({ title: '请输入标签名称', icon: 'none' })
        return
      }
      if (tagName.length > 10) {
        uni.showToast({ title: '标签名称不能超过10个字符', icon: 'none' })
        return
      }
      if (this.selectedTags.includes(tagName)) {
        uni.showToast({ title: '该标签已添加', icon: 'none' })
        return
      }
      if (this.selectedTags.length >= 5) {
        uni.showToast({ title: '最多只能添加5个标签', icon: 'none' })
        return
      }
      // 添加新标签到已选列表
      this.selectedTags.push(tagName)
      // 如果不在常用标签列表中，添加到常用标签
      if (!this.commonTags.includes(tagName)) {
        this.commonTags.unshift(tagName)
        // 限制常用标签数量
        if (this.commonTags.length > 20) {
          this.commonTags = this.commonTags.slice(0, 20)
        }
      }
      this.newTagName = ''
      uni.showToast({ title: '标签添加成功', icon: 'success' })
    },
    removeTag(index) {
      this.selectedTags.splice(index, 1)
    },
    async handlePublish() {
      if (!this.canPublish) {
        uni.showToast({ title: '请输入内容或添加图片/视频', icon: 'none' })
        return
      }

      // 显示发布中状态
      uni.showLoading({ title: '发布中...', mask: true })

      try {
        // 构建发布数据
        const publishData = {
          content: this.content.trim(),
          images: this.images,
          video: this.video,
<<<<<<< HEAD
          tags: this.selectedTags
        }

        // 调用实际的API上传接口
        const response = await publishPost(publishData)
        console.log('发布成功:', response)

        // 格式化时间显示
        const formatTime = (timestamp) => {
          const now = Date.now()
          const diff = now - timestamp
          const minutes = Math.floor(diff / 60000)
          if (minutes < 1) return '刚刚'
          if (minutes < 60) return `${minutes}分钟前`
          const hours = Math.floor(minutes / 60)
          if (hours < 24) return `${hours}小时前`
          const days = Math.floor(hours / 24)
          if (days < 7) return `${days}天前`
          return new Date(timestamp).toLocaleDateString()
        }

<<<<<<< HEAD
        // 从响应中提取帖子数据
        const postData = response.data || response
        
        // 构建新帖子数据（用于添加到首页）
        const newPost = {
          id: postData.id,
          name: this.currentUser.nickname || '我',
          avatar: this.currentUser.avatar || 'https://picsum.photos/200',
          isMine: true,
          time: formatTime(Date.now()),
          text: postData.text,
          type: postData.type,
          media: postData.media,
          poster: this.videoPoster || '',
          tag: postData.tags?.length > 0 ? postData.tags[0] : '',
          tags: postData.tags || [],
          likes: postData.likes_count,
          comments: postData.comments_count,
          liked: false
        }

        // 构建我的动态数据
        const myPost = {
<<<<<<< HEAD
          id: postData.id,
          time: formatTime(Date.now()),
          text: postData.text,
          type: postData.type,
          media: postData.media,
          avatar: this.currentUser.avatar || 'https://picsum.photos/200',
          name: this.currentUser.nickname || '我',
          poster: this.videoPoster || '',
          isMine: true
        }

        // 通过事件总线通知首页更新
        uni.$emit('newPostPublished', {
          discoverPost: newPost,
          myPost: myPost
        })
<<<<<<< HEAD
        // 通知我的页面刷新数据
        uni.$emit('refreshMyPosts')

        uni.hideLoading()
        uni.showToast({ title: '发布成功', icon: 'success' })

        // 延迟返回，让用户看到成功提示
        setTimeout(() => {
          uni.navigateBack()
        }, 1500)
      } catch (error) {
        uni.hideLoading()
        uni.showToast({ title: '发布失败，请重试', icon: 'none' })
        console.error('发布失败', error)
      }
    }
  }
}
</script>

<style scoped>
.publish-container {
  min-height: 100vh;
  background: #f5f7fb;
  display: flex;
  flex-direction: column;
}

/* 自定义导航栏 */
.custom-navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: #fff;
  border-bottom: 1rpx solid #eee;
}

.navbar-content {
  height: 88rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 30rpx;
  padding-top: var(--status-bar-height, 44rpx);
}

.navbar-back {
  font-size: 30rpx;
  color: #333;
  padding: 10rpx 0;
}

.navbar-title {
  font-size: 36rpx;
  font-weight: 700;
  color: #333;
}

.navbar-placeholder {
  width: 60rpx;
}

.content-scroll {
  flex: 1;
  margin-top: calc(var(--status-bar-height, 44rpx) + 88rpx);
  margin-bottom: 120rpx;
  padding: 30rpx;
}

/* 文字编辑区域 */
.editor-section {
  background: #fff;
  border-radius: 24rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 10rpx 30rpx rgba(0, 0, 0, 0.05);
}

.text-editor {
  width: 100%;
  min-height: 300rpx;
  font-size: 32rpx;
  line-height: 1.8;
  color: #333;
}

.char-count {
  display: block;
  text-align: right;
  margin-top: 20rpx;
  font-size: 24rpx;
  color: #999;
}

/* 标签区域 */
.tag-section {
  background: #fff;
  border-radius: 24rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 10rpx 30rpx rgba(0, 0, 0, 0.05);
}

.tag-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20rpx;
}

.tag-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
}

.tag-add-btn {
  font-size: 28rpx;
  color: #667eea;
  padding: 8rpx 16rpx;
  border: 1rpx solid #667eea;
  border-radius: 999rpx;
}

.selected-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.tag-item {
  display: inline-flex;
  align-items: center;
  padding: 12rpx 20rpx;
  background: rgba(102, 126, 234, 0.12);
  border-radius: 999rpx;
  gap: 8rpx;
}

.tag-text {
  font-size: 26rpx;
  color: #667eea;
}

.tag-remove {
  font-size: 28rpx;
  color: #667eea;
  width: 32rpx;
  height: 32rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(102, 126, 234, 0.2);
  line-height: 1;
}

.no-tags {
  padding: 20rpx 0;
}

.no-tags-text {
  font-size: 26rpx;
  color: #999;
}

/* 标签选择弹窗 */
.tag-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 200;
  display: flex;
  align-items: flex-end;
}

.tag-modal-content {
  width: 100%;
  max-height: 80vh;
  background: #fff;
  border-radius: 40rpx 40rpx 0 0;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    transform: translateY(100%);
  }
  to {
    transform: translateY(0);
  }
}

.tag-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 30rpx;
  border-bottom: 1rpx solid #eee;
}

.tag-modal-title {
  font-size: 36rpx;
  font-weight: 700;
  color: #333;
}

.tag-modal-close {
  font-size: 48rpx;
  color: #999;
  width: 60rpx;
  height: 60rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #f5f5f5;
  line-height: 1;
}

.tag-modal-body {
  flex: 1;
  padding: 30rpx;
  overflow-y: auto;
}

.new-tag-input-wrapper {
  display: flex;
  gap: 16rpx;
  margin-bottom: 40rpx;
  padding-bottom: 30rpx;
  border-bottom: 1rpx solid #eee;
}

.new-tag-input {
  flex: 1;
  height: 80rpx;
  padding: 0 24rpx;
  background: #f5f7fb;
  border-radius: 999rpx;
  font-size: 28rpx;
  color: #333;
}

.create-tag-btn {
  height: 80rpx;
  padding: 0 32rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  font-size: 28rpx;
  border-radius: 999rpx;
  border: none;
  white-space: nowrap;
}

.common-tags-section {
  margin-top: 20rpx;
}

.common-tags-title {
  display: block;
  font-size: 28rpx;
  font-weight: 600;
  color: #666;
  margin-bottom: 20rpx;
}

.common-tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.common-tag-item {
  display: inline-flex;
  align-items: center;
  padding: 16rpx 24rpx;
  background: #f5f7fb;
  border-radius: 999rpx;
  border: 2rpx solid transparent;
  gap: 8rpx;
  transition: all 0.2s;
}

.common-tag-item.selected {
  background: rgba(102, 126, 234, 0.12);
  border-color: #667eea;
}

.common-tag-text {
  font-size: 28rpx;
  color: #333;
}

.common-tag-item.selected .common-tag-text {
  color: #667eea;
}

.common-tag-check {
  font-size: 24rpx;
  color: #667eea;
  font-weight: 700;
}

/* 媒体预览区域 */
.media-section {
  background: #fff;
  border-radius: 24rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 10rpx 30rpx rgba(0, 0, 0, 0.05);
}

.media-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20rpx;
  margin-bottom: 20rpx;
}

.media-item {
  position: relative;
  width: 100%;
  aspect-ratio: 1;
  border-radius: 16rpx;
  overflow: hidden;
}

.media-preview {
  width: 100%;
  height: 100%;
  background: #f2f2f2;
}

.media-delete {
  position: absolute;
  top: 10rpx;
  right: 10rpx;
  width: 48rpx;
  height: 48rpx;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
  font-weight: 300;
  line-height: 1;
}

.video-preview {
  position: relative;
  width: 100%;
  border-radius: 16rpx;
  overflow: hidden;
  background: #000;
}

.video-player {
  width: 100%;
  height: 400rpx;
}

.video-delete {
  top: 20rpx;
  right: 20rpx;
}

/* 操作按钮区域 */
.action-section {
  display: flex;
  gap: 20rpx;
  padding: 0 10rpx;
}

.action-btn {
  flex: 1;
  background: #fff;
  border-radius: 24rpx;
  padding: 30rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
  box-shadow: 0 10rpx 30rpx rgba(0, 0, 0, 0.05);
  transition: transform 0.2s;
}

.action-btn:active {
  transform: scale(0.98);
}

.action-icon {
  font-size: 48rpx;
}

.action-text {
  font-size: 28rpx;
  color: #666;
}

/* 底部发布按钮 */
.bottom-publish-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: #fff;
  border-top: 1rpx solid #eee;
  padding: 20rpx 30rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.publish-btn {
  width: 100%;
  height: 88rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  font-size: 32rpx;
  font-weight: 600;
  border-radius: 999rpx;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10rpx 30rpx rgba(102, 126, 234, 0.3);
  transition: all 0.2s;
}

.publish-btn:active {
  transform: scale(0.98);
  opacity: 0.9;
}

.publish-btn.disabled {
  background: #e0e0e0;
  color: #999;
  box-shadow: none;
}
</style>

