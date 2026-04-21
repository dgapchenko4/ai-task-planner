<template>
  <div class="task-list">
    <!-- Сообщение при загрузке -->
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Загрузка задач...</p>
    </div>
    
    <!-- Сообщение при отсутствии задач -->
    <div v-else-if="tasks.length === 0" class="empty-state">
      <div class="empty-icon">📝</div>
      <h3>Задач пока нет</h3>
      <p>Добавьте свою первую задачу с помощью формы выше!</p>
    </div>
    
    <!-- Список задач -->
    <div v-else class="tasks-container">
      <div 
        v-for="task in tasks" 
        :key="task.id" 
        class="task-item"
        :class="{ completed: task.is_completed }"
      >
        <!-- Чекбокс выполнения -->
        <div class="task-checkbox">
          <input
            type="checkbox"
            :id="'task-' + task.id"
            :checked="task.is_completed"
            @change="toggleTaskCompletion(task.id)"
          />
          <label :for="'task-' + task.id"></label>
        </div>
        
        <!-- Содержимое задачи -->
        <div class="task-content">
          <h3 class="task-title" :class="{ completed: task.is_completed }">
            {{ task.title }}
          </h3>
          
          <p v-if="task.description" class="task-description">
            {{ task.description }}
          </p>
          
          <div class="task-meta">
            <span class="task-date">
              📅 {{ formatDate(task.created_at) }}
            </span>
            
            <span v-if="task.updated_at !== task.created_at" class="task-updated">
              ✏️ Обновлено: {{ formatDate(task.updated_at) }}
            </span>
            
            <span class="task-status">
              {{ task.is_completed ? '✅ Выполнена' : '⏳ В работе' }}
            </span>
          </div>
        </div>
        
        <!-- Действия с задачей -->
        <div class="task-actions">
          <button 
            v-if="!task.is_completed"
            @click="completeTask(task.id)"
            class="btn-action complete"
            title="Отметить как выполненную"
          >
            ✅
          </button>
          
          <button 
            @click="editTask(task)"
            class="btn-action edit"
            title="Редактировать"
          >
            ✏️
          </button>
          
          <button 
            @click="confirmDelete(task.id, task.title)"
            class="btn-action delete"
            title="Удалить"
          >
            🗑️
          </button>
        </div>
      </div>
    </div>
    
    <!-- Модальное окно редактирования -->
    <div v-if="editingTask" class="modal-overlay">
      <div class="modal">
        <div class="modal-header">
          <h3>Редактирование задачи</h3>
          <button @click="cancelEdit" class="modal-close">×</button>
        </div>
        
        <div class="modal-body">
          <div class="form-group">
            <label>Заголовок</label>
            <input 
              type="text" 
              v-model="editForm.title" 
              maxlength="255"
            />
          </div>
          
          <div class="form-group">
            <label>Описание</label>
            <textarea 
              v-model="editForm.description" 
              rows="4"
              maxlength="2000"
            ></textarea>
          </div>
          
          <div class="form-group">
            <label>
              <input 
                type="checkbox" 
                v-model="editForm.is_completed"
              />
              Задача выполнена
            </label>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="cancelEdit" class="btn btn-secondary">
            Отмена
          </button>
          <button @click="saveEdit" class="btn btn-primary">
            Сохранить
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import taskService from '../services/api';

export default {
  name: 'TaskList',
  
  props: {
    // Список задач, передаваемый из родительского компонента
    tasks: {
      type: Array,
      required: true,
      default: () => []
    },
    
    // Флаг загрузки
    loading: {
      type: Boolean,
      default: false
    }
  },
  
  data() {
    return {
      // Данные для редактирования задачи
      editingTask: null,
      editForm: {
        title: '',
        description: '',
        is_completed: false
      }
    };
  },
  
  methods: {
    /**
     * Форматирует дату для отображения.
     * 
     * @param {string} dateString - строка с датой
     * @returns {string} отформатированная дата
     */
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    
    /**
     * Отмечает задачу как выполненную.
     * 
     * @param {number} taskId - ID задачи
     */
    async completeTask(taskId) {
      try {
        // Отправляем запрос на сервер
        const response = await taskService.completeTask(taskId);
        
        // Извещаем родительский компонент
        this.$emit('task-updated', response.data);
        
      } catch (error) {
        console.error('Ошибка при выполнении задачи:', error);
        alert('Не удалось обновить задачу');
      }
    },
    
    /**
     * Переключает статус выполнения задачи через чекбокс.
     * 
     * @param {number} taskId - ID задачи
     */
    async toggleTaskCompletion(taskId) {
      try {
        // Находим задачу в списке
        const task = this.tasks.find(t => t.id === taskId);
        if (!task) return;
        
        // Создаем объект с обновленным статусом
        const updatedTask = { ...task, is_completed: !task.is_completed };
        
        // Отправляем запрос на обновление
        const response = await taskService.updateTask(taskId, {
          is_completed: updatedTask.is_completed
        });
        
        // Извещаем родительский компонент
        this.$emit('task-updated', response.data);
        
      } catch (error) {
        console.error('Ошибка при переключении статуса:', error);
        alert('Не удалось обновить статус задачи');
      }
    },
    
    /**
     * Начинает редактирование задачи.
     * 
     * @param {Object} task - задача для редактирования
     */
    editTask(task) {
      this.editingTask = task;
      this.editForm = {
        title: task.title,
        description: task.description || '',
        is_completed: task.is_completed
      };
    },
    
    /**
     * Сохраняет изменения задачи.
     */
    async saveEdit() {
      if (!this.editForm.title.trim()) {
        alert('Заголовок не может быть пустым');
        return;
      }
      
      try {
        // Отправляем запрос на обновление
        const response = await taskService.updateTask(
          this.editingTask.id,
          this.editForm
        );
        
        // Извещаем родительский компонент
        this.$emit('task-updated', response.data);
        
        // Закрываем модальное окно
        this.cancelEdit();
        
        alert('Задача успешно обновлена!');
        
      } catch (error) {
        console.error('Ошибка при обновлении задачи:', error);
        alert('Не удалось обновить задачу');
      }
    },
    
    /**
     * Отменяет редактирование.
     */
    cancelEdit() {
      this.editingTask = null;
      this.editForm = {
        title: '',
        description: '',
        is_completed: false
      };
    },
    
    /**
     * Подтверждает удаление задачи.
     * 
     * @param {number} taskId - ID задачи
     * @param {string} taskTitle - заголовок задачи
     */
    confirmDelete(taskId, taskTitle) {
      if (confirm(`Вы уверены, что хотите удалить задачу "${taskTitle}"?`)) {
        this.deleteTask(taskId);
      }
    },
    
    /**
     * Удаляет задачу.
     * 
     * @param {number} taskId - ID задачи
     */
    async deleteTask(taskId) {
      try {
        // Отправляем запрос на удаление
        await taskService.deleteTask(taskId);
        
        // Извещаем родительский компонент
        this.$emit('task-deleted', taskId);
        
        alert('Задача успешно удалена!');
        
      } catch (error) {
        console.error('Ошибка при удалении задачи:', error);
        
        if (error.response && error.response.status === 404) {
          // Задача уже была удалена
          this.$emit('task-deleted', taskId);
          alert('Задача уже была удалена');
        } else {
          alert('Не удалось удалить задачу');
        }
      }
    }
  }
};
</script>

