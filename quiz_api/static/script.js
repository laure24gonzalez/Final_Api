const API_BASE_URL = 'http://localhost:8000';

let currentQuizSession = null;
let currentQuestions = [];
let currentAnswers = {};
let currentQuestionIndex = 0;

document.addEventListener('DOMContentLoaded', function() {
    setupNavigationListeners();
    setupFormListeners();
    loadInitialStats();
});

function setupFormListeners() {
    const createQuestionForm = document.getElementById('create-question-form');
    if (createQuestionForm) {
        createQuestionForm.addEventListener('submit', handleCreateQuestion);
    }
}

function setupNavigationListeners() {
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const section = this.dataset.section;
            goToSection(section);
        });
    });
}

function goToSection(sectionId) {
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });

    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    const section = document.getElementById(sectionId);
    if (section) {
        section.classList.add('active');
    }

    document.querySelector(`[data-section="${sectionId}"]`).classList.add('active');

    if (sectionId === 'preguntas') {
        loadQuestions();
    } else if (sectionId === 'estadisticas') {
        loadStatistics();
    } else if (sectionId === 'sesiones') {
        loadSessions();
    }
}

// ==================== Home Section ====================
function loadInitialStats() {
    fetchGlobalStats();
}

async function startQuiz() {
    const username = document.getElementById('username').value || 'Anónimo';
    const numQuestions = parseInt(document.getElementById('num-questions').value) || 5;

    try {
        // Crea nueva sesión
        const sessionResponse = await fetch(`${API_BASE_URL}/quiz-sessions/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                usuario_nombre: username
            })
        });

        if (!sessionResponse.ok) throw new Error('Error al crear sesión');
        currentQuizSession = await sessionResponse.json();

        // Obtiene preguntas aleatorias
        const questionsResponse = await fetch(
            `${API_BASE_URL}/questions/random?limit=${numQuestions}`
        );

        if (!questionsResponse.ok) throw new Error('Error al cargar preguntas');
        currentQuestions = await questionsResponse.json();
        currentAnswers = {};
        currentQuestionIndex = 0;

        // Muestra el quiz
        document.getElementById('quiz-start').classList.add('hidden');
        document.getElementById('quiz-results').classList.add('hidden');
        document.getElementById('quiz-content').classList.remove('hidden');

        document.getElementById('total-question').textContent = currentQuestions.length;
        loadQuestion();

    } catch (error) {
        alert('Error: ' + error.message);
    }
}

function loadQuestion() {
    if (currentQuestionIndex >= currentQuestions.length) {
        return;
    }

    const question = currentQuestions[currentQuestionIndex];
    document.getElementById('current-question').textContent = currentQuestionIndex + 1;

    const container = document.getElementById('question-container');
    
    let optionsHTML = '<div class="options">';
    question.opciones.forEach((opcion, index) => {
        const isSelected = currentAnswers[question.id] === index;
        const selectedClass = isSelected ? 'selected' : '';
        optionsHTML += `
            <label class="option ${selectedClass}">
                <input type="radio" name="answer" value="${index}" 
                       ${isSelected ? 'checked' : ''} 
                       onchange="selectAnswer(${question.id}, ${index})">
                <span>${opcion}</span>
            </label>
        `;
    });
    optionsHTML += '</div>';

    container.innerHTML = `
        <h4>Pregunta ${currentQuestionIndex + 1}</h4>
        <p><strong>${question.pregunta}</strong></p>
        ${optionsHTML}
        <p style="margin-top: 15px; font-size: 0.9rem; color: #7f8c8d;">
            <em>Categoría: <strong>${question.categoria}</strong> | 
            Dificultad: <strong>${question.dificultad}</strong></em>
        </p>
    `;

    // Update button states
    updateQuizButtons();
}

function selectAnswer(questionId, optionIndex) {
    currentAnswers[questionId] = optionIndex;
    
    const options = document.querySelectorAll('.option');
    options.forEach(opt => {
        opt.classList.remove('selected');
        const radio = opt.querySelector('input[type="radio"]');
        if (radio.value == optionIndex && radio.name === 'answer') {
            opt.classList.add('selected');
        }
    });
}

function nextQuestion() {
    if (currentQuestionIndex < currentQuestions.length - 1) {
        currentQuestionIndex++;
        loadQuestion();
    }
}

function previousQuestion() {
    if (currentQuestionIndex > 0) {
        currentQuestionIndex--;
        loadQuestion();
    }
}

function updateQuizButtons() {
    const nextBtn = document.getElementById('next-btn');
    const finishBtn = document.getElementById('finish-btn');
    const prevBtn = document.querySelector('.quiz-buttons .btn-secondary');

    if (currentQuestionIndex === currentQuestions.length - 1) {
        nextBtn.classList.add('hidden');
        finishBtn.classList.remove('hidden');
    } else {
        nextBtn.classList.remove('hidden');
        finishBtn.classList.add('hidden');
    }

    if (currentQuestionIndex === 0) {
        prevBtn.disabled = true;
    } else {
        prevBtn.disabled = false;
    }
}

async function finishQuiz() {
    try {
        // Register all answers
        for (const questionId in currentAnswers) {
            const question = currentQuestions.find(q => q.id == questionId);
            const optionIndex = currentAnswers[questionId];

            await fetch(`${API_BASE_URL}/answers/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    quiz_session_id: currentQuizSession.id,
                    question_id: parseInt(questionId),
                    respuesta_seleccionada: optionIndex,
                    tiempo_respuesta_segundos: 10
                })
            });
        }

        // Complete session
        const completeResponse = await fetch(
            `${API_BASE_URL}/quiz-sessions/${currentQuizSession.id}/complete`,
            {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                }
            }
        );

        if (!completeResponse.ok) throw new Error('Error al completar sesión');
        
        const completedSession = await completeResponse.json();

        // Get session statistics
        const statsResponse = await fetch(
            `${API_BASE_URL}/statistics/session/${currentQuizSession.id}`
        );

        if (!statsResponse.ok) throw new Error('Error al cargar estadísticas');
        const stats = await statsResponse.json();

        // Show results
        showResults(stats);

    } catch (error) {
        alert('Error: ' + error.message);
    }
}

