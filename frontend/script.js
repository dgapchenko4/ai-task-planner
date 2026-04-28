// ============================================================================
// AI TASK PLANNER - ПОЛНАЯ ЛОГИКА (АУТЕНТИФИКАЦИЯ + ТЕГИ + ФИЛЬТРАЦИЯ)
// ============================================================================

// ----- 1. ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ -----
let tasks = [];
let currentUser = null;
let userTags = ['работа', 'учеба', 'личное', 'покупки', 'здоровье'];
let currentDate = new Date();
let editingTaskId = null;
let selectedTagFilter = null;      // Выбранный тег для фильтрации
let selectedStatusFilter = 'all';  // 'all', 'active', 'completed'
const API_URL = 'http://localhost:5000';
const STORAGE_KEYS = {
    users: 'ai_planner_users',
    currentUser: 'ai_planner_current_user',
    tasks: 'ai_planner_tasks'
};

// ----- 2. ИНИЦИАЛИЗАЦИЯ -----
function init() {
    console.log("🚀 Приложение запущено");
    loadUsers();
    checkAutoLogin();
    checkServer();
    setInterval(checkServer, 30000);
}

// ----- 3. РАБОТА С ПОЛЬЗОВАТЕЛЯМИ (localStorage) -----
function loadUsers() {
    const users = localStorage.getItem(STORAGE_KEYS.users);
    if (!users) {
        const defaultUsers = {
            'test@example.com': {
                id: 'user1',
                username: 'Тестовый пользователь',
                email: 'test@example.com',
                password: '123456',
                tags: ['работа', 'учеба', 'личное', 'покупки', 'здоровье']
            }
        };
        localStorage.setItem(STORAGE_KEYS.users, JSON.stringify(defaultUsers));
    }
}

function getUsers() {
    return JSON.parse(localStorage.getItem(STORAGE_KEYS.users) || '{}');
}

function saveUsers(users) {
    localStorage.setItem(STORAGE_KEYS.users, JSON.stringify(users));
}

function checkAutoLogin() {
    const savedUser = localStorage.getItem(STORAGE_KEYS.currentUser);
    if (savedUser) {
        currentUser = JSON.parse(savedUser);
        userTags = currentUser.tags || ['работа', 'учеба', 'личное', 'покупки', 'здоровье'];
        loadUserTasks();
        showUserInterface();
        renderTags();
    }
}

function getUserTasksKey() {
    return `${STORAGE_KEYS.tasks}_${currentUser?.id}`;
}

function loadUserTasks() {
    if (!currentUser) return;
    const saved = localStorage.getItem(getUserTasksKey());
    if (saved) {
        tasks = JSON.parse(saved);
        tasks.forEach(task => {
            if (task.due_date && task.due_date !== 'null') {
                task.due_date_display = formatDateFromGPT(task.due_date);
            } else {
                task.due_date_display = "Без срока";
            }
            if (!task.tags) task.tags = [];
        });
        console.log(`📦 Загружено ${tasks.length} задач для пользователя ${currentUser.username}`);
    } else {
        tasks = [];
    }
    applyFiltersAndRender();
}

function saveUserTasks() {
    if (!currentUser) return;
    localStorage.setItem(getUserTasksKey(), JSON.stringify(tasks));
}

// ----- 4. ФИЛЬТРАЦИЯ ЗАДАЧ -----
function filterTasksByTag(tagName) {
    if (selectedTagFilter === tagName) {
        // Если уже выбран этот тег - сбрасываем фильтр
        selectedTagFilter = null;
    } else {
        selectedTagFilter = tagName;
    }
    renderTags(); // Обновляем подсветку тегов
    applyFiltersAndRender();
}

function clearTagFilter() {
    selectedTagFilter = null;
    renderTags();
    applyFiltersAndRender();
}

function setStatusFilter(status) {
    selectedStatusFilter = status;
    // Обновляем активный класс у кнопок
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-filter') === status) {
            btn.classList.add('active');
        }
    });
    applyFiltersAndRender();
}

