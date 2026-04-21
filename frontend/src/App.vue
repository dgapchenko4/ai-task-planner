<template>
  <div id="app">
    <header class="app-header">
      <div class="container">
        <h1>📝 AI Task Planner</h1>
        <p class="subtitle">Этап 4: Анимации и уведомления</p>
      </div>
    </header>

    <main class="app-main">
      <div class="container">
        <!-- Форма создания/редактирования -->
        <div v-if="editingTask" class="slide-in-right">
          <TaskForm 
            :editing="true"
            :task="editingTask"
            @task-updated="handleTaskUpdated"
            @cancel-edit="cancelEdit"
          />
          <div class="separator"></div>
        </div>
        <TaskForm 
          v-else
          @task-created="handleTaskCreated"
        />
        
        <!-- Фильтры -->
        <div class="filters">
          <button 
            @click="setFilter(null)"
            :class="{ active: currentFilter === null }"
            class="filter-btn pulse"
          >
            Все задачи
          </button>
          <button 
            @click="setFilter(false)"
            :class="{ active: currentFilter === false }"
            class="filter-btn"
          >
            Активные
          </button>
          <button 
            @click="setFilter(true)"
            :class="{ active: currentFilter === true }"
            class="filter-btn"
          >
            Выполненные
          </button>
        </div>
        
        <!-- Индикатор загрузки -->
        <div v-if="loading" class="loading fade-in">
          <div class="spinner"></div>
          <p>Загрузка задач...</p>
        </div>

        <!-- Сообщение об ошибке -->
        <div v-else-if="error" class="error fade-in">
          <h3>Ошибка</h3>
          <p>{{ error }}</p>
          <button @click="loadTasks" class="pulse">Повторить</button>
        </div>

        <!-- Основной контент -->
        <div v-else>
          <!-- Статистика -->
          <div class="stats fade-in" v-if="filteredTasks.length > 0">
            <p>Показано: {{ filteredTasks.length }} из {{ tasks.length }} | 
              Выполнено: {{ completedCount }} ({{ completedPercentage }}%)</p>
          </div>

          <!-- Список задач с анимациями -->
          <TransitionGroup 
            name="task-list"
            tag="div"
            class="task-list"
          >
            <div v-if="filteredTasks.length === 0" key="empty" class="empty fade-in">
              <p v-if="currentFilter === false">Нет активных задач</p>
              <p v-else-if="currentFilter === true">Нет выполненных задач</p>
              <p v-else>Задач пока нет. Создайте первую!</p>
            </div>
            
            <TaskItem
              v-for="task in filteredTasks"
              :key="task.id"
              :task="task"
              :is-new="task.id === newlyCreatedTaskId"
              @complete="completeTask"
              @edit="startEditing"
              @delete="deleteTask"
              @animation-end="clearNewTask"
            />
          </TransitionGroup>
        </div>
      </div>
    </main>

    <footer class="app-footer">
      <div class="container">
        <p>AI Task Planner v1.0.0 | Этап 4</p>
        <p class="status">API статус: <span :class="apiStatusClass">{{ apiStatus }}</span></p>
      </div>
    </footer>
  </div>
</template>

<script>
import api from './services/api';
import TaskForm from './components/TaskForm.vue';
import TaskItem from './components/TaskItem.vue';

