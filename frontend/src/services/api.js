import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Интерцептор для успешных ответов
apiClient.interceptors.response.use(
  (response) => {
    console.log(`✅ ${response.config.method.toUpperCase()} ${response.config.url}: ${response.status}`);
    
    // Показываем уведомление для успешных операций (кроме GET)
    if (response.config.method !== 'get') {
      const actionMap = {
        'post': 'создана',
        'put': 'обновлена',
        'delete': 'удалена',
        'patch': 'обновлена'
      };
      
      const action = actionMap[response.config.method] || 'выполнена';
      
      // Используем глобальный метод уведомлений
      if (window.appInstance) {
        window.appInstance.config.globalProperties.$notify.success(
          `Задача успешно ${action}`,
          'Успех!'
        );
      }
    }
    
    return response;
  },
  
  // Интерцептор для ошибок
  (error) => {
    console.error(`❌ API Error:`, {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      data: error.response?.data,
      message: error.message
    });
    
    // Показываем уведомление об ошибке
    let errorMessage = 'Ошибка сети';
    
    if (error.response) {
      const status = error.response.status;
      
      if (status === 400) errorMessage = 'Неверный запрос';
      else if (status === 401) errorMessage = 'Требуется авторизация';
      else if (status === 403) errorMessage = 'Доступ запрещен';
      else if (status === 404) errorMessage = 'Ресурс не найден';
      else if (status === 422) errorMessage = 'Ошибка валидации данных';
      else if (status === 429) errorMessage = 'Слишком много запросов';
      else if (status >= 500) errorMessage = 'Внутренняя ошибка сервера';
      else errorMessage = `Ошибка ${status}`;
      
      // Показываем детали ошибки если есть
      if (error.response.data?.detail) {
        const detail = error.response.data.detail;
        if (Array.isArray(detail)) {
          errorMessage += ': ' + detail.map(d => d.msg).join(', ');
        } else if (typeof detail === 'string') {
          errorMessage += ': ' + detail;
        }
      }
    } else if (error.request) {
      errorMessage = 'Нет ответа от сервера. Проверьте подключение.';
    } else {
      errorMessage = 'Ошибка при отправке запроса';
    }
    
    // Используем глобальный метод уведомлений
    if (window.appInstance) {
      window.appInstance.config.globalProperties.$notify.error(errorMessage, 'Ошибка');
    }
    
    return Promise.reject(error);
  }
);

// Методы API
export default {
  getTasks(skip = 0, limit = 100, completed = null) {
    const params = { skip, limit };
    if (completed !== null) params.completed = completed;
    return apiClient.get('/tasks', { params });
  },
  
  getTask(id) {
    return apiClient.get(`/tasks/${id}`);
  },
  
  createTask(taskData) {
    return apiClient.post('/tasks', taskData);
  },
  
  updateTask(id, taskData) {
    return apiClient.put(`/tasks/${id}`, taskData);
  },
  
  deleteTask(id) {
    return apiClient.delete(`/tasks/${id}`);
  },
  
  completeTask(id) {
    return apiClient.patch(`/tasks/${id}/complete`);
  }
};