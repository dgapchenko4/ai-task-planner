<template>
  <div id="app">
    <!-- Шапка приложения -->
    <header class="app-header">
      <div class="container">
        <h1>📝 AI Task Planner</h1>
        <p class="subtitle">Умный планировщик задач с AI-ассистентом</p>
      </div>
    </header>
    
    <!-- Основное содержимое -->
    <main class="app-main">
      <div class="container">
        <!-- Компонент для добавления новой задачи -->
        <TaskForm @task-added="handleTaskAdded" />
        
        <!-- Фильтры для задач -->
        <div class="filters">
          <button 
            @click="setFilter(null)" 
            :class="{ active: filter === null }"
            class="filter-btn"
          >
            Все задачи
          </button>
          <button 
            @click="setFilter(false)" 
            :class="{ active: filter === false }"
            class="filter-btn"
          >
            Активные
          </button>
          <button 
            @click="setFilter(true)" 
            :class="{ active: filter === true }"
            class="filter-btn"
          >
            Выполненные
          </button>
        </div>
        
        <!-- Компонент списка задач -->
        <TaskList 
          :tasks="filteredTasks" 
          :loading="loading"
          @task-updated="handleTaskUpdated"
          @task-deleted="handleTaskDeleted"
        />
        
        <!-- Статистика -->
        <div class="stats" v-if="tasks.length > 0">
          <p>
            Всего задач: {{ totalTasks }} | 
            Выполнено: {{ completedTasks }} ({{ completionPercentage }}%)
          </p>
        </div>
      </div>
    </main>
    
    <!-- Подвал -->
    <footer class="app-footer">
      <div class="container">
        <p>AI Task Planner v1.0.0 | Этап 1: MVP</p>
      </div>
    </footer>
  </div>
</template>

<script>
// Импортируем компоненты
import TaskForm from './components/TaskForm.vue';
import TaskList from './components/TaskList.vue';
import taskService from './services/api';

export default {
  name: 'App',
  
  components: {
    TaskForm,
    TaskList
  },
  
  data() {
    return {
      // Список всех задач
      tasks: [],
      
      // Фильтр по статусу выполнения (null - все задачи)
      filter: null,
      
      // Флаг загрузки данных
      loading: false,
      
      // Общее количество задач (для пагинации)
      total: 0
    };
  },
  
  computed: {
    /**
     * Отфильтрованный список задач в зависимости от выбранного фильтра.
     */
    filteredTasks() {
      if (this.filter === null) {
        return this.tasks;
      }
      return this.tasks.filter(task => task.is_completed === this.filter);
    },
    
    /**
     * Количество выполненных задач.
     */
    completedTasks() {
      return this.tasks.filter(task => task.is_completed).length;
    },
    
    /**
     * Общее количество задач.
     */
    totalTasks() {
      return this.tasks.length;
    },
    
    /**
     * Процент выполнения задач.
     */
    completionPercentage() {
      if (this.totalTasks === 0) return 0;
      return Math.round((this.completedTasks / this.totalTasks) * 100);
    }
  },
  
  // Хук, который выполняется при монтировании компонента
  mounted() {
    // Загружаем задачи при запуске приложения
    this.loadTasks();
  },
  
  methods: {
    /**
     * Загружает задачи с сервера.
     */
    async loadTasks() {
      this.loading = true;
      
      try {
        // Вызываем метод сервиса для получения задач
        const response = await taskService.getTasks();
        
        // Сохраняем задачи в data
        this.tasks = response.data.tasks;
        this.total = response.data.total;
        
        console.log('Задачи загружены:', this.tasks.length);
      } catch (error) {
        console.error('Ошибка при загрузке задач:', error);
        alert('Не удалось загрузить задачи. Проверьте подключение к серверу.');
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * Обрабатывает добавление новой задачи.
     * 
     * @param {Object} newTask - новая задача
     */
    handleTaskAdded(newTask) {
      // Добавляем новую задачу в начало списка
      this.tasks.unshift(newTask);
    },
    
    /**
     * Обрабатывает обновление задачи.
     * 
     * @param {Object} updatedTask - обновленная задача
     */
    handleTaskUpdated(updatedTask) {
      // Находим индекс обновленной задачи в массиве
      const index = this.tasks.findIndex(task => task.id === updatedTask.id);
      
      // Если задача найдена, обновляем ее
      if (index !== -1) {
        this.tasks.splice(index, 1, updatedTask);
      }
    },
    
    /**
     * Обрабатывает удаление задачи.
     * 
     * @param {number} taskId - ID удаленной задачи
     */
    handleTaskDeleted(taskId) {
      // Удаляем задачу из массива
      this.tasks = this.tasks.filter(task => task.id !== taskId);
    },
    
    /**
     * Устанавливает фильтр для отображения задач.
     * 
     * @param {boolean|null} filterType - тип фильтра
     */
    setFilter(filterType) {
      this.filter = filterType;
    }
  }
};
</script>

<style>
/* Глобальные стили */
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

/* Стили шапки */
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

/* Стили основного содержимого */
.app-main {
  padding: 2rem 0;
  min-height: calc(100vh - 160px);
}

/* Стили фильтров */
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
  background: #f0f2ff;
}

.filter-btn.active {
  background: #667eea;
  color: white;
}

/* Стили статистики */
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

/* Стили подвала */
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

/* Адаптивность */
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