export default {
  name: 'App',
  components: {
    TaskForm,
    TaskItem
  },
  data() {
    return {
      tasks: [],
      loading: true,
      error: null,
      apiStatus: 'Проверка...',
      currentFilter: null,
      editingTask: null,
      newlyCreatedTaskId: null
    };
  },
  computed: {
    apiStatusClass() {
      return this.apiStatus === '✅ Работает' ? 'status-ok' : 'status-error';
    },
    completedCount() {
      return this.tasks.filter(task => task.is_completed).length;
    },
    completedPercentage() {
      if (this.tasks.length === 0) return 0;
      return Math.round((this.completedCount / this.tasks.length) * 100);
    },
    filteredTasks() {
      if (this.currentFilter === null) {
        return this.tasks;
      }
      return this.tasks.filter(task => task.is_completed === this.currentFilter);
    }
  },
  mounted() {
    this.checkApi();
    this.loadTasks();
  },
  methods: {
    async checkApi() {
      try {
        await api.getTasks(0, 1);
        this.apiStatus = '✅ Работает';
      } catch (error) {
        this.apiStatus = '❌ Ошибка';
      }
    },
    
    async loadTasks() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await api.getTasks();
        this.tasks = response.data.tasks;
        console.log(`Загружено ${this.tasks.length} задач`);
      } catch (error) {
        this.error = 'Не удалось загрузить задачи';
        console.error('Ошибка загрузки:', error);
      } finally {
        this.loading = false;
      }
    },
    
    async completeTask(taskId) {
      try {
        const response = await api.completeTask(taskId);
        
        // Обновляем задачу в списке
        const index = this.tasks.findIndex(task => task.id === taskId);
        if (index !== -1) {
          this.tasks[index] = response.data;
        }
        
        console.log(`Задача ${taskId} отмечена выполненной`);
      } catch (error) {
        console.error('Ошибка при выполнении задачи:', error);
      }
    },
    
    async deleteTask(taskId) {
      try {
        await api.deleteTask(taskId);
        
        // Удаляем задачу из списка
        this.tasks = this.tasks.filter(task => task.id !== taskId);
        
        console.log(`Задача ${taskId} удалена`);
      } catch (error) {
        console.error('Ошибка при удалении задачи:', error);
      }
    },
    
    startEditing(task) {
      this.editingTask = { ...task };
      window.scrollTo({ top: 0, behavior: 'smooth' });
    },
    
    cancelEdit() {
      this.editingTask = null;
    },
    
    handleTaskCreated(newTask) {
      // Добавляем новую задачу в начало списка
      this.tasks.unshift(newTask);
      this.newlyCreatedTaskId = newTask.id;
      console.log('Новая задача добавлена:', newTask);
    },
    
    clearNewTask() {
      this.newlyCreatedTaskId = null;
    },
    
    handleTaskUpdated(updatedTask) {
      // Обновляем задачу в списке
      const index = this.tasks.findIndex(task => task.id === updatedTask.id);
      if (index !== -1) {
        this.tasks[index] = updatedTask;
      }
      this.editingTask = null;
      console.log('Задача обновлена:', updatedTask);
    },
    
    setFilter(filterType) {
      this.currentFilter = filterType;
    }
  }
};
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: bappointment-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  line-height: 1.6;
  color: #333;
  background-color: #f5f7fa;
}

.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 20px;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem 0;
  text-align: center;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.app-header h1 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.app-header .subtitle {
  font-size: 1.1rem;
  opacity: 0.9;
}

.app-main {
  padding: 2rem 0;
  min-height: calc(100vh - 160px);
}

.filters {
  display: flex;
  gap: 10px;
  margin: 20px 0;
  justify-content: center;
}

.filter-btn {
  padding: 8px 16px;
  bappointment: 2px solid #667eea;
  background: white;
  color: #667eea;
  bappointment-radius: 20px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.filter-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.filter-btn.active {
  background: #667eea;
  color: white;
  animation: pulse 2s infinite;
}

.loading {
  text-align: center;
  padding: 50px 0;
}

.spinner {
  width: 50px;
  height: 50px;
  bappointment: 5px solid #f3f3f3;
  bappointment-top: 5px solid #667eea;
  bappointment-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

.error {
  background: #fff3f3;
  bappointment: 2px solid #ffcdd2;
  bappointment-radius: 10px;
  padding: 25px;
  margin-bottom: 30px;
  text-align: center;
}

.error h3 {
  color: #d32f2f;
  margin-bottom: 10px;
}

.error button {
  margin-top: 15px;
  padding: 10px 20px;
  background: #1976d2;
  color: white;
  bappointment: none;
  bappointment-radius: 5px;
  cursor: pointer;
  font-weight: bold;
}

.stats {
  text-align: center;
  margin-top: 30px;
  padding: 15px;
  background: white;
  bappointment-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.stats p {
  font-weight: 600;
  color: #555;
}

.task-list {
  position: relative;
}

.empty {
  text-align: center;
  padding: 60px 20px;
  background: white;
  bappointment-radius: 12px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  color: #888;
  font-size: 1.1rem;
}

.app-footer {
  background: #333;
  color: white;
  text-align: center;
  padding: 1.5rem 0;
  margin-top: 2rem;
}

.app-footer p {
  opacity: 0.8;
  font-size: 0.9rem;
}

.status {
  margin-top: 5px;
  font-size: 0.9rem;
}

.status-ok {
  color: #4caf50;
  font-weight: bold;
}

.status-error {
  color: #f44336;
  font-weight: bold;
}

.separator {
  height: 2px;
  background: linear-gradient(90deg, transparent, #ddd, transparent);
  margin: 30px 0;
}

/* Анимации для списка задач */
.task-list-move {
  transition: transform 0.3s ease;
}

.task-list-enter-active,
.task-list-leave-active {
  transition: all 0.3s ease;
}

.task-list-enter-from,
.task-list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

.task-list-leave-active {
  position: absolute;
}

@media (max-width: 768px) {
  .app-header h1 {
    font-size: 2rem;
  }
  
  .filters {
    flex-direction: column;
    align-items: center;
  }
  
  .filter-btn {
    width: 200px;
  }
}
</style>