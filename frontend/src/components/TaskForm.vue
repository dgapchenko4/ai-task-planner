<template>
  <div class="task-form">
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="title">Заголовок задачи *</label>
        <input
          type="text"
          id="title"
          v-model="title"
          placeholder="Что нужно сделать?"
          required
          maxlength="255"
          :disabled="loading"
        />
        <div class="char-counter">{{ title.length }}/255</div>
      </div>
      
      <div class="form-group">
        <label for="description">Описание (необязательно)</label>
        <textarea
          id="description"
          v-model="description"
          placeholder="Подробное описание задачи..."
          rows="3"
          maxlength="2000"
          :disabled="loading"
        ></textarea>
        <div class="char-counter">{{ description.length }}/2000</div>
      </div>
      
      <div class="form-actions">
        <button 
          type="submit" 
          class="btn btn-primary"
          :disabled="loading || !title.trim()"
        >
          <span v-if="loading">Добавление...</span>
          <span v-else>Добавить задачу</span>
        </button>
        
        <button 
          type="button" 
          class="btn btn-secondary"
          @click="resetForm"
          :disabled="loading"
        >
          Очистить
        </button>
      </div>
      
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
    </form>
  </div>
</template>

<script>
import taskService from '../services/api';

export default {
  name: 'TaskForm',
  
  data() {
    return {
      // Данные формы
      title: '',
      description: '',
      
      // Состояния формы
      loading: false,
      error: null
    };
  },
  
  methods: {
    /**
     * Обрабатывает отправку формы.
     */
    async handleSubmit() {
      // Проверяем, что заголовок не пустой
      if (!this.title.trim()) {
        this.error = 'Заголовок задачи не может быть пустым';
        return;
      }
      
      // Сбрасываем предыдущую ошибку
      this.error = null;
      this.loading = true;
      
      try {
        // Создаем объект с данными задачи
        const taskData = {
          title: this.title.trim(),
          description: this.description.trim() || null
        };
        
        // Отправляем запрос на создание задачи
        const response = await taskService.createTask(taskData);
        
        // Извещаем родительский компонент о новой задаче
        this.$emit('task-added', response.data);
        
        // Сбрасываем форму
        this.resetForm();
        
        // Показываем сообщение об успехе
        alert('Задача успешно добавлена!');
        
      } catch (error) {
        console.error('Ошибка при создании задачи:', error);
        
        // Формируем понятное сообщение об ошибке
        if (error.response) {
          // Сервер ответил с кодом ошибки
          if (error.response.status === 422) {
            this.error = 'Проверьте правильность заполнения формы';
          } else {
            this.error = `Ошибка сервера: ${error.response.status}`;
          }
        } else if (error.request) {
          // Запрос был отправлен, но ответа не получено
          this.error = 'Не удалось подключиться к серверу. Проверьте подключение к интернету.';
        } else {
          // Ошибка при настройке запроса
          this.error = 'Ошибка при отправке запроса';
        }
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * Сбрасывает форму к исходному состоянию.
     */
    resetForm() {
      this.title = '';
      this.description = '';
      this.error = null;
    }
  }
};
</script>

<style scoped>
.task-form {
  background: white;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
  margin-bottom: 30px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #444;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 12px 15px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 16px;
  font-family: inherit;
  transition: border-color 0.3s ease;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #667eea;
}

.form-group input:disabled,
.form-group textarea:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.char-counter {
  text-align: right;
  font-size: 12px;
  color: #888;
  margin-top: 5px;
}

.form-actions {
  display: flex;
  gap: 15px;
  margin-top: 25px;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  flex: 1;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 7px 14px rgba(102, 126, 234, 0.3);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f0f0f0;
  color: #666;
}

.btn-secondary:hover:not(:disabled) {
  background: #e0e0e0;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error-message {
  margin-top: 15px;
  padding: 10px 15px;
  background: #ffe6e6;
  color: #d32f2f;
  border-radius: 6px;
  font-size: 14px;
}
</style>