function getFilteredTasks() {
    let filtered = [...tasks];
    
    // Фильтр по тегу
    if (selectedTagFilter) {
        filtered = filtered.filter(task => task.tags && task.tags.includes(selectedTagFilter));
    }
    
    // Фильтр по статусу
    if (selectedStatusFilter === 'active') {
        filtered = filtered.filter(task => !task.completed);
    } else if (selectedStatusFilter === 'completed') {
        filtered = filtered.filter(task => task.completed);
    }
    
    return filtered;
}

function applyFiltersAndRender() {
    const filteredTasks = getFilteredTasks();
    renderTasks(filteredTasks);
    renderCalendar(filteredTasks);
    updateTaskCount(filteredTasks.length);
    
    // Показываем/скрываем кнопку сброса фильтра
    const clearFilterBtn = document.getElementById('clearFilterBtn');
    if (clearFilterBtn) {
        clearFilterBtn.style.display = selectedTagFilter ? 'inline-block' : 'none';
    }
}

// ----- 5. АУТЕНТИФИКАЦИЯ -----
function switchAuthTab(tab) {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const tabs = document.querySelectorAll('.auth-tab');
    
    tabs.forEach(t => t.classList.remove('active'));
    
    if (tab === 'login') {
        loginForm.style.display = 'flex';
        registerForm.style.display = 'none';
        tabs[0].classList.add('active');
    } else {
        loginForm.style.display = 'none';
        registerForm.style.display = 'flex';
        tabs[1].classList.add('active');
    }
}

async function login(event) {
    event.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    const users = getUsers();
    const user = users[email];
    
    if (user && user.password === password) {
        currentUser = user;
        userTags = user.tags || ['работа', 'учеба', 'личное', 'покупки', 'здоровье'];
        localStorage.setItem(STORAGE_KEYS.currentUser, JSON.stringify(currentUser));
        loadUserTasks();
        showUserInterface();
        renderTags();
        showNotification('Успешный вход!', 'success');
    } else {
        showNotification('Неверный email или пароль', 'error');
    }
}

async function register(event) {
    event.preventDefault();
    const username = document.getElementById('regUsername').value;
    const email = document.getElementById('regEmail').value;
    const password = document.getElementById('regPassword').value;
    const confirmPassword = document.getElementById('regConfirmPassword').value;
    
    if (password !== confirmPassword) {
        showNotification('Пароли не совпадают', 'error');
        return;
    }
    
    const users = getUsers();
    if (users[email]) {
        showNotification('Пользователь с таким email уже существует', 'error');
        return;
    }
    
    const newUser = {
        id: 'user_' + Date.now(),
        username: username,
        email: email,
        password: password,
        tags: ['работа', 'учеба', 'личное', 'покупки', 'здоровье']
    };
    
    users[email] = newUser;
    saveUsers(users);
    
    currentUser = newUser;
    userTags = newUser.tags;
    localStorage.setItem(STORAGE_KEYS.currentUser, JSON.stringify(currentUser));
    loadUserTasks();
    showUserInterface();
    renderTags();
    showNotification('Регистрация успешна!', 'success');
}

function logout() {
    currentUser = null;
    userTags = ['работа', 'учеба', 'личное', 'покупки', 'здоровье'];
    tasks = [];
    selectedTagFilter = null;
    selectedStatusFilter = 'all';
    localStorage.removeItem(STORAGE_KEYS.currentUser);
    showAuthInterface();
    applyFiltersAndRender();
    showNotification('Вы вышли из системы', 'info');
}

function showUserInterface() {
    document.getElementById('authBlock').style.display = 'none';
    document.getElementById('userPanel').style.display = 'flex';
    document.getElementById('taskFormBlock').style.display = 'block';
    document.getElementById('tagsBlock').style.display = 'block';
    document.getElementById('filterBlock').style.display = 'block';
    
    document.getElementById('userName').textContent = currentUser.username;
    document.getElementById('userEmail').textContent = currentUser.email;
}