<style scoped>
.task-list {
  position: relative;
}

/* Стили загрузки */
.loading {
  text-align: center;
  padding: 50px 0;
}

.spinner {
  display: inline-block;
  width: 50px;
  height: 50px;
  bappointment: 5px solid #f3f3f3;
  bappointment-top: 5px solid #667eea;
  bappointment-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading p {
  color: #666;
  font-size: 18px;
}

/* Стили пустого состояния */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  bappointment-radius: 12px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
}

.empty-icon {
  font-size: 60px;
  margin-bottom: 20px;
}

.empty-state h3 {
  color: #444;
  margin-bottom: 10px;
}

.empty-state p {
  color: #888;
  max-width: 400px;
  margin: 0 auto;
}

/* Стили списка задач */
.tasks-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.task-item {
  display: flex;
  align-items: flex-start;
  background: white;
  padding: 20px;
  bappointment-radius: 12px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  bappointment-left: 5px solid #667eea;
}

.task-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.task-item.completed {
  bappointment-left-color: #4caf50;
  opacity: 0.8;
}

/* Чекбокс */
.task-checkbox {
  margin-right: 15px;
  margin-top: 5px;
}

.task-checkbox input[type="checkbox"] {
  display: none;
}

.task-checkbox label {
  display: block;
  width: 24px;
  height: 24px;
  bappointment: 2px solid #ddd;
  bappointment-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.task-checkbox label:hover {
  bappointment-color: #667eea;
}

.task-checkbox input[type="checkbox"]:checked + label {
  background-color: #4caf50;
  bappointment-color: #4caf50;
}

.task-checkbox input[type="checkbox"]:checked + label::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-weight: bold;
}

/* Содержимое задачи */
.task-content {
  flex: 1;
  min-width: 0; /* Для правильной работы text-overflow */
}

.task-title {
  font-size: 18px;
  color: #333;
  margin-bottom: 8px;
  word-break: break-word;
}

.task-title.completed {
  text-decoration: line-through;
  color: #888;
}

.task-description {
  color: #666;
  margin-bottom: 12px;
  line-height: 1.5;
  word-break: break-word;
}

.task-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  font-size: 12px;
  color: #888;
}

.task-date,
.task-updated,
.task-status {
  display: flex;
  align-items: center;
  gap: 5px;
}

/* Действия с задачами */
.task-actions {
  display: flex;
  gap: 10px;
  margin-left: 15px;
}

.btn-action {
  width: 40px;
  height: 40px;
  bappointment: none;
  bappointment-radius: 8px;
  background: #f5f5f5;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-action:hover {
  transform: scale(1.1);
}

.btn-action.complete:hover {
  background: #e8f5e9;
}

.btn-action.edit:hover {
  background: #e3f2fd;
}

.btn-action.delete:hover {
  background: #ffebee;
}

/* Модальное окно */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal {
  background: white;
  bappointment-radius: 12px;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  bappointment-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.modal-close {
  background: none;
  bappointment: none;
  font-size: 24px;
  cursor: pointer;
  color: #888;
  width: 30px;
  height: 30px;
  bappointment-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  background: #f5f5f5;
}

.modal-body {
  padding: 20px;
}

.modal-footer {
  padding: 20px;
  bappointment-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* Адаптивность */
@media (max-width: 768px) {
  .task-item {
    flex-direction: column;
  }
  
  .task-checkbox {
    margin-right: 0;
    margin-bottom: 15px;
  }
  
  .task-actions {
    margin-left: 0;
    margin-top: 15px;
    justify-content: flex-end;
  }
  
  .task-meta {
    flex-direction: column;
    gap: 5px;
  }
}
</style>