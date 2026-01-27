<template>
  <transition name="slide-fade">
    <div v-if="visible" :class="['notification', type]" @click="close">
      <div class="notification-icon">
        <span v-if="type === 'success'">✅</span>
        <span v-if="type === 'error'">❌</span>
        <span v-if="type === 'warning'">⚠️</span>
        <span v-if="type === 'info'">ℹ️</span>
      </div>
      <div class="notification-content">
        <h4 v-if="title">{{ title }}</h4>
        <p>{{ message }}</p>
      </div>
      <button class="notification-close" @click.stop="close">×</button>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'Notification',
  props: {
    title: String,
    message: String,
    type: {
      type: String,
      default: 'info',
      validator: (value) => ['success', 'error', 'warning', 'info'].includes(value)
    },
    duration: {
      type: Number,
      default: 3000
    }
  },
  data() {
    return {
      visible: false,
      timeout: null
    };
  },
  mounted() {
    this.show();
  },
  methods: {
    show() {
      this.visible = true;
      
      if (this.duration > 0) {
        this.timeout = setTimeout(() => {
          this.close();
        }, this.duration);
      }
    },
    
    close() {
      this.visible = false;
      if (this.timeout) {
        clearTimeout(this.timeout);
      }
      this.$emit('close');
    }
  }
};
</script>

<style scoped>
.notification {
  position: fixed;
  top: 20px;
  right: 20px;
  min-width: 300px;
  max-width: 400px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  display: flex;
  align-items: flex-start;
  padding: 15px;
  z-index: 1000;
  cursor: pointer;
  transition: all 0.3s ease;
}

.notification:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.2);
}

.notification.success {
  border-left: 4px solid #4caf50;
}

.notification.error {
  border-left: 4px solid #f44336;
}

.notification.warning {
  border-left: 4px solid #ff9800;
}

.notification.info {
  border-left: 4px solid #2196f3;
}

.notification-icon {
  font-size: 24px;
  margin-right: 12px;
  flex-shrink: 0;
}

.notification-content {
  flex: 1;
}

.notification-content h4 {
  margin: 0 0 5px 0;
  font-size: 16px;
  color: #333;
}

.notification-content p {
  margin: 0;
  font-size: 14px;
  color: #666;
  line-height: 1.4;
}

.notification-close {
  background: none;
  border: none;
  font-size: 20px;
  color: #999;
  cursor: pointer;
  padding: 0;
  margin-left: 10px;
  flex-shrink: 0;
}

.notification-close:hover {
  color: #333;
}

/* Анимации */
.slide-fade-enter-active {
  transition: all 0.3s ease;
}

.slide-fade-leave-active {
  transition: all 0.3s cubic-bezier(1, 0.5, 0.8, 1);
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateX(20px);
  opacity: 0;
}
</style>