function showResults(stats) {
    document.getElementById('quiz-content').classList.add('hidden');
    document.getElementById('quiz-results').classList.remove('hidden');

    document.getElementById('final-score').textContent = `${stats.puntuacion_final}%`;
    document.getElementById('correct-answers').textContent = stats.preguntas_correctas;
    document.getElementById('total-answered').textContent = stats.preguntas_respondidas;
    document.getElementById('total-time').textContent = `${stats.tiempo_total_segundos || 0}s`;

    // Show answer details
    let detailsHTML = '';
    stats.resumen_respuestas.forEach((resp, index) => {
        const question = currentQuestions.find(q => q.id === resp.question_id);
        const correctClass = resp.es_correcta ? 'correct' : 'incorrect';
        const correctIcon = resp.es_correcta ? '✓' : '✗';

        detailsHTML += `
            <div class="result-detail-item ${correctClass}">
                <h5>${correctIcon} Pregunta ${index + 1}: ${resp.pregunta}</h5>
                <p><strong>Tu respuesta:</strong> ${question.opciones[resp.respuesta_seleccionada]}</p>
                ${!resp.es_correcta ? `<p><strong>Respuesta correcta:</strong> ${question.opciones[question.respuesta_correcta]}</p>` : ''}
                <p style="font-size: 0.85rem;">Tiempo: ${resp.tiempo_segundos}s</p>
            </div>
        `;
    });

    document.getElementById('results-details').innerHTML = detailsHTML;
}

