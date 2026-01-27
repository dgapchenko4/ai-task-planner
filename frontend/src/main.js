import { createApp } from 'vue'
import App from './App.vue'

// Импортируем стили анимаций
import './assets/styles/animations.css'

// Создаем экземпляр приложения
const app = createApp(App)

// Сохраняем экземпляр приложения в глобальной переменной для доступа из API
window.appInstance = app

// Глобальный метод для уведомлений
app.config.globalProperties.$notify = {
  success(message, title = 'Успешно') {
    this.showNotification('success', title, message)
  },
  error(message, title = 'Ошибка') {
    this.showNotification('error', title, message)
  },
  info(message, title = 'Информация') {
    this.showNotification('info', title, message)
  },
  warning(message, title = 'Внимание') {
    this.showNotification('warning', title, message)
  },
  
  showNotification(type, title, message) {
    // Создаем контейнер для уведомлений если его нет
    let container = document.getElementById('notifications-container')
    if (!container) {
      container = document.createElement('div')
      container.id = 'notifications-container'
      container.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        display: flex;
        flex-direction: column;
        gap: 10px;
        max-width: 400px;
      `
      document.body.appendChild(container)
    }
    
    // Создаем элемент уведомления
    const notification = document.createElement('div')
    notification.className = `notification notification-${type} fade-in`
    
    // Иконка в зависимости от типа
    const icons = {
      success: '✅',
      error: '❌',
      warning: '⚠️',
      info: 'ℹ️'
    }
    
    notification.innerHTML = `
      <div class="notification-icon">${icons[type]}</div>
      <div class="notification-content">
        <h4>${title}</h4>
        <p>${message}</p>
      </div>
      <button class="notification-close">×</button>
    `
    
    // Добавляем обработчик закрытия
    const closeBtn = notification.querySelector('.notification-close')
    closeBtn.addEventListener('click', () => {
      notification.classList.add('fade-out')
      setTimeout(() => notification.remove(), 300)
    })
    
    container.appendChild(notification)
    
    // Автоматически удаляем через 5 секунд
    setTimeout(() => {
      if (notification.parentElement) {
        notification.classList.add('fade-out')
        setTimeout(() => notification.remove(), 300)
      }
    }, 5000)
  }
}

// Монтируем приложение
app.mount('#app')

console.log('🚀 Vue приложение запущено!')