/**
 * Сервис для работы с API бэкенда.
 * Содержит все функции для отправки HTTP запросов.
 */

import axios from 'axios';

// Создаем экземпляр axios с базовыми настройками
const apiClient = axios.create({
  // Базовый URL для всех запросов
  baseURL: 'http://localhost:8000',
  
  // Общие заголовки для всех запросов
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  
  // Таймаут запроса (в миллисекундах)
  timeout: 10000
});

// Интерцептор для обработки ошибок
apiClient.interceptors.response.use(
  // Если запрос успешный, просто возвращаем ответ
  (response) => response,
  
  // Если произошла ошибка
  (error) => {
    console.error('API Error:', error);
    
    // Пробрасываем ошибку дальше для обработки в компонентах
    return Promise.reject(error);
  }
);

// Сервис для работы с задачами
const taskService = {
  /**
   * Получает список задач с пагинацией и фильтрацией.
   * 
   * @param {number} skip - сколько задач пропустить
   * @param {number} limit - максимальное количество задач
   * @param {boolean|null} completed - фильтр по статусу выполнения
   * @returns {Promise} Promise с данными задач
   */
  getTasks(skip = 0, limit = 100, completed = null) {
    // Создаем объект с параметрами запроса
    const params = { skip, limit };
    
    // Добавляем фильтр по статусу, если он указан
    if (completed !== null) {
      params.completed = completed;
    }
    
    // Отправляем GET запрос с параметрами
    return apiClient.get('/tasks', { params });
  },
  
  /**
   * Получает задачу по ID.
   * 
   * @param {number} id - ID задачи
   * @returns {Promise} Promise с данными задачи
   */
  getTask(id) {
    return apiClient.get(`/tasks/${id}`);
  },
  
  /**
   * Создает новую задачу.
   * 
   * @param {Object} taskData - данные задачи
   * @param {string} taskData.title - заголовок задачи
   * @param {string} [taskData.description] - описание задачи
   * @returns {Promise} Promise с созданной задачей
   */
  /*createTask(taskData) {
    return apiClient.post('/tasks', taskData);
  },*/
  createTask(taskData) {
  return apiClient.post('/tasks', taskData);  // Просто отправляем JSON
},
  
  /**
   * Обновляет существующую задачу.
   * 
   * @param {number} id - ID задачи
   * @param {Object} taskData - данные для обновления
   * @returns {Promise} Promise с обновленной задачей
   */
  updateTask(id, taskData) {
    return apiClient.put(`/tasks/${id}`, taskData);
  },
  
  /**
   * Удаляет задачу.
   * 
   * @param {number} id - ID задачи
   * @returns {Promise} Promise без данных (статус 204)
   */
  deleteTask(id) {
    return apiClient.delete(`/tasks/${id}`);
  },
  
  /**
   * Отмечает задачу как выполненную.
   * 
   * @param {number} id - ID задачи
   * @returns {Promise} Promise с обновленной задачей
   */
  completeTask(id) {
    return apiClient.patch(`/tasks/${id}/complete`);
  }
};

// Экспортируем сервис для использования в компонентах
export default taskService;