// ==================== Questions Section ====================
async function loadQuestions() {
    const category = document.getElementById('filter-category').value;
    const difficulty = document.getElementById('filter-difficulty').value;

    let url = `${API_BASE_URL}/questions/?limit=50`;
    if (category) url += `&categoria=${category}`;
    if (difficulty) url += `&dificultad=${difficulty}`;

    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error('Error al cargar preguntas');
        const questions = await response.json();

        const container = document.getElementById('questions-list');
        
        if (questions.length === 0) {
            container.innerHTML = '<p class="loading">No se encontraron preguntas</p>';
            return;
        }

        let html = '';
        questions.forEach(q => {
            const difficultyClass = q.dificultad.toLowerCase();
            html += `
                <div class="question-item" id="question-${q.id}">
                    <div class="question-header">
                        <div class="question-content">
                            <h4>${q.pregunta}</h4>
                            <p>${q.explicacion || 'Sin explicación'}</p>
                            <div class="meta">
                                <span class="meta-item">📁 ${q.categoria}</span>
                                <span class="badge ${difficultyClass}">
                                    ${q.dificultad}
                                </span>
                                <span class="meta-item">📝 ${q.opciones.length} opciones</span>
                            </div>
                        </div>
                    </div>
                    <div class="question-actions">
                        <button class="btn btn-primary btn-sm" onclick="editQuestion(${q.id})">
                            ✏️ Editar
                        </button>
                        <button class="btn btn-danger btn-sm" onclick="deleteQuestion(${q.id}, '${q.pregunta.replace(/'/g, "\\'")}')">
                            🗑️ Eliminar
                        </button>
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;

    } catch (error) {
        document.getElementById('questions-list').innerHTML = 
            `<p class="loading">Error: ${error.message}</p>`;
    }
}

// ==================== Statistics Section ====================
async function loadStatistics() {
    try {
        // Global stats
        const globalResponse = await fetch(`${API_BASE_URL}/statistics/global`);
        if (!globalResponse.ok) throw new Error('Error al cargar estadísticas globales');
        const global = await globalResponse.json();

        document.getElementById('stat-active-questions').textContent = global.total_preguntas_activas;
        document.getElementById('stat-completed-sessions').textContent = global.total_sesiones_completadas;
        document.getElementById('stat-avg-score').textContent = `${global.promedio_aciertos}%`;

        // Difficult questions
        const difficultResponse = await fetch(`${API_BASE_URL}/statistics/questions/difficult?limit=5`);
        if (!difficultResponse.ok) throw new Error('Error al cargar preguntas difíciles');
        const difficult = await difficultResponse.json();

        let difficultHTML = '';
        if (difficult.length === 0) {
            difficultHTML = '<p class="loading">Sin datos aún</p>';
        } else {
            difficult.forEach(q => {
                difficultHTML += `
                    <div class="question-item">
                        <h4>${q.pregunta}</h4>
                        <div class="meta">
                            <span class="meta-item">📊 Tasa de error: ${q.tasa_error}%</span>
                            <span class="meta-item">📈 Respondida ${q.veces_respondida} veces</span>
                            <span class="meta-item">❌ ${q.veces_incorrecta} incorrectas</span>
                        </div>
                    </div>
                `;
            });
        }
        document.getElementById('difficult-questions').innerHTML = difficultHTML;

        // Categories stats
        const categoriesResponse = await fetch(`${API_BASE_URL}/statistics/categories`);
        if (!categoriesResponse.ok) throw new Error('Error al cargar categorías');
        const categories = await categoriesResponse.json();

        let categoriesHTML = '';
        if (categories.length === 0) {
            categoriesHTML = '<p class="loading">Sin datos aún</p>';
        } else {
            categories.forEach(cat => {
                const progressPercent = Math.min(100, Math.max(0, cat.promedio_aciertos));
                categoriesHTML += `
                    <div class="category-item">
                        <h4>${cat.categoria}</h4>
                        <div class="meta">
                            <span class="meta-item">📚 ${cat.num_preguntas} preguntas</span>
                            <span class="meta-item">📊 ${cat.num_respuestas} respuestas</span>
                            <span class="meta-item">✓ ${cat.aciertos} correctas</span>
                        </div>
                        <div style="margin-top: 10px; background: #ecf0f1; height: 8px; border-radius: 4px; overflow: hidden;">
                            <div style="background: #3498db; height: 100%; width: ${progressPercent}%;"></div>
                        </div>
                        <p style="margin-top: 8px; font-weight: 600; color: #3498db;">
                            ${cat.promedio_aciertos}% de aciertos
                        </p>
                    </div>
                `;
            });
        }
        document.getElementById('categories-stats').innerHTML = categoriesHTML;

    } catch (error) {
        console.error(error);
        alert('Error: ' + error.message);
    }
}

async function fetchGlobalStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/statistics/global`);
        if (!response.ok) throw new Error('Error al cargar estadísticas');
        const stats = await response.json();

        document.getElementById('total-questions').textContent = stats.total_preguntas_activas;
        document.getElementById('total-sessions').textContent = stats.total_sesiones_completadas;
        document.getElementById('avg-score').textContent = `${stats.promedio_aciertos}%`;

    } catch (error) {
        console.error(error);
    }
}

