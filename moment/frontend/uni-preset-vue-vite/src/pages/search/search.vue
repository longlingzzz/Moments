<template>
  <view class="search-page" :style="{ paddingTop: statusBarHeight + 'px' }">
    <!-- 搜索头部 -->
    <view class="search-header">
      <view class="search-input-box">
        <text class="search-icon">🔍</text>
        <input
          class="search-input"
          type="text"
          v-model="searchForm.keyword"
          placeholder="搜索用户昵称、内容关键词"
          confirm-type="search"
          @confirm="performSearch"
          @input="onKeywordInput"
          @focus="onInputFocus"
        />
        <text class="clear-input" v-if="searchForm.keyword" @tap="clearKeyword">✕</text>
      </view>
      <text class="cancel-btn" @tap="goBack">取消</text>
    </view>

    <!-- 搜索建议（输入时显示） -->
    <view class="search-suggestions" v-if="showSuggestions && searchForm.keyword && !hasSearched">
      <view class="suggestion-item" v-for="(item, index) in suggestions" :key="index" @tap="selectSuggestion(item)">
        <text class="suggestion-icon">🔍</text>
        <text class="suggestion-text">{{ item }}</text>
      </view>
    </view>

    <!-- 搜索条件卡片 -->
    <view class="filters-card" v-if="!hasSearched">
      <view class="card-header">
        <text class="card-title">筛选条件</text>
        <text class="filter-count" v-if="hasActiveFilters">{{ activeFilterCount }} 个条件</text>
      </view>

      <!-- 标签选择 -->
      <view class="filter-group">
        <text class="filter-label">标签</text>
        <scroll-view class="tag-scroll" scroll-x>
          <view class="tag-list">
            <view
              class="tag-item"
              :class="{ active: searchForm.tag === tag }"
              v-for="tag in availableTags"
              :key="tag"
              @tap="selectTag(tag)"
            >
              {{ tag }}
            </view>
          </view>
        </scroll-view>
      </view>

      <!-- 日期选择 -->
      <view class="filter-group">
        <text class="filter-label">日期</text>
        <view class="date-container">
          <picker mode="date" :value="searchForm.date" @change="onDateChange">
            <view class="date-picker" :class="{ selected: searchForm.date }">
              <text class="date-icon">📅</text>
              <text class="date-text">{{ searchForm.date || '选择日期' }}</text>
            </view>
          </picker>
          <text class="clear-date-btn" v-if="searchForm.date" @tap="clearDate">清除</text>
        </view>
      </view>
    </view>

    <!-- 操作按钮 -->
    <view class="action-buttons" v-if="!hasSearched">
      <button class="search-action-btn primary" @tap="performSearch" :disabled="!hasActiveFilters && !searchForm.keyword.trim()">
        <text class="btn-icon">🔍</text>
        <text>搜索</text>
      </button>
      <button class="search-action-btn" @tap="resetFilters" v-if="hasActiveFilters">
        <text>重置</text>
      </button>
    </view>

    <!-- 搜索历史 -->
    <view class="history-card" v-if="!hasSearched && searchHistory.length > 0">
      <view class="card-header">
        <text class="card-title">搜索历史</text>
        <text class="clear-history-btn" @tap="clearHistory">清除全部</text>
      </view>
      <view class="history-list">
        <view
          class="history-item"
          v-for="(item, index) in searchHistory"
          :key="index"
          @tap="useHistoryItem(item)"
        >
          <view class="history-content">
            <text class="history-icon">🕐</text>
            <text class="history-text">{{ formatHistoryText(item) }}</text>
          </view>
          <text class="history-delete" @tap.stop="deleteHistoryItem(index)">✕</text>
        </view>
      </view>
    </view>

    <!-- 热门标签 -->
    <view class="hot-tags-card" v-if="!hasSearched">
      <view class="card-header">
        <text class="card-title">热门标签</text>
        <text class="card-subtitle">点击快速搜索</text>
      </view>
      <view class="hot-tags">
        <view
          class="hot-tag"
          v-for="(tag, index) in hotTags"
          :key="tag"
          :style="{ animationDelay: index * 0.1 + 's' }"
          @tap="selectHotTag(tag)"
        >
          <text class="hot-tag-icon">{{ getTagIcon(tag) }}</text>
          <text>{{ tag }}</text>
        </view>
      </view>
    </view>

    <!-- 搜索结果 -->
    <scroll-view class="results-container" scroll-y v-if="hasSearched">
      <view class="results-header">
        <view class="results-info">
          <text class="results-count">找到 <text class="count-number">{{ searchResults.length }}</text> 条结果</text>
          <text class="results-tip" v-if="searchForm.keyword">关键词: "{{ searchForm.keyword }}"</text>
        </view>
        <text class="clear-results-btn" @tap="clearResults">
          <text class="btn-icon">↻</text>
          <text>重新搜索</text>
        </text>
      </view>

      <!-- 空结果 -->
      <view v-if="searchResults.length === 0" class="empty-state">
        <view class="empty-icon-wrapper">
          <text class="empty-icon">🔍</text>
        </view>
        <text class="empty-title">未找到相关内容</text>
        <text class="empty-desc">试试调整搜索条件或使用其他关键词</text>
        <button class="empty-action-btn" @tap="resetFilters">重新搜索</button>
      </view>

      <!-- 结果列表 -->
      <view class="results-list">
        <view 
          class="post-card" 
          v-for="(item, index) in searchResults" 
          :key="item.id"
          :style="{ animationDelay: index * 0.05 + 's' }"
        >
          <view class="post-header">
            <image class="avatar" :src="item.avatar" mode="aspectFill" />
            <view class="meta">
              <text class="name">{{ item.name }}</text>
              <text class="time">{{ item.time }}</text>
            </view>
            <text class="tag-badge" v-if="item.tag">{{ item.tag }}</text>
          </view>

          <view class="text-content" v-if="item.text">
            <rich-text :nodes="highlightKeyword(item.text)"></rich-text>
          </view>

          <view class="media-grid" v-if="item.type === 'image' && item.media">
            <image
              v-for="(img, idx) in item.media"
              :key="idx"
              class="media-img"
              :src="img"
              mode="aspectFill"
              @tap="previewImage(item.media, idx)"
            />
          </view>

          <view class="media-video" v-if="item.type === 'video'">
            <video
              :src="item.media"
              :poster="item.poster"
              controls
              autoplay="false"
              show-center-play-btn
              object-fit="cover"
            />
          </view>

          <view class="actions-row">
            <view class="action-btn" @tap="toggleLike(item)">
              <text class="action-icon">{{ item.liked ? '❤️' : '🤍' }}</text>
              <text class="action-count">{{ item.likes }}</text>
            </view>
            <view class="action-btn" @tap="handleComment(item)">
              <text class="action-icon">💬</text>
              <text class="action-count">{{ item.comments }}</text>
            </view>
          </view>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      statusBarHeight: 0, // 状态栏高度
      capsuleHeight: 0,   // 胶囊高度
      topPadding: 0,      // 页面顶部预留边距
      searchForm: {
        keyword: '',
        tag: '',
        date: ''
      },
      hasSearched: false,
      showSuggestions: false,
      searchResults: [],
      searchHistory: [],
      availableTags: ['户外', '日常', '美食', '旅行', '摄影', '运动', '学习', '工作'],
      hotTags: ['户外', '美食', '旅行', '摄影', '运动', '学习'],
      allPosts: [],
      suggestions: []
    };
  },
  onLoad() {
    this.calculateSafeArea();
    this.setStatusBar();
    this.loadAllPosts();
    this.loadSearchHistory();
  },
  onShow() {
    this.setStatusBar();
  },
  methods: {
    calculateSafeArea() {
      try {
        const systemInfo = uni.getSystemInfoSync();
        const menuButtonInfo = wx.getMenuButtonBoundingClientRect();

        // 状态栏高度
        const statusBarHeight = systemInfo.statusBarHeight || 0;

        // 胶囊高度和顶部间距
        const capsuleHeight = menuButtonInfo.height || 32;
        const capsuleTop = menuButtonInfo.top || statusBarHeight;

        // 计算顶部预留边距
        const topPadding = capsuleTop + capsuleHeight + 8; // 额外预留 8px 间距

        // 设置数据
        this.statusBarHeight = statusBarHeight;
        this.capsuleHeight = capsuleHeight;
        this.topPadding = topPadding;
      } catch (e) {
        console.error('获取胶囊信息失败', e);
      }
    },
    setStatusBar() {
      try {
        const info = uni.getSystemInfoSync();
        this.statusBarHeight = info.statusBarHeight || 0;
      } catch (e) {
        this.statusBarHeight = 0;
      }
    },
    loadAllPosts() {
      // 示例数据
      this.allPosts = [
        {
          id: 1,
          name: '沐白',
          avatar: 'https://picsum.photos/200?1',
          time: '2分钟前',
          text: '周末徒步，山顶风景太美啦！',
          type: 'image',
          media: [
            'https://picsum.photos/400?2',
            'https://picsum.photos/400?3',
            'https://picsum.photos/400?4'
          ],
          tag: '户外',
          likes: 32,
          comments: 6,
          liked: false
        },
        {
          id: 2,
          name: '阿宁',
          avatar: 'https://picsum.photos/200?5',
          time: '10分钟前',
          text: '简单的日常记录，阳光很好 ☀️',
          type: 'video',
          media: 'https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4',
          poster: 'https://picsum.photos/400?6',
          tag: '日常',
          likes: 18,
          comments: 4,
          liked: true
        },
        {
          id: 3,
          name: '小美',
          avatar: 'https://picsum.photos/200?10',
          time: '1小时前',
          text: '今天做了好吃的红烧肉，太香了！',
          type: 'image',
          media: ['https://picsum.photos/400?20'],
          tag: '美食',
          likes: 25,
          comments: 8,
          liked: false
        },
        {
          id: 4,
          name: '旅行者',
          avatar: 'https://picsum.photos/200?21',
          time: '3小时前',
          text: '云南大理，风景如画',
          type: 'image',
          media: [
            'https://picsum.photos/400?22',
            'https://picsum.photos/400?23'
          ],
          tag: '旅行',
          likes: 45,
          comments: 12,
          liked: true
        },
        {
          id: 5,
          name: '摄影师',
          avatar: 'https://picsum.photos/200?24',
          time: '5小时前',
          text: '今天拍了一组很满意的照片',
          type: 'image',
          media: ['https://picsum.photos/400?25'],
          tag: '摄影',
          likes: 38,
          comments: 5,
          liked: false
        }
      ]
    },
    onKeywordInput(e) {
      const keyword = e.detail.value
      if (keyword.length > 0) {
        this.showSuggestions = true
        this.generateSuggestions(keyword)
      } else {
        this.showSuggestions = false
      }
    },
    onInputFocus() {
      if (this.searchForm.keyword) {
        this.showSuggestions = true
      }
    },
    generateSuggestions(keyword) {
      // 生成搜索建议
      const keywordLower = keyword.toLowerCase()
      const userNames = [...new Set(this.allPosts.map(p => p.name))]
      const suggestions = userNames
        .filter(name => name.toLowerCase().includes(keywordLower))
        .slice(0, 5)
        .map(name => name)
      this.suggestions = suggestions
    },
    selectSuggestion(suggestion) {
      this.searchForm.keyword = suggestion
      this.showSuggestions = false
      this.performSearch()
    },
    clearKeyword() {
      this.searchForm.keyword = ''
      this.showSuggestions = false
    },
    selectTag(tag) {
      this.searchForm.tag = this.searchForm.tag === tag ? '' : tag
    },
    selectHotTag(tag) {
      this.searchForm.tag = tag
      this.performSearch()
    },
    onDateChange(e) {
      this.searchForm.date = e.detail.value
    },
    clearDate() {
      this.searchForm.date = ''
    },
    resetFilters() {
      this.searchForm = {
        keyword: '',
        tag: '',
        date: ''
      }
      this.hasSearched = false
      this.searchResults = []
      this.showSuggestions = false
    },
    performSearch() {
      const { keyword, tag, date } = this.searchForm
      
      if (!keyword.trim() && !tag && !date) {
        uni.showToast({ title: '请输入搜索条件', icon: 'none' })
        return
      }

      this.showSuggestions = false
      
      // 显示加载状态
      uni.showLoading({ title: '搜索中...' })

      // 模拟搜索延迟
      setTimeout(() => {
        let results = [...this.allPosts]

        if (keyword.trim()) {
          const keywordLower = keyword.toLowerCase()
          results = results.filter(post => {
            return (
              post.name.toLowerCase().includes(keywordLower) ||
              (post.text && post.text.toLowerCase().includes(keywordLower))
            )
          })
        }

        if (tag) {
          results = results.filter(post => post.tag === tag)
        }

        if (date) {
          // 日期搜索（简化处理，实际应该根据动态的真实发布时间进行筛选）
          // 这里可以根据 date 字段进行筛选
          // results = results.filter(post => {
          //   const postDate = post.createdAt // 假设有 createdAt 字段
          //   return postDate && postDate.startsWith(date)
          // })
        }

        this.searchResults = results
        this.hasSearched = true

        this.saveSearchHistory({
          keyword: keyword.trim(),
          tag,
          date
        })

        uni.hideLoading()
        uni.showToast({ 
          title: `找到 ${results.length} 条结果`, 
          icon: 'none',
          duration: 1500
        })
      }, 500)
    },
    clearResults() {
      this.hasSearched = false
      this.searchResults = []
      this.showSuggestions = false
    },
    highlightKeyword(text) {
      if (!this.searchForm.keyword || !text) return text
      const keyword = this.searchForm.keyword
      const escapedKeyword = keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
      const regex = new RegExp(`(${escapedKeyword})`, 'gi')
      return text.replace(regex, '<span style="color: #667eea; font-weight: 600;">$1</span>')
    },
    getTagIcon(tag) {
      const icons = {
        '户外': '🏔️',
        '美食': '🍜',
        '旅行': '✈️',
        '摄影': '📷',
        '运动': '🏃',
        '学习': '📚'
      }
      return icons[tag] || '🏷️'
    },
    previewImage(urls, current) {
      uni.previewImage({
        urls: urls,
        current: current
      })
    },
    toggleLike(item) {
      item.liked = !item.liked
      item.likes += item.liked ? 1 : -1
      this.$forceUpdate()
    },
    handleComment(item) {
      uni.navigateBack({
        success: () => {
          uni.$emit('openComment', { postId: item.id })
        }
      })
    },
    handleShare(item) {
      uni.showToast({ title: '分享功能待实现', icon: 'none' })
    },
    goBack() {
      uni.navigateBack()
    },
    formatHistoryText(item) {
      let text = ''
      if (item.keyword) text += item.keyword
      if (item.tag) text += (text ? ' · ' : '') + `#${item.tag}`
      if (item.date) {
        text += (text ? ' · ' : '') + `📅 ${item.date}`
      }
      return text || '综合搜索'
    },
    useHistoryItem(item) {
      this.searchForm = {
        keyword: item.keyword || '',
        tag: item.tag || '',
        date: item.date || ''
      }
      this.performSearch()
    },
    deleteHistoryItem(index) {
      this.searchHistory.splice(index, 1)
      this.saveSearchHistoryToStorage()
    },
    clearHistory() {
      this.searchHistory = []
      this.saveSearchHistoryToStorage()
      uni.showToast({ title: '已清除搜索历史', icon: 'success' })
    },
    saveSearchHistory(searchItem) {
      const exists = this.searchHistory.some(item => 
        item.keyword === searchItem.keyword &&
        item.tag === searchItem.tag &&
        item.date === searchItem.date
      )
      
      if (!exists) {
        this.searchHistory.unshift(searchItem)
        if (this.searchHistory.length > 10) {
          this.searchHistory = this.searchHistory.slice(0, 10)
        }
        this.saveSearchHistoryToStorage()
      }
    },
    saveSearchHistoryToStorage() {
      try {
        uni.setStorageSync('searchHistory', this.searchHistory)
      } catch (e) {
        console.error('保存搜索历史失败', e)
      }
    },
    loadSearchHistory() {
      try {
        const history = uni.getStorageSync('searchHistory')
        if (history && Array.isArray(history)) {
          this.searchHistory = history
        }
      } catch (e) {
        console.error('加载搜索历史失败', e)
      }
    }
  }
}
</script>

