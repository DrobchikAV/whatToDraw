document.addEventListener('DOMContentLoaded', function() {
    // Элементы
    const colorDisplay = document.getElementById('colorDisplay');
    const colorName = document.getElementById('colorName');
    const colorHex = document.getElementById('colorHex');
    const colorCopyBtn = document.getElementById('colorCopyBtn');
    const newColorBtn = document.getElementById('newColorBtn');

    const randomWord = document.getElementById('randomWord');
    const newWordBtn = document.getElementById('newWordBtn');

    const challengeCategory = document.getElementById('challengeCategory');
    const challengeName = document.getElementById('challengeName');
    const challengeContent = document.getElementById('challengeContent');
    const newChallengeBtn = document.getElementById('newChallengeBtn');

    const newAllBtn = document.getElementById('newAllBtn');

    // Переменные для таймера
    let timerInterval = null;
    let timeLeft = 0;
    let isTimerRunning = false;
    let totalTime = 0;

    // Уведомления
    function showNotification(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 1050; min-width: 300px;';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(alertDiv);

        setTimeout(() => alertDiv.remove(), 2000);
    }

    // Функция для парсинга времени из описания
    function parseTimeFromDescription(description) {
        if (!description || description.trim() === '') {
            return 300; // По умолчанию 5 минут
        }

        description = description.trim();

        // Если формат "минуты:секунды"
        if (description.includes(':')) {
            const parts = description.split(':');
            const minutes = parseInt(parts[0]) || 0;
            const seconds = parseInt(parts[1]) || 0;
            return minutes * 60 + seconds;
        }
        // Если просто целое число (минуты)
        else {
            const minutes = parseInt(description) || 5;
            return minutes * 60;
        }
    }

    // Функция для форматирования времени в MM:SS
    function formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }

    // Функции для работы с таймером
    function initializeTimer(description) {
        // Останавливаем существующий таймер
        stopTimer();

        // Парсим время из описания
        totalTime = parseTimeFromDescription(description);

        // Проверяем, что время валидное
        if (totalTime <= 0) {
            totalTime = 300; // 5 минут по умолчанию
        }

        timeLeft = totalTime;

        // Обновляем отображение
        updateTimerDisplay();

        // Устанавливаем кнопку старт/пауза в состояние "Старт"
        const startPauseBtn = document.getElementById('startPauseTimerBtn');
        if (startPauseBtn) {
            startPauseBtn.innerHTML = '<i class="bi bi-play-fill"></i> Старт';
            startPauseBtn.disabled = false;
            startPauseBtn.classList.remove('btn-warning');
            startPauseBtn.classList.add('btn-danger');
        }
    }

    function updateTimerDisplay() {
        const timerDisplay = document.getElementById('timerDisplay');
        if (!timerDisplay) return;

        timerDisplay.textContent = formatTime(timeLeft);
    }

    function toggleTimer() {
        const startPauseBtn = document.getElementById('startPauseTimerBtn');

        if (!isTimerRunning) {
            // Запускаем таймер
            if (timeLeft <= 0) return;

            isTimerRunning = true;
            startPauseBtn.innerHTML = '<i class="bi bi-pause-fill"></i> Пауза';
            startPauseBtn.classList.remove('btn-danger');
            startPauseBtn.classList.add('btn-warning');

            timerInterval = setInterval(() => {
                timeLeft--;
                updateTimerDisplay();

                if (timeLeft <= 0) {
                    stopTimer();
                    showNotification('<i class="bi bi-alarm me-1"></i>Время вышло!', 'danger');
                    startPauseBtn.disabled = true;
                    startPauseBtn.classList.remove('btn-warning');
                    startPauseBtn.classList.add('btn-secondary');
                }
            }, 1000);
        } else {
            // Ставим на паузу
            isTimerRunning = false;
            clearInterval(timerInterval);
            startPauseBtn.innerHTML = '<i class="bi bi-play-fill"></i> Продолжить';
            startPauseBtn.classList.remove('btn-warning');
            startPauseBtn.classList.add('btn-danger');
        }
    }

    function stopTimer() {
        isTimerRunning = false;
        clearInterval(timerInterval);
        timerInterval = null;
    }

    function resetTimer() {
        stopTimer();
        timeLeft = totalTime;
        updateTimerDisplay();

        const startPauseBtn = document.getElementById('startPauseTimerBtn');
        if (startPauseBtn) {
            startPauseBtn.innerHTML = '<i class="bi bi-play-fill"></i> Старт';
            startPauseBtn.disabled = false;
            startPauseBtn.classList.remove('btn-warning', 'btn-secondary');
            startPauseBtn.classList.add('btn-danger');
        }
    }

    // Инициализация таймера при загрузке страницы
    function initPageTimer() {
        if (challengeCategory && challengeCategory.textContent.includes('Временное ограничение')) {
            const timeDescriptionInput = document.getElementById('timeDescription');
            const challengeDescription = document.getElementById('challengeDescription');

            // Получаем описание из скрытого поля или из текстового элемента
            let timeDescription = '';
            if (timeDescriptionInput && timeDescriptionInput.value) {
                timeDescription = timeDescriptionInput.value;
            } else if (challengeDescription && challengeDescription.textContent) {
                timeDescription = challengeDescription.textContent;
            }

            if (timeDescription) {
                // Обновляем таймер
                const timerDisplay = document.getElementById('timerDisplay');
                if (timerDisplay) {
                    const initialTime = parseTimeFromDescription(timeDescription);
                    timerDisplay.textContent = formatTime(initialTime);
                }

                initializeTimer(timeDescription);
            }
        }
    }

    // Инициализируем таймер при загрузке страницы
    initPageTimer();

    // Обработчики для таймера
    document.addEventListener('click', function(e) {
        if (e.target.id === 'startPauseTimerBtn' || e.target.closest('#startPauseTimerBtn')) {
            toggleTimer();
        } else if (e.target.id === 'resetTimerBtn' || e.target.closest('#resetTimerBtn')) {
            resetTimer();
        }
    });

    // Копирование цвета
    if (colorCopyBtn) {
        colorCopyBtn.addEventListener('click', async function() {
            try {
                await navigator.clipboard.writeText(colorHex.textContent);
                showNotification(`<i class="bi bi-check-circle me-1"></i>Скопирован: ${colorHex.textContent}`, 'success');
                colorCopyBtn.innerHTML = '<i class="bi bi-check"></i>';
                setTimeout(() => {
                    colorCopyBtn.innerHTML = '<i class="bi bi-clipboard"></i>';
                }, 1000);
            } catch (err) {
                showNotification('<i class="bi bi-exclamation-triangle me-1"></i>Не удалось скопировать', 'danger');
            }
        });
    }

    // Получить новый цвет
    async function fetchNewColor() {
        try {
            newColorBtn.disabled = true;
            newColorBtn.innerHTML = '<i class="bi bi-hourglass-split me-1"></i>Загрузка...';

            const response = await fetch('/api/random-color');
            if (!response.ok) throw new Error('Network error');

            const color = await response.json();

            // Анимация
            colorDisplay.classList.add('pulse');
            setTimeout(() => {
                colorDisplay.style.backgroundColor = color.hex;
                colorName.textContent = color.name;
                colorHex.textContent = color.hex;
                colorDisplay.classList.remove('pulse');

                showNotification(`<i class="bi bi-palette me-1"></i>Новый цвет: ${color.name}`, 'info');
                newColorBtn.innerHTML = '<i class="bi bi-arrow-clockwise me-2"></i>Новый цвет';
                newColorBtn.disabled = false;
            }, 300);

        } catch (error) {
            showNotification('<i class="bi bi-exclamation-triangle me-1"></i>Ошибка при загрузке цвета', 'danger');
            newColorBtn.innerHTML = '<i class="bi bi-arrow-clockwise me-2"></i>Новый цвет';
            newColorBtn.disabled = false;
        }
    }

    // Получить новое слово
    async function fetchNewWord() {
        try {
            newWordBtn.disabled = true;
            newWordBtn.innerHTML = '<i class="bi bi-hourglass-split me-1"></i>Загрузка...';

            const response = await fetch('/api/random-word');
            if (!response.ok) throw new Error('Network error');

            const data = await response.json();

            // Анимация
            randomWord.classList.add('pulse');
            setTimeout(() => {
                randomWord.textContent = data.word;
                randomWord.classList.remove('pulse');

                showNotification(`<i class="bi bi-chat-square-text me-1"></i>Новое слово: ${data.word}`, 'success');
                newWordBtn.innerHTML = '<i class="bi bi-arrow-clockwise me-2"></i>Новое слово';
                newWordBtn.disabled = false;
            }, 300);

        } catch (error) {
            showNotification('<i class="bi bi-exclamation-triangle me-1"></i>Ошибка при загрузке слова', 'danger');
            newWordBtn.innerHTML = '<i class="bi bi-arrow-clockwise me-2"></i>Новое слово';
            newWordBtn.disabled = false;
        }
    }

    // Получить новое усложнение
    async function fetchNewChallenge() {
        try {
            newChallengeBtn.disabled = true;
            newChallengeBtn.innerHTML = '<i class="bi bi-hourglass-split me-1"></i>Загрузка...';

            const response = await fetch('/api/random-challenge');
            if (!response.ok) throw new Error('Network error');

            const challenge = await response.json();

            // Останавливаем таймер, если он был запущен
            stopTimer();

            // Анимация
            if (challengeName) challengeName.classList.add('pulse');
            setTimeout(() => {
                // Обновляем категорию с правильным классом
                let categoryClass = 'bg-secondary';
                let icon = '';
                if (challenge.category === 'Временное ограничение') {
                    categoryClass = 'time-category';
                    icon = '⏱️ ';
                } else if (challenge.category === 'Художественный стиль') {
                    categoryClass = 'style-category';
                    icon = '🎭 ';
                } else if (challenge.category === 'Композиция рисунка') {
                    categoryClass = 'composition-category';
                    icon = '📐 ';
                }

                if (challengeCategory) {
                    challengeCategory.className = `category-badge ${categoryClass}`;
                    challengeCategory.textContent = icon + challenge.category;
                }
                if (challengeName) challengeName.textContent = challenge.name;

                // Обновляем контент в зависимости от категории
                if (challenge.category === 'Временное ограничение') {
                    // Создаем HTML для таймера
                    if (challengeContent) {
                        challengeContent.innerHTML = `
                            <div class="timer-container text-center">
                                <div class="timer-display mb-3">
                                    <div class="display-4 fw-bold text-dark" id="timerDisplay">${formatTime(parseTimeFromDescription(challenge.description))}</div>
                                </div>
                                <div class="timer-controls">
                                    <button class="btn btn-sm btn-danger me-2" id="startPauseTimerBtn">
                                        <i class="bi bi-play-fill"></i> Старт
                                    </button>
                                    <button class="btn btn-sm btn-outline-secondary" id="resetTimerBtn">
                                        <i class="bi bi-arrow-clockwise"></i> Сброс
                                    </button>
                                </div>
                                <input type="hidden" id="timeDescription" value="${challenge.description}">
                            </div>
                        `;
                    }

                    // Инициализируем таймер
                    initializeTimer(challenge.description);

                } else {
                    // Обычное описание для других категорий
                    if (challengeContent) {
                        challengeContent.innerHTML = `<p class="text-muted fade-in" id="challengeDescription">${challenge.description}</p>`;
                    }
                }

                if (challengeName) challengeName.classList.remove('pulse');

                showNotification(`<i class="bi bi-lightning-charge me-1"></i>Новое усложнение: ${challenge.name}`, 'warning');
                newChallengeBtn.innerHTML = '<i class="bi bi-arrow-clockwise me-2"></i>Новое усложнение';
                newChallengeBtn.disabled = false;
            }, 300);

        } catch (error) {
            showNotification('<i class="bi bi-exclamation-triangle me-1"></i>Ошибка при загрузке усложнения', 'danger');
            newChallengeBtn.innerHTML = '<i class="bi bi-arrow-clockwise me-2"></i>Новое усложнение';
            newChallengeBtn.disabled = false;
        }
    }

    // Получить всё новое
    async function fetchNewAll() {
        try {
            newAllBtn.disabled = true;
            newAllBtn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Генерация...';

            const response = await fetch('/api/random-all');
            if (!response.ok) throw new Error('Network error');

            const data = await response.json();

            // Останавливаем таймер, если он был запущен
            stopTimer();

            // Анимация всех элементов
            colorDisplay.classList.add('pulse');
            randomWord.classList.add('pulse');
            if (challengeName) challengeName.classList.add('pulse');

            setTimeout(() => {
                // Обновляем цвет
                colorDisplay.style.backgroundColor = data.color.hex;
                colorName.textContent = data.color.name;
                colorHex.textContent = data.color.hex;
                colorDisplay.classList.remove('pulse');

                // Обновляем слово
                randomWord.textContent = data.word;
                randomWord.classList.remove('pulse');

                // Обновляем усложнение
                let categoryClass = 'bg-secondary';
                let icon = '';
                if (data.challenge.category === 'Временное ограничение') {
                    categoryClass = 'time-category';
                    icon = '⏱️ ';
                } else if (data.challenge.category === 'Художественный стиль') {
                    categoryClass = 'style-category';
                    icon = '🎭 ';
                } else if (data.challenge.category === 'Композиция рисунка') {
                    categoryClass = 'composition-category';
                    icon = '📐 ';
                }

                if (challengeCategory) {
                    challengeCategory.className = `category-badge ${categoryClass}`;
                    challengeCategory.textContent = icon + data.challenge.category;
                }
                if (challengeName) challengeName.textContent = data.challenge.name;

                // Обновляем контент в зависимости от категории
                if (data.challenge.category === 'Временное ограничение') {
                    // Создаем HTML для таймера
                    if (challengeContent) {
                        challengeContent.innerHTML = `
                            <div class="timer-container text-center">
                                <div class="timer-display mb-3">
                                    <div class="display-4 fw-bold text-dark" id="timerDisplay">${formatTime(parseTimeFromDescription(data.challenge.description))}</div>
                                </div>
                                <div class="timer-controls">
                                    <button class="btn btn-sm btn-danger me-2" id="startPauseTimerBtn">
                                        <i class="bi bi-play-fill"></i> Старт
                                    </button>
                                    <button class="btn btn-sm btn-outline-secondary" id="resetTimerBtn">
                                        <i class="bi bi-arrow-clockwise"></i> Сброс
                                    </button>
                                </div>
                                <input type="hidden" id="timeDescription" value="${data.challenge.description}">
                            </div>
                        `;
                    }

                    // Инициализируем таймер
                    initializeTimer(data.challenge.description);

                } else {
                    // Обычное описание для других категорий
                    if (challengeContent) {
                        challengeContent.innerHTML = `<p class="text-muted fade-in" id="challengeDescription">${data.challenge.description}</p>`;
                    }
                }

                if (challengeName) challengeName.classList.remove('pulse');

                showNotification(`<i class="bi bi-stars me-1"></i>Всё сгенерировано заново!`, 'success');
                newAllBtn.innerHTML = '<i class="bi bi-shuffle me-2"></i>Сгенерировать всё заново';
                newAllBtn.disabled = false;
            }, 300);

        } catch (error) {
            showNotification('<i class="bi bi-exclamation-triangle me-1"></i>Ошибка при генерации', 'danger');
            newAllBtn.innerHTML = '<i class="bi bi-shuffle me-2"></i>Сгенерировать всё заново';
            newAllBtn.disabled = false;
        }
    }

    // Обработчики кнопок
    if (newColorBtn) newColorBtn.addEventListener('click', fetchNewColor);
    if (newWordBtn) newWordBtn.addEventListener('click', fetchNewWord);
    if (newChallengeBtn) newChallengeBtn.addEventListener('click', fetchNewChallenge);
    if (newAllBtn) newAllBtn.addEventListener('click', fetchNewAll);

    // Подсказки
    if (newColorBtn) newColorBtn.title = 'Сгенерировать новый случайный цвет';
    if (newWordBtn) newWordBtn.title = 'Сгенерировать новое случайное слово';
    if (newChallengeBtn) newChallengeBtn.title = 'Сгенерировать новое случайное усложнение';
    if (newAllBtn) newAllBtn.title = 'Сгенерировать новое сочетание цвета, слова и усложнения';
    if (colorCopyBtn) colorCopyBtn.title = 'Скопировать HEX код цвета';
});