function showAuthInterface() {
    document.getElementById('authBlock').style.display = 'flex';
    document.getElementById('userPanel').style.display = 'none';
    document.getElementById('taskFormBlock').style.display = 'none';
    document.getElementById('tagsBlock').style.display = 'none';
    document.getElementById('filterBlock').style.display = 'none';
    
    document.getElementById('loginEmail').value = '';
    document.getElementById('loginPassword').value = '';
    document.getElementById('regUsername').value = '';
    document.getElementById('regEmail').value = '';
    document.getElementById('regPassword').value = '';
    document.getElementById('regConfirmPassword').value = '';
}

// ----- 6. РАБОТА С ТЕГАМИ -----
function renderTags() {
    const container = document.getElementById('tagsList');
    if (!container) return;
    
    container.innerHTML = userTags.map(tag => `
        <div class="tag-item ${selectedTagFilter === tag ? 'active' : ''}" onclick="filterTasksByTag('${escapeHtml(tag)}')">
            <span>#${escapeHtml(tag)}</span>
            <span class="remove-tag" onclick="event.stopPropagation(); removeTag('${escapeHtml(tag)}')">×</span>
        </div>
    `).join('');
}

function showAddTagInput() {
    document.getElementById('addTagInput').classList.add('active');
    document.getElementById('newTagName').focus();
}

function hideAddTagInput() {
    document.getElementById('addTagInput').classList.remove('active');
    document.getElementById('newTagName').value = '';
}

function addTag() {
    const newTag = document.getElementById('newTagName').value.trim().toLowerCase();
    if (!newTag) {
        showNotification('Введите название тега', 'warning');
        return;
    }
    if (userTags.includes(newTag)) {
        showNotification('Такой тег уже существует', 'warning');
        return;
    }
    if (newTag.length > 20) {
        showNotification('Тег не должен превышать 20 символов', 'warning');
        return;
    }
    
    userTags.push(newTag);
    
    const users = getUsers();
    if (users[currentUser.email]) {
        users[currentUser.email].tags = userTags;
        saveUsers(users);
        currentUser.tags = userTags;
        localStorage.setItem(STORAGE_KEYS.currentUser, JSON.stringify(currentUser));
    }
    
    renderTags();
    hideAddTagInput();
    showNotification(`Тег "${newTag}" добавлен`, 'success');
}

function removeTag(tagName) {
    if (confirm(`Удалить тег "${tagName}"?`)) {
        userTags = userTags.filter(t => t !== tagName);
        
        tasks.forEach(task => {
            if (task.tags) {
                task.tags = task.tags.filter(t => t !== tagName);
            }
        });
        
        // Если удалённый тег был выбран для фильтрации - сбрасываем фильтр
        if (selectedTagFilter === tagName) {
            selectedTagFilter = null;
        }
        
        const users = getUsers();
        if (users[currentUser.email]) {
            users[currentUser.email].tags = userTags;
            saveUsers(users);
            currentUser.tags = userTags;
            localStorage.setItem(STORAGE_KEYS.currentUser, JSON.stringify(currentUser));
        }
        
        saveUserTasks();
        renderTags();
        applyFiltersAndRender();
        showNotification(`Тег "${tagName}" удалён`, 'info');
    }
}

// ----- 7. ФОРМАТИРОВАНИЕ ДАТЫ -----
function formatDateFromGPT(dateString) {
    if (!dateString || dateString === 'null') return "Без срока";
    try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return "Без срока";
        
        const now = new Date();
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        const taskDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());
        
        if (taskDate.getTime() === today.getTime()) {
            return `Сегодня в ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
        }
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
        if (taskDate.getTime() === tomorrow.getTime()) {
            return `Завтра в ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
        }
        return date.toLocaleString('ru-RU', {
            day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit'
        });
    } catch(e) {
        return "Без срока";
    }
}

// ----- 8. ПРОВЕРКА СЕРВЕРА -----
async function checkServer() {
    const statusDiv = document.getElementById('status');
    try {
        const response = await fetch(`${API_URL}/api/ai/status`);
        if (response.ok) {
            const data = await response.json();
            const aiText = data.is_real_ai ? '🤖 Yandex GPT' : '🎭 Демо-режим';
            statusDiv.innerHTML = `✅ Сервер работает (${aiText})`;
            statusDiv.className = 'status online';
            console.log("✅ Сервер доступен");
        } else {
            throw new Error();
        }
    } catch(error) {
        statusDiv.innerHTML = '⚠️ Сервер не запущен! Запустите: cd backend && python3 app.py';
        statusDiv.className = 'status offline';
        console.error("❌ Сервер недоступен");
    }
}