<style scoped>
.search-page {
  width: 100%;
  min-height: 100vh;
  background: linear-gradient(180deg, #f8f9ff 0%, #f5f7fb 100%);
  box-sizing: border-box;
  overflow-x: hidden;
}

/* 搜索页面结果容器 */
.results-container {
  flex: 1;
  padding: 24rpx;
  box-sizing: border-box;
  overflow-x: hidden; /* 防止内容溢出 */
}

/* 结果列表 */
.results-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
  width: 100%;
  box-sizing: border-box;
}

/* 结果卡片，复用发现页的 post-card 样式 */
.post-card {
  width: 100%;
  background: #fff;
  border-radius: 24rpx;
  padding: 24rpx;
  box-shadow: 0 10rpx 30rpx rgba(0, 0, 0, 0.05);
  margin-bottom: 24rpx;
  box-sizing: border-box;
  animation: fadeInUp 0.5s ease backwards;
}

.post-header {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
}

.avatar {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  margin-right: 16rpx;
  background: #f2f2f2;
}

.meta {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.name {
  font-size: 30rpx;
  color: #333;
  font-weight: 600;
}

.time {
  font-size: 24rpx;
  color: #999;
}

.tag {
  padding: 8rpx 16rpx;
  border-radius: 999rpx;
  background: rgba(102, 126, 234, 0.12);
  color: #667eea;
  font-size: 22rpx;
}

.text {
  color: #444;
  font-size: 30rpx;
  line-height: 1.6;
  margin-bottom: 16rpx;
}

.media-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10rpx;
  margin-top: 10rpx;
  margin-bottom: 12rpx;
  width: 100%;
  box-sizing: border-box;
}

