<template>
  <div 
    class="task-item" 
    :class="{ completed: task.is_completed, 'bounce-in': isNew }"
    @animationend="onAnimationEnd"
  >
    <div class="task-content">
      <div class="task-header">
        <h3 :class="{ completed: task.is_completed }">
          {{ task.title }}
        </h3>
        <div class="task-status-indicator">
          <span class="status" :class="statusClass">
            {{ task.is_completed ? '✅ Выполнена' : '⏳ В работе' }}
          </span>
          <span class="priority" v-if="task.priority">
            {{ getPriorityLabel(task.priority) }}
          </span>
        </div>
      </div>
      
      <p v-if="task.description" class="task-description">
        {{ task.description }}
      </p>
      
      <div class="task-meta">
        <span class="date">📅 {{ formatDate(task.created_at) }}</span>
        <span v-if="task.updated_at !== task.created_at" class="date">
          ✏️ {{ formatDate(task.updated_at) }}
        </span>
        <span class="task-id">ID: {{ task.id }}</span>
      </div>
    </div>
    
    <div class="task-actions">
      <button 
        v-if="!task.is_completed"
        @click="$emit('complete', task.id)"
        class="btn-action complete"
        title="Отметить выполненной"
      >
        ✅
      </button>
      
      <button 
        @click="$emit('edit', task)"
        class="btn-action edit"
        title="Редактировать"
      >
        ✏️
      </button>
      
      <button 
        @click="$emit('delete', task.id)"
        class="btn-action delete"
        title="Удалить"
      >
        🗑️
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TaskItem',
  props: {
    task: {
      type: Object,
      required: true
    },
    isNew: {
      type: Boolean,
      default: false
    }
  },
  emits: ['complete', 'edit', 'delete'],
  computed: {
    statusClass() {
      return this.task.is_completed ? 'status-completed' : 'status-pending';
    }
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    
    getPriorityLabel(priority) {
      const priorities = {
        'high': '🔴 Высокий',
        'medium': '🟡 Средний',
        'low': '🟢 Низкий'
      };
      return priorities[priority] || priority;
    },
    
    onAnimationEnd() {
      // Убираем класс анимации после завершения
      this.$emit('animation-end');
    }
  }
};
</script>

<style scoped>
.task-item {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 15px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  border-left: 4px solid #2196f3;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.task-item:hover {
  transform: translateY(-2px) scale(1.01);
  box-shadow: 0 6px 16px rgba(0,0,0,0.15);
}

.task-item.completed {
  border-left-color: #4caf50;
  opacity: 0.8;
}

.task-content {
  flex: 1;
  min-width: 0; /* Для правильной работы text-overflow */
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.task-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
  word-break: break-word;
}

.task-header h3.completed {
  text-decoration: line-through;
  color: #777;
}

.task-status-indicator {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 5px;
  transition: all 0.3s ease;
}

.task-item.completed .task-status-indicator {
  animation: completedPulse 2s ease-out;
}

@keyframes completedPulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); }
}

.status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  white-space: nowrap;
}

.status-completed {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-pending {
  background: #fff3e0;
  color: #ef6c00;
}

.priority {
  font-size: 11px;
  color: #666;
  padding: 2px 6px;
  border-radius: 3px;
  background: #f5f5f5;
}

.task-description {
  color: #555;
  margin: 10px 0;
  line-height: 1.5;
  word-break: break-word;
}

.task-meta {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #777;
  margin-top: 15px;
  flex-wrap: wrap;
}

.date {
  display: flex;
  align-items: center;
  gap: 5px;
}

.task-id {
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: monospace;
}

.task-actions {
  display: flex;
  gap: 8px;
  margin-left: 15px;
  flex-shrink: 0;
}

.btn-action {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 6px;
  background: #f5f5f5;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-action:hover {
  transform: scale(1.2);
}

.btn-action.complete:hover {
  background: #e8f5e9;
  color: #4caf50;
  box-shadow: 0 0 0 4px rgba(76, 175, 80, 0.2);
}

.btn-action.edit:hover {
  background: #e3f2fd;
  color: #2196f3;
  box-shadow: 0 0 0 4px rgba(33, 150, 243, 0.2);
}

.btn-action.delete:hover {
  background: #ffebee;
  color: #f44336;
  box-shadow: 0 0 0 4px rgba(244, 67, 54, 0.2);
}

.bounce-in {
  animation: bounceIn 0.6s ease-out;
}

@keyframes bounceIn {
  0% {
    opacity: 0;
    transform: scale(0.3) translateY(20px);
  }
  50% {
    opacity: 1;
    transform: scale(1.05) translateY(-5px);
  }
  70% {
    transform: scale(0.9) translateY(0);
  }
  100% {
    transform: scale(1) translateY(0);
  }
}
</style>