// ----- 9. СОЗДАНИЕ ЗАДАЧИ -----
async function createTask() {
    if (!currentUser) {
        showNotification('Войдите в систему', 'warning');
        return;
    }
    
    const text = document.getElementById('taskText').value.trim();
    if (!text) {
        alert('Введите описание задачи');
        return;
    }
    
    console.log("📤 Отправка на сервер:", text);
    
    const resultDiv = document.getElementById('result');
    resultDiv.style.display = 'block';
    resultDiv.innerHTML = '<div class="loading"><div class="spinner"></div>🤔 AI анализирует...</div>';
    
    const btn = document.getElementById('createBtn');
    btn.disabled = true;
    
    try {
        const response = await fetch(`${API_URL}/api/ai/process`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });
        
        const data = await response.json();
        console.log("📥 Данные от сервера:", data);
        
        if (data.success && data.task) {
            const displayDate = formatDateFromGPT(data.task.due_date);
            
            let tagsFromAI = data.task.tags || [];
            const validTags = tagsFromAI.filter(tag => userTags.includes(tag));
            
            const newTask = {
                id: Date.now(),
                title: data.task.title,
                due_date: data.task.due_date || null,
                due_date_display: displayDate,
                priority: data.task.priority || 'medium',
                tags: validTags,
                completed: false,
                created: new Date().toLocaleString()
            };
            
            tasks.unshift(newTask);
            saveUserTasks();
            
            const aiBadge = data.is_real_ai ? '🤖 Обработано Yandex GPT' : '🎭 Демо-режим';
            
            resultDiv.innerHTML = `
                <div class="result-card">
                    ✅ ЗАДАЧА СОЗДАНА!<br>
                    📝 <strong>${escapeHtml(newTask.title)}</strong><br>
                    📅 ${newTask.due_date_display}<br>
                    ⚠️ ${getPriorityText(newTask.priority)}<br>
                    🏷️ ${newTask.tags.map(t => '#' + t).join(' ')}<br>
                    <small>${aiBadge}</small>
                </div>
            `;
            
            document.getElementById('taskText').value = '';
            applyFiltersAndRender();
            
            setTimeout(() => {
                resultDiv.style.display = 'none';
            }, 4000);
        } else {
            throw new Error(data.error || 'Ошибка от сервера');
        }
    } catch(error) {
        console.error("❌ Ошибка:", error);
        resultDiv.innerHTML = `
            <div class="error-card">
                ❌ Ошибка: ${error.message}<br>
                Проверьте, запущен ли сервер
            </div>
        `;
    } finally {
        btn.disabled = false;
    }
}

