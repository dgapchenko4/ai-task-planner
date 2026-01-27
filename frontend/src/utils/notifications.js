import { createApp } from 'vue';
import Notification from '../components/Notification.vue';

class NotificationManager {
  constructor() {
    this.notifications = [];
    this.container = null;
  }
  
  init() {
    // Создаем контейнер для уведомлений
    this.container = document.createElement('div');
    this.container.id = 'notifications-container';
    document.body.appendChild(this.container);
  }
  
  show(options) {
    const id = Date.now();
    const notification = {
      id,
      ...options,
      onClose: () => this.remove(id)
    };
    
    this.notifications.push(notification);
    this.render();
    
    return id;
  }
  
  success(message, title = 'Успешно', duration = 3000) {
    return this.show({
      type: 'success',
      title,
      message,
      duration
    });
  }
  
  error(message, title = 'Ошибка', duration = 5000) {
    return this.show({
      type: 'error',
      title,
      message,
      duration
    });
  }
  
  info(message, title = 'Информация', duration = 3000) {
    return this.show({
      type: 'info',
      title,
      message,
      duration
    });
  }
  
  warning(message, title = 'Внимание', duration = 4000) {
    return this.show({
      type: 'warning',
      title,
      message,
      duration
    });
  }
  
  remove(id) {
    this.notifications = this.notifications.filter(n => n.id !== id);
    this.render();
  }
  
  clear() {
    this.notifications = [];
    this.render();
  }
  
  render() {
    if (!this.container) return;
    
    // Удаляем старые уведомления
    while (this.container.firstChild) {
      this.container.removeChild(this.container.firstChild);
    }
    
    // Создаем новые
    this.notifications.forEach(notification => {
      const app = createApp(Notification, {
        ...notification,
        key: notification.id
      });
      
      const instance = app.mount(document.createElement('div'));
      this.container.appendChild(instance.$el);
    });
  }
}

// Экспортируем синглтон
const notificationManager = new NotificationManager();
export default notificationManager;