.media-img {
  width: 100%;
  height: 220rpx;
  border-radius: 16rpx;
  background: #f2f2f2;
  object-fit: cover;
  box-sizing: border-box;
}

.media-video {
  width: 100%;
  box-sizing: border-box;
}

.media-video video {
  width: 100%;
  height: 360rpx;
  border-radius: 16rpx;
  overflow: hidden;
  background: #000;
  box-sizing: border-box;
}

.actions-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 10rpx;
}

.action {
  display: flex;
  align-items: center;
  gap: 8rpx;
  color: #666;
  font-size: 26rpx;
}

.action-text {
  color: #666;
}

/* 搜索头部 */
.search-header {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 24rpx;
  background: #fff;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 100;
  box-sizing: border-box;
}

.search-input-box {
  flex: 1;
  display: flex;
  align-items: center;
  background: #f5f7fb;
  border-radius: 999rpx;
  padding: 18rpx 24rpx;
  gap: 12rpx;
  border: 2rpx solid transparent;
  transition: all 0.3s;
  min-width: 0;
  box-sizing: border-box;
}

.search-input-box:focus-within {
  border-color: #667eea;
  background: #fff;
  box-shadow: 0 0 0 4rpx rgba(102, 126, 234, 0.1);
}

.search-icon {
  font-size: 32rpx;
  color: #999;
}