// ----- 10. ОТОБРАЖЕНИЕ ЗАДАЧ -----
function renderTasks(tasksToRender = null) {
    const container = document.getElementById('tasksList');
    const tasksToShow = tasksToRender !== null ? tasksToRender : tasks;
    
    if (!currentUser) {
        container.innerHTML = '<div class="empty-state">✨ Войдите в систему, чтобы видеть задачи</div>';
        return;
    }
    
    if (tasksToShow.length === 0) {
        let message = '✨ Нет задач. Создайте первую!';
        if (selectedTagFilter) {
            message = `✨ Нет задач с тегом #${selectedTagFilter}`;
        } else if (selectedStatusFilter === 'active') {
            message = '✨ Нет активных задач';
        } else if (selectedStatusFilter === 'completed') {
            message = '✨ Нет выполненных задач';
        }
        container.innerHTML = `<div class="empty-state">${message}</div>`;
        return;
    }
    
    container.innerHTML = tasksToShow.map(task => `
        <div class="task-item ${task.completed ? 'completed' : ''}">
            <div class="task-title">${escapeHtml(task.title)}</div>
            <div class="task-meta">
                <span class="priority-${task.priority}">
                    ${getPriorityIcon(task.priority)} ${getPriorityText(task.priority)}
                </span>
                <span>📅 ${task.due_date_display || "Без срока"}</span>
                <span>🏷️ ${task.tags.map(t => `<span class="task-tag" onclick="filterTasksByTag('${escapeHtml(t)}')">#${escapeHtml(t)}</span>`).join(' ')}</span>
            </div>
            <div class="task-actions">
                <button class="complete-btn" onclick="toggleTask(${task.id})">
                    ${task.completed ? '↩️ Вернуть' : '✅ Выполнить'}
                </button>
                <button class="delete-btn" onclick="deleteTask(${task.id})">🗑️ Удалить</button>
            </div>
        </div>
    `).join('');
}

function toggleTask(id) {
    const task = tasks.find(t => t.id === id);
    if (task) {
        task.completed = !task.completed;
        saveUserTasks();
        applyFiltersAndRender();
        console.log(`🔄 Задача "${task.title}" ${task.completed ? 'выполнена' : 'возвращена'}`);
    }
}

function deleteTask(id) {
    if (confirm('Удалить задачу?')) {
        const task = tasks.find(t => t.id === id);
        tasks = tasks.filter(t => t.id !== id);
        saveUserTasks();
        applyFiltersAndRender();
        console.log(`🗑️ Задача "${task?.title}" удалена`);
    }
}

// ----- 11. КАЛЕНДАРЬ С ПОДСВЕТКОЙ ПО ПРИОРИТЕТУ И ФИЛЬТРАЦИЕЙ -----
function renderCalendar(tasksToRender = null) {
    const tasksForCalendar = tasksToRender !== null ? tasksToRender : getFilteredTasks();
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    
    const firstDay = new Date(year, month, 1);
    const startDay = firstDay.getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    
    document.getElementById('currentMonth').textContent = 
        `${firstDay.toLocaleString('ru-RU', { month: 'long' })} ${year}`;
    
    const calendarDays = document.getElementById('calendarDays');
    calendarDays.innerHTML = '';
    
    const prevMonthDays = startDay === 0 ? 6 : startDay - 1;
    for (let i = 0; i < prevMonthDays; i++) {
        const emptyDay = document.createElement('div');
        emptyDay.className = 'calendar-day other-month';
        calendarDays.appendChild(emptyDay);
    }
    
    const today = new Date();
    for (let day = 1; day <= daysInMonth; day++) {
        const dayDate = new Date(year, month, day);
        const dayDiv = document.createElement('div');
        dayDiv.className = 'calendar-day';
        
        if (dayDate.toDateString() === today.toDateString()) {
            dayDiv.classList.add('today');
        }
        
        const dayNumber = document.createElement('div');
        dayNumber.className = 'day-number';
        dayNumber.textContent = day;
        dayDiv.appendChild(dayNumber);
        
        const dayTasksDiv = document.createElement('div');
        dayTasksDiv.className = 'day-tasks';
        
        const dayTasks = tasksForCalendar.filter(task => {
            if (!task.due_date || task.due_date === null || task.due_date === 'null') return false;
            const taskDate = new Date(task.due_date);
            if (isNaN(taskDate.getTime())) return false;
            return taskDate.toDateString() === dayDate.toDateString();
        });
        
        dayTasks.forEach(task => {
            const taskDiv = document.createElement('div');
            taskDiv.className = `day-task priority-${task.priority}`;
            if (task.completed) taskDiv.classList.add('completed');
            taskDiv.textContent = task.title.length > 20 ? 
                task.title.substring(0, 20) + '...' : task.title;
            taskDiv.onclick = (e) => {
                e.stopPropagation();
                openEditModal(task.id);
                if (window.innerWidth <= 768) {
                    document.getElementById('leftPanel').classList.remove('open');
                }
            };
            dayTasksDiv.appendChild(taskDiv);
        });
        
        dayDiv.appendChild(dayTasksDiv);
        calendarDays.appendChild(dayDiv);
    }
}

function prevMonth() {
    currentDate.setMonth(currentDate.getMonth() - 1);
    renderCalendar();
}

function nextMonth() {
    currentDate.setMonth(currentDate.getMonth() + 1);
    renderCalendar();
}

// ----- 12. РЕДАКТИРОВАНИЕ ЗАДАЧИ -----
function openEditModal(id) {
    const task = tasks.find(t => t.id === id);
    if (!task) return;
    
    editingTaskId = id;
    document.getElementById('editTitle').value = task.title;
    document.getElementById('editDate').value = task.due_date ? task.due_date.slice(0, 16) : '';
    document.getElementById('editPriority').value = task.priority;
    
    const editTagsContainer = document.getElementById('editTagsList');
    editTagsContainer.innerHTML = userTags.map(tag => `
        <span class="task-tag" style="background: ${task.tags.includes(tag) ? '#667eea' : '#e9ecef'}; color: ${task.tags.includes(tag) ? 'white' : '#333'}; cursor: pointer;" onclick="toggleTagInEdit('${escapeHtml(tag)}')">
            #${escapeHtml(tag)}
        </span>
    `).join('');
    
    document.getElementById('editModal').classList.add('active');
}

function toggleTagInEdit(tagName) {
    const task = tasks.find(t => t.id === editingTaskId);
    if (task) {
        if (task.tags.includes(tagName)) {
            task.tags = task.tags.filter(t => t !== tagName);
        } else {
            task.tags.push(tagName);
        }
        const editTagsContainer = document.getElementById('editTagsList');
        editTagsContainer.innerHTML = userTags.map(tag => `
            <span class="task-tag" style="background: ${task.tags.includes(tag) ? '#667eea' : '#e9ecef'}; color: ${task.tags.includes(tag) ? 'white' : '#333'}; cursor: pointer;" onclick="toggleTagInEdit('${escapeHtml(tag)}')">
                #${escapeHtml(tag)}
            </span>
        `).join('');
    }
}

function saveEdit() {
    const task = tasks.find(t => t.id === editingTaskId);
    if (task) {
        task.title = document.getElementById('editTitle').value;
        task.due_date = document.getElementById('editDate').value;
        task.priority = document.getElementById('editPriority').value;
        
        if (task.due_date) {
            task.due_date_display = formatDateFromGPT(task.due_date);
        } else {
            task.due_date_display = "Без срока";
        }
        
        saveUserTasks();
        applyFiltersAndRender();
        showNotification('Задача обновлена', 'success');
    }
    closeModal();
}

function closeModal() {
    document.getElementById('editModal').classList.remove('active');
    editingTaskId = null;
}

function updateTaskCount(count) {
    const taskCountElement = document.getElementById('taskCount');
    if (taskCountElement) {
        taskCountElement.textContent = count !== undefined ? count : tasks.length;
    }
}

// ----- 13. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ -----
function getPriorityText(priority) {
    const texts = { 'high': 'Высокий', 'medium': 'Средний', 'low': 'Низкий' };
    return texts[priority] || 'Средний';
}

function getPriorityIcon(priority) {
    const icons = { 'high': '🔴', 'medium': '🟡', 'low': '🟢' };
    return icons[priority] || '🟡';
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showNotification(message, type) {
    const resultDiv = document.getElementById('result');
    resultDiv.style.display = 'block';
    resultDiv.innerHTML = `
        <div class="${type === 'error' ? 'error-card' : 'result-card'}" style="background: ${type === 'success' ? '#d4edda' : type === 'error' ? '#f8d7da' : '#d4edda'}">
            ${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'} ${message}
        </div>
    `;
    setTimeout(() => {
        resultDiv.style.display = 'none';
        resultDiv.innerHTML = '';
    }, 3000);
}

function toggleMobileMenu() {
    document.getElementById('leftPanel').classList.toggle('open');
}

document.addEventListener('click', function(event) {
    const panel = document.getElementById('leftPanel');
    const menuBtn = document.querySelector('.mobile-menu-btn');
    if (window.innerWidth <= 768 && panel.classList.contains('open')) {
        if (!panel.contains(event.target) && !menuBtn.contains(event.target)) {
            panel.classList.remove('open');
        }
    }
});

// ----- 14. ЗАПУСК -----
document.addEventListener('DOMContentLoaded', init);