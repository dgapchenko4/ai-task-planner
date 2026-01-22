/**
 * Главный файл Vue.js приложения.
 * Здесь происходит инициализация и настройка приложения.
 */

import { createApp } from 'vue'
import App from './App.vue'

// Создаем экземпляр приложения Vue
const app = createApp(App)

// Монтируем приложение в элемент #app
app.mount('#app')

// Выводим сообщение в консоль для отладки
console.log('Vue приложение запущено!')
