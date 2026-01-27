<template>
  <div class="task-form">
    <h3 v-if="editing">✏️ Редактирование задачи</h3>
    <h3 v-else>➕ Новая задача</h3>
    
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="title">Заголовок *</label>
        <input
          type="text"
          id="title"
          v-model="formData.title"
          placeholder="Что нужно сделать?"
          required
          :disabled="loading"
          @input="clearError"
        />
      </div>
      
      <div class="form-group">
        <label for="description">Описание</label>
        <textarea
          id="description"
          v-model="formData.description"
          placeholder="Подробное описание..."
          rows="3"
          :disabled="loading"
        ></textarea>
      </div>
      
      <div class="form-group" v-if="editing">
        <label class="checkbox-label">
          <input 
            type="checkbox" 
            v-model="formData.is_completed"
            :disabled="loading"
          />
          <span>Задача выполнена</span>
        </label>
      </div>
      
      <div class="form-actions">
        <button 
          type="submit" 
          :disabled="loading || !formData.title.trim()"
          class="btn btn-primary"
        >
          <span v-if="loading">{{ editing ? 'Сохранение...' : 'Создание...' }}</span>
          <span v-else>{{ editing ? 'Сохранить' : 'Создать задачу' }}</span>
        </button>
        
        <button 
          type="button" 
          @click="resetForm"
          class="btn btn-secondary"
          :disabled="loading"
        >
          {{ editing ? 'Отмена' : 'Очистить' }}
        </button>
        
        <button 
          v-if="editing"
          type="button" 
          @click="$emit('cancel-edit')"
          class="btn btn-secondary"
          :disabled="loading"
        >
          Закрыть
        </button>
      </div>
      
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
      
      <div v-if="success" class="success-message">
        ✅ {{ editing ? 'Задача обновлена!' : 'Задача успешно создана!' }}
      </div>
    </form>
  </div>
</template>

<script>
import api from '../services/api';

export default {
  name: 'TaskForm',
  props: {
    editing: {
      type: Boolean,
      default: false
    },
    task: {
      type: Object,
      default: null
    }
  },
  emits: ['task-created', 'task-updated', 'cancel-edit'],
  data() {
    return {
      formData: {
        title: '',
        description: '',
        is_completed: false
      },
      loading: false,
      error: null,
      success: false
    };
  },
  watch: {
    task: {
      immediate: true,
      handler(newTask) {
        if (newTask) {
          this.formData = {
            title: newTask.title || '',
            description: newTask.description || '',
            is_completed: newTask.is_completed || false
          };
        }
      }
    }
  },
  methods: {
    async handleSubmit() {
      if (!this.formData.title.trim()) {
        this.error = 'Введите заголовок задачи';
        this.$notify.error('Заголовок задачи не может быть пустым', 'Ошибка');
        return;
      }
      
      this.loading = true;
      this.error = null;
      this.success = false;
      
      try {
        const taskData = {
          title: this.formData.title.trim(),
          description: this.formData.description.trim() || null
        };
        
        if (this.editing) {
          taskData.is_completed = this.formData.is_completed;
        }
        
        let response;
        if (this.editing && this.task) {
          response = await api.updateTask(this.task.id, taskData);
          this.$emit('task-updated', response.data);
        } else {
          response = await api.createTask(taskData);
          this.$emit('task-created', response.data);
        }
        
        this.success = true;
        
        if (!this.editing) {
          this.resetForm();
        }
        
        // Автоматически скрыть сообщение об успехе
        setTimeout(() => {
          this.success = false;
          if (this.editing) {
            this.$emit('cancel-edit');
          }
        }, 2000);
        
      } catch (error) {
        console.error('Ошибка операции с задачей:', error);
        // Уведомление об ошибке уже показывается через интерцептор API
        if (error.response?.status === 422) {
          this.error = 'Ошибка валидации данных. Проверьте введенные данные.';
        } else if (error.response?.status === 404) {
          this.error = 'Задача не найдена. Возможно, она была удалена.';
        } else {
          this.error = 'Произошла ошибка. Попробуйте еще раз.';
        }
      } finally {
        this.loading = false;
      }
    },
    
    resetForm() {
      this.formData = {
        title: '',
        description: '',
        is_completed: false
      };
      this.error = null;
      this.success = false;
    },
    
    clearError() {
      if (this.error) {
        this.error = null;
      }
    }
  }
};
</script>

<style scoped>
.task-form {
  background: white;
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  margin-bottom: 30px;
  animation: fadeIn 0.5s ease-out;
}

.task-form h3 {
  margin-bottom: 20px;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #555;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 16px;
  font-family: inherit;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #2196f3;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.1);
  animation: inputFocus 0.3s ease-out;
}

@keyframes inputFocus {
  0% { box-shadow: 0 0 0 0 rgba(33, 150, 243, 0.4); }
  100% { box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.1); }
}

.form-group input:disabled,
.form-group textarea:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.checkbox-label input {
  margin-right: 8px;
}

.checkbox-label span {
  user-select: none;
}

.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 25px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  flex: 1;
  position: relative;
  overflow: hidden;
}

.btn::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 5px;
  height: 5px;
  background: rgba(255, 255, 255, 0.5);
  opacity: 0;
  border-radius: 100%;
  transform: scale(1, 1) translate(-50%);
  transform-origin: 50% 50%;
}

.btn:focus:not(:active)::after {
  animation: ripple 1s ease-out;
}

@keyframes ripple {
  0% {
    transform: scale(0, 0);
    opacity: 0.5;
  }
  100% {
    transform: scale(20, 20);
    opacity: 0;
  }
}

.btn-primary {
  background: #2196f3;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #1976d2;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f5f5f5;
  color: #666;
}

.btn-secondary:hover:not(:disabled) {
  background: #e0e0e0;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error-message {
  margin-top: 15px;
  padding: 10px 15px;
  background: #ffebee;
  color: #d32f2f;
  border-radius: 5px;
  border-left: 4px solid #f44336;
  animation: shake 0.5s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
  20%, 40%, 60%, 80% { transform: translateX(5px); }
}

.success-message {
  margin-top: 15px;
  padding: 10px 15px;
  background: #e8f5e9;
  color: #2e7d32;
  border-radius: 5px;
  border-left: 4px solid #4caf50;
  animation: slideInRight 0.5s ease-out;
}
</style>