// ==================== Sessions Section ====================
async function loadSessions() {
    try {
        const response = await fetch(`${API_BASE_URL}/quiz-sessions/?limit=50`);
        if (!response.ok) throw new Error('Error al cargar sesiones');
        const sessions = await response.json();

        const container = document.getElementById('sessions-list');

        if (sessions.length === 0) {
            container.innerHTML = '<p class="loading">No hay sesiones registradas</p>';
            return;
        }

        let html = '';
        sessions.forEach(s => {
            const startDate = new Date(s.fecha_inicio).toLocaleDateString('es-ES');
            const endDate = s.fecha_fin ? new Date(s.fecha_fin).toLocaleDateString('es-ES') : 'N/A';
            const statusClass = s.estado === 'completado' ? 'success' : '';
            
            html += `
                <div class="session-item">
                    <h4>${s.usuario_nombre || 'Anónimo'}</h4>
                    <p><strong>Estado:</strong> <span class="badge ${statusClass}">${s.estado}</span></p>
                    <div class="meta">
                        <span class="meta-item">📅 Inicio: ${startDate}</span>
                        <span class="meta-item">🏁 Fin: ${endDate}</span>
                        ${s.estado === 'completado' ? `
                            <span class="meta-item">⭐ Puntuación: ${s.puntuacion_total}%</span>
                            <span class="meta-item">✓ ${s.preguntas_correctas}/${s.preguntas_respondidas}</span>
                        ` : ''}
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;

    } catch (error) {
        document.getElementById('sessions-list').innerHTML = 
            `<p class="loading">Error: ${error.message}</p>`;
    }
}

// ==================== Utility Functions ====================
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES') + ' ' + date.toLocaleTimeString('es-ES');
}

function formatTime(seconds) {
    if (!seconds) return '0s';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
}

// ==================== Create Question Functions ====================
async function handleCreateQuestion(event) {
    event.preventDefault();

    const messageDiv = document.getElementById('create-question-message');
    messageDiv.classList.add('hidden');

    const pregunta = document.getElementById('q-pregunta').value.trim();
    const categoria = document.getElementById('q-categoria').value;
    const dificultad = document.getElementById('q-dificultad').value;
    const opcion1 = document.getElementById('q-opcion-1').value.trim();
    const opcion2 = document.getElementById('q-opcion-2').value.trim();
    const opcion3 = document.getElementById('q-opcion-3').value.trim();
    const opcion4 = document.getElementById('q-opcion-4').value.trim();
    const respuestaCorrecta = parseInt(document.getElementById('q-respuesta-correcta').value);
    const explicacion = document.getElementById('q-explicacion').value.trim();

    // Validaciones básicas
    if (!pregunta || !categoria || !dificultad) {
        showMessage('Error: Completa todos los campos requeridos', 'error');
        return;
    }

    if (!opcion1 || !opcion2 || !opcion3 || !opcion4) {
        showMessage('Error: Todas las 4 opciones son requeridas', 'error');
        return;
    }

    if (isNaN(respuestaCorrecta) || respuestaCorrecta < 0 || respuestaCorrecta > 3) {
        showMessage('Error: Selecciona una respuesta correcta válida', 'error');
        return;
    }

    // Prepara los datos
    const questionData = {
        pregunta: pregunta,
        opciones: [opcion1, opcion2, opcion3, opcion4],
        respuesta_correcta: respuestaCorrecta,
        explicacion: explicacion || null,
        categoria: categoria,
        dificultad: dificultad
    };

    try {
        // Envía a la API
        const response = await fetch(`${API_BASE_URL}/questions/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(questionData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Error al crear la pregunta');
        }

        const createdQuestion = await response.json();
        
        // Muestra mensaje de éxito
        showMessage(
            `✓ ¡Pregunta creada exitosamente! ID: ${createdQuestion.id}`,
            'success'
        );

        // Limpia el formulario
        document.getElementById('create-question-form').reset();

        // Recarga las preguntas después de 2 segundos
        setTimeout(() => {
            loadQuestions();
        }, 2000);

    } catch (error) {
        console.error('Error:', error);
        showMessage(`Error: ${error.message}`, 'error');
    }
}

function showMessage(message, type) {
    const messageDiv = document.getElementById('create-question-message');
    messageDiv.className = `message ${type}`;
    messageDiv.innerHTML = message;
    messageDiv.classList.remove('hidden');

    // Auto-ocultar después de 5 segundos
    setTimeout(() => {
        messageDiv.classList.add('hidden');
    }, 5000);
}

// ==================== Edit/Delete Question Functions ====================
async function editQuestion(questionId) {
    try {
        // Obtener los datos de la pregunta
        const response = await fetch(`${API_BASE_URL}/questions/${questionId}`);
        if (!response.ok) throw new Error('Error al cargar la pregunta');
        const question = await response.json();

        // Llenar el formulario con los datos actuales
        document.getElementById('edit-q-id').value = question.id;
        document.getElementById('edit-q-pregunta').value = question.pregunta;
        document.getElementById('edit-q-categoria').value = question.categoria;
        document.getElementById('edit-q-dificultad').value = question.dificultad;
        document.getElementById('edit-q-opcion-1').value = question.opciones[0] || '';
        document.getElementById('edit-q-opcion-2').value = question.opciones[1] || '';
        document.getElementById('edit-q-opcion-3').value = question.opciones[2] || '';
        document.getElementById('edit-q-opcion-4').value = question.opciones[3] || '';
        document.getElementById('edit-q-respuesta-correcta').value = question.respuesta_correcta;
        document.getElementById('edit-q-explicacion').value = question.explicacion || '';

        // Mostrar el modal de edición
        document.getElementById('edit-question-modal').classList.remove('hidden');
        document.body.style.overflow = 'hidden';

    } catch (error) {
        alert('Error: ' + error.message);
    }
}

function closeEditModal() {
    document.getElementById('edit-question-modal').classList.add('hidden');
    document.body.style.overflow = 'auto';
}

async function handleEditQuestion(event) {
    event.preventDefault();

    const questionId = parseInt(document.getElementById('edit-q-id').value);
    const pregunta = document.getElementById('edit-q-pregunta').value.trim();
    const categoria = document.getElementById('edit-q-categoria').value;
    const dificultad = document.getElementById('edit-q-dificultad').value;
    const opcion1 = document.getElementById('edit-q-opcion-1').value.trim();
    const opcion2 = document.getElementById('edit-q-opcion-2').value.trim();
    const opcion3 = document.getElementById('edit-q-opcion-3').value.trim();
    const opcion4 = document.getElementById('edit-q-opcion-4').value.trim();
    const respuestaCorrecta = parseInt(document.getElementById('edit-q-respuesta-correcta').value);
    const explicacion = document.getElementById('edit-q-explicacion').value.trim();

    // Validaciones
    if (!pregunta || !categoria || !dificultad) {
        alert('Error: Completa todos los campos requeridos');
        return;
    }

    if (!opcion1 || !opcion2 || !opcion3 || !opcion4) {
        alert('Error: Todas las 4 opciones son requeridas');
        return;
    }

    if (isNaN(respuestaCorrecta) || respuestaCorrecta < 0 || respuestaCorrecta > 3) {
        alert('Error: Selecciona una respuesta correcta válida');
        return;
    }

    const updateData = {
        pregunta: pregunta,
        opciones: [opcion1, opcion2, opcion3, opcion4],
        respuesta_correcta: respuestaCorrecta,
        explicacion: explicacion || null,
        categoria: categoria,
        dificultad: dificultad
    };

    try {
        const response = await fetch(`${API_BASE_URL}/questions/${questionId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(updateData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Error al actualizar la pregunta');
        }

        alert('✓ Pregunta actualizada exitosamente');
        closeEditModal();
        loadQuestions();

    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function deleteQuestion(questionId, questionText) {
    const confirmDelete = confirm(
        `¿Estás seguro de que deseas eliminar esta pregunta?\n\n"${questionText}"`
    );

    if (!confirmDelete) return;

    try {
        const response = await fetch(`${API_BASE_URL}/questions/${questionId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Error al eliminar la pregunta');
        }

        alert('✓ Pregunta eliminada correctamente');
        loadQuestions();

    } catch (error) {
        alert('Error: ' + error.message);
    }
}