.search-input {
  flex: 1;
  font-size: 28rpx;
  color: #333;
}

.clear-input {
  font-size: 24rpx;
  color: #999;
  padding: 4rpx 8rpx;
  background: #e0e0e0;
  border-radius: 50%;
  width: 32rpx;
  height: 32rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cancel-btn {
  font-size: 28rpx;
  color: #667eea;
  font-weight: 500;
  padding: 8rpx;
}

/* 搜索建议 */
.search-suggestions {
  background: #fff;
  margin: 0 24rpx 20rpx;
  border-radius: 16rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
  overflow: hidden;
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.suggestion-item {
  display: flex;
  align-items: center;
  padding: 20rpx 24rpx;
  border-bottom: 1rpx solid #f0f0f0;
  gap: 16rpx;
}

.suggestion-item:last-child {
  border-bottom: none;
}

.suggestion-item:active {
  background: #f5f7fb;
}

.suggestion-icon {
  font-size: 28rpx;
  color: #999;
}

.suggestion-text {
  flex: 1;
  font-size: 28rpx;
  color: #333;
}

/* 卡片样式 */
.filters-card,
.history-card,
.hot-tags-card {
  background: #fff;
  margin: 0 24rpx 24rpx;
  border-radius: 24rpx;
  padding: 28rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24rpx;
}

.card-title {
  font-size: 32rpx;
  color: #333;
  font-weight: 700;
}

.card-subtitle {
  font-size: 24rpx;
  color: #999;
}

.filter-count {
  font-size: 24rpx;
  color: #667eea;
  background: rgba(102, 126, 234, 0.1);
  padding: 4rpx 12rpx;
  border-radius: 12rpx;
}

/* 筛选条件 */
.filter-group {
  margin-bottom: 32rpx;
}

.filter-group:last-child {
  margin-bottom: 0;
}

.filter-label {
  display: block;
  font-size: 28rpx;
  color: #666;
  font-weight: 600;
  margin-bottom: 16rpx;
}

.tag-scroll {
  white-space: nowrap;
}

.tag-list {
  display: inline-flex;
  gap: 16rpx;
  padding-right: 24rpx;
}

.tag-item {
  padding: 14rpx 28rpx;
  background: #f5f7fb;
  border-radius: 999rpx;
  font-size: 26rpx;
  color: #666;
  border: 2rpx solid transparent;
  white-space: nowrap;
  transition: all 0.3s;
}

.tag-item.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  font-weight: 600;
  border-color: #667eea;
  box-shadow: 0 4rpx 12rpx rgba(102, 126, 234, 0.3);
  transform: scale(1.05);
}

.date-container {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.date-picker {
  flex: 1;
  display: flex;
  align-items: center;
  padding: 20rpx;
  background: #f5f7fb;
  border-radius: 16rpx;
  gap: 12rpx;
  border: 2rpx solid transparent;
  transition: all 0.3s;
}

.date-picker.selected {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border-color: #667eea;
}

.date-icon {
  font-size: 28rpx;
}

.date-text {
  flex: 1;
  font-size: 28rpx;
  color: #333;
}

.clear-date-btn {
  font-size: 24rpx;
  color: #667eea;
  padding: 12rpx 20rpx;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 12rpx;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: 16rpx;
  padding: 0 24rpx 24rpx;
}

.search-action-btn {
  flex: 1;
  padding: 24rpx;
  background: #f5f7fb;
  color: #666;
  border: none;
  border-radius: 20rpx;
  font-size: 30rpx;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
}

.search-action-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  box-shadow: 0 8rpx 20rpx rgba(102, 126, 234, 0.3);
}

.search-action-btn[disabled] {
  opacity: 0.5;
}

.btn-icon {
  font-size: 28rpx;
}

/* 搜索历史 */
.history-list {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.history-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx;
  background: #f5f7fb;
  border-radius: 16rpx;
  transition: all 0.3s;
}

.history-item:active {
  background: #e8eaf6;
  transform: scale(0.98);
}

.history-content {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.history-icon {
  font-size: 28rpx;
}

.history-text {
  flex: 1;
  font-size: 28rpx;
  color: #333;
}

.history-delete {
  font-size: 24rpx;
  color: #999;
  padding: 8rpx;
  background: #fff;
  border-radius: 50%;
  width: 40rpx;
  height: 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.clear-history-btn {
  font-size: 26rpx;
  color: #999;
}

/* 热门标签 */
.hot-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.hot-tag {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 18rpx 32rpx;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
  border-radius: 999rpx;
  font-size: 28rpx;
  color: #667eea;
  font-weight: 500;
  border: 2rpx solid rgba(102, 126, 234, 0.2);
  transition: all 0.3s;
  animation: fadeInUp 0.5s ease backwards;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.hot-tag:active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-color: #667eea;
  transform: scale(1.05);
  box-shadow: 0 4rpx 12rpx rgba(102, 126, 234, 0.3);
}

.hot-tag-icon {
  font-size: 32rpx;
}

/* 搜索结果 */
.results-container {
  flex: 1;
  padding: 24rpx;
}

.results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24rpx;
  padding: 20rpx;
  background: #fff;
  border-radius: 16rpx;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
}

.results-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.results-count {
  font-size: 28rpx;
  color: #666;
  font-weight: 600;
}

.count-number {
  color: #667eea;
  font-weight: 700;
  font-size: 32rpx;
}

.results-tip {
  font-size: 24rpx;
  color: #999;
}

.clear-results-btn {
  display: flex;
  align-items: center;
  gap: 8rpx;
  font-size: 26rpx;
  color: #667eea;
  padding: 12rpx 20rpx;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 20rpx;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 120rpx 40rpx;
  background: #fff;
  border-radius: 24rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
}

.empty-icon-wrapper {
  width: 160rpx;
  height: 160rpx;
  margin: 0 auto 32rpx;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-icon {
  font-size: 80rpx;
}

.empty-title {
  display: block;
  font-size: 32rpx;
  color: #333;
  font-weight: 600;
  margin-bottom: 16rpx;
}

.empty-desc {
  display: block;
  font-size: 26rpx;
  color: #999;
  margin-bottom: 40rpx;
  line-height: 1.6;
}

.empty-action-btn {
  padding: 20rpx 48rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border: none;
  border-radius: 999rpx;
  font-size: 28rpx;
  font-weight: 600;
}

/* 结果列表 */
.results-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
  width: 100%;
  box-sizing: border-box;
}

.post-card {
  width: 100%;
  background: #fff;
  border-radius: 24rpx;
  padding: 28rpx;
  box-shadow: 0 10rpx 30rpx rgba(0, 0, 0, 0.05);
  animation: fadeInUp 0.5s ease backwards;
  box-sizing: border-box;
}

.post-header {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
}

.avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  margin-right: 20rpx;
  background: #f2f2f2;
}

.meta {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.name {
  font-size: 30rpx;
  color: #333;
  font-weight: 600;
  margin-bottom: 6rpx;
}

.time {
  font-size: 24rpx;
  color: #999;
}

.tag-badge {
  padding: 8rpx 16rpx;
  border-radius: 999rpx;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.12) 0%, rgba(118, 75, 162, 0.12) 100%);
  color: #667eea;
  font-size: 22rpx;
  font-weight: 500;
}

.text-content {
  color: #444;
  font-size: 30rpx;
  line-height: 1.8;
  margin-bottom: 20rpx;
}

.media-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12rpx;
  margin-bottom: 20rpx;
}

.media-img {
  width: 100%;
  height: 220rpx;
  border-radius: 16rpx;
  background: #f2f2f2;
}

.media-video video {
  width: 100%;
  height: 400rpx;
  border-radius: 16rpx;
  overflow: hidden;
  background: #000;
  margin-bottom: 20rpx;
}

.actions-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 20rpx;
  border-top: 1rpx solid #f0f0f0;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 12rpx 18rpx;
  border-radius: 16rpx;
  transition: all 0.3s;
  color: #666;
  font-size: 26rpx;
}

.action-btn:active {
  background: #f5f7fb;
  transform: scale(0.96);
}

.action-icon {
  font-size: 30rpx;
}

.action-count {
  font-size: 26rpx;
  color: #666;
}
</style>