// API Configuration
const API_BASE = '/api';

// DOM Elements
const sections = document.querySelectorAll('.section');
const menuItems = document.querySelectorAll('.menu-item');
const modal = document.getElementById('modal');
const closeBtn = document.querySelector('.close');
const cancelBtn = document.getElementById('cancel-btn');
const modalForm = document.getElementById('modal-form');
const toast = document.getElementById('toast');
const addBtn = document.getElementById('add-btn');
const pageTitle = document.getElementById('page-title');

let currentSection = 'dashboard';
let currentData = null;
let editingId = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    loadDashboard();
    populateCarreraFilter();
});

// Event Listeners
function initializeEventListeners() {
    menuItems.forEach(item => {
        item.addEventListener('click', () => {
            const section = item.dataset.section;
            switchSection(section);
        });
    });

    closeBtn.addEventListener('click', closeModal);
    cancelBtn.addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });

    addBtn.addEventListener('click', openAddModal);

    // Search and filter listeners
    document.getElementById('search-estudiantes')?.addEventListener('input', debounce(filterEstudiantes, 300));
    document.getElementById('search-carreras')?.addEventListener('input', debounce(filterCarreras, 300));
    document.getElementById('search-facultades')?.addEventListener('input', debounce(filterFacultades, 300));
    document.getElementById('filter-estado')?.addEventListener('change', filterEstudiantes);
    document.getElementById('filter-carrera')?.addEventListener('change', filterEstudiantes);
}

// Section Management
function switchSection(section) {
    currentSection = section;
    
    // Update menu
    menuItems.forEach(item => item.classList.remove('active'));
    document.querySelector(`[data-section="${section}"]`).classList.add('active');
    
    // Update content
    sections.forEach(s => s.classList.remove('active'));
    document.getElementById(section).classList.add('active');
    
    // Update header
    const titles = {
        'dashboard': 'Dashboard',
        'estudiantes': 'Gestión de Estudiantes',
        'carreras': 'Gestión de Carreras',
        'facultades': 'Gestión de Facultades'
    };
    
    pageTitle.textContent = titles[section];
    addBtn.style.display = section === 'dashboard' ? 'none' : 'inline-flex';
    
    // Load section data
    if (section === 'estudiantes') {
        loadEstudiantes();
    } else if (section === 'carreras') {
        loadCarreras();
    } else if (section === 'facultades') {
        loadFacultades();
    }
}

// Dashboard
async function loadDashboard() {
    try {
        // Load estudiantes
        const estudiantesRes = await fetch(`${API_BASE}/estudiantes/`);
        const estudiantesData = await estudiantesRes.json();
        const estudiantes = estudiantesData.datos || [];
        
        // Load carreras
        const carrerasRes = await fetch(`${API_BASE}/carreras/`);
        const carrerasData = await carrerasRes.json();
        const carreras = carrerasData.datos || [];
        
        // Load facultades
        const facultadesRes = await fetch(`${API_BASE}/facultades/`);
        const facultadesData = await facultadesRes.json();
        const facultades = facultadesData.datos || [];
        
        // Calculate stats
        const totalEstudiantes = estudiantes.length;
        const disponibles = estudiantes.filter(e => e.estado_practica === 'Disponible').length;
        const contratados = estudiantes.filter(e => e.estado_practica === 'Contratado').length;
        const finalizados = estudiantes.filter(e => e.estado_practica === 'Finalizó').length;
        
        // Update stats
        document.getElementById('total-estudiantes').textContent = totalEstudiantes;
        document.getElementById('disponibles').textContent = disponibles;
        document.getElementById('contratados').textContent = contratados;
        document.getElementById('finalizados').textContent = finalizados;
        document.getElementById('total-carreras').textContent = carreras.length;
        document.getElementById('total-facultades').textContent = facultades.length;
        
        // Load recent estudiantes
        const recentList = document.getElementById('recent-list');
        const recent = estudiantes.slice(0, 5);
        
        if (recent.length === 0) {
            recentList.innerHTML = '<div class="empty-state"><p>No hay estudiantes registrados</p></div>';
        } else {
            recentList.innerHTML = recent.map(est => `
                <div class="list-item">
                    <div class="item-info">
                        <div class="item-title">${est.nombre} ${est.apellido}</div>
                        <div class="item-detail">Documento: ${est.numero_documento}</div>
                        <div class="item-detail">Email: ${est.email}</div>
                        <span class="item-badge badge-${est.estado_practica.toLowerCase().replace(' ', '-')}">${est.estado_practica}</span>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showToast('Error al cargar el dashboard', true);
    }
}

// Estudiantes Management
async function loadEstudiantes() {
    try {
        const res = await fetch(`${API_BASE}/estudiantes/`);
        const data = await res.json();
        currentData = data.datos || [];
        renderEstudiantes(currentData);
    } catch (error) {
        console.error('Error loading estudiantes:', error);
        showToast('Error al cargar estudiantes', true);
    }
}

function renderEstudiantes(estudiantes) {
    const listContainer = document.getElementById('estudiantes-list');
    
    if (estudiantes.length === 0) {
        listContainer.innerHTML = '<div class="empty-state"><p>No hay estudiantes registrados</p></div>';
        return;
    }
    
    listContainer.innerHTML = estudiantes.map(est => `
        <div class="list-item">
            <div class="item-info">
                <div class="item-title">${est.nombre} ${est.apellido}</div>
                <div class="item-detail">Documento: ${est.numero_documento}</div>
                <div class="item-detail">Email: ${est.email}</div>
                <div class="item-detail">Teléfono: ${est.telefono}</div>
                <div>
                    <span class="item-badge badge-${est.estado_practica.toLowerCase().replace(' ', '-')}">${est.estado_practica}</span>
                </div>
            </div>
            <div class="item-actions">
                <button class="btn btn-edit" onclick="editEstudiante(${est.id})">Editar</button>
                <button class="btn btn-danger" onclick="deleteEstudiante(${est.id})">Eliminar</button>
                ${est.estado_practica === 'Disponible' ? `
                    <button class="btn btn-primary" onclick="changeEstudianteStatus(${est.id}, 'Contratado')">Contratar</button>
                ` : ''}
            </div>
        </div>
    `).join('');
}

function filterEstudiantes() {
    const search = (document.getElementById('search-estudiantes')?.value || '').toLowerCase();
    const estado = document.getElementById('filter-estado')?.value || '';
    const carrera = document.getElementById('filter-carrera')?.value || '';
    
    const filtered = currentData.filter(est => {
        const matchSearch = !search || 
            est.nombre.toLowerCase().includes(search) ||
            est.apellido.toLowerCase().includes(search) ||
            est.numero_documento.includes(search) ||
            est.email.toLowerCase().includes(search);
        
        const matchEstado = !estado || est.estado_practica === estado;
        const matchCarrera = !carrera || est.carrera_id == carrera;
        
        return matchSearch && matchEstado && matchCarrera;
    });
    
    renderEstudiantes(filtered);
}

async function populateCarreraFilter() {
    try {
        const res = await fetch(`${API_BASE}/carreras/`);
        const data = await res.json();
        const carreras = data.datos || [];
        
        const select = document.getElementById('filter-carrera');
        if (select) {
            select.innerHTML = '<option value="">Todas las carreras</option>' + 
                carreras.map(c => `<option value="${c.id}">${c.nombre}</option>`).join('');
        }
    } catch (error) {
        console.error('Error loading carreras for filter:', error);
    }
}

async function changeEstudianteStatus(id, newStatus) {
    try {
        const res = await fetch(`${API_BASE}/estudiantes/${id}/estado`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ estado: newStatus })
        });
        
        if (res.ok) {
            showToast(`Estado actualizado a ${newStatus}`);
            loadEstudiantes();
            loadDashboard();
        } else {
            showToast('Error al actualizar estado', true);
        }
    } catch (error) {
        console.error('Error changing status:', error);
        showToast('Error al actualizar estado', true);
    }
}

async function editEstudiante(id) {
    const estudiante = currentData.find(e => e.id === id);
    if (!estudiante) return;
    
    try {
        const facultadesRes = await fetch(`${API_BASE}/facultades/`);
        const facultadesData = await facultadesRes.json();
        const facultades = facultadesData.datos || [];
        
        const carrerasRes = await fetch(`${API_BASE}/carreras/`);
        const carrerasData = await carrerasRes.json();
        const carreras = carrerasData.datos || [];
        
        editingId = id;
        document.getElementById('modal-title').textContent = 'Editar Estudiante';
        
        const fieldsContainer = document.getElementById('form-fields');
        fieldsContainer.innerHTML = `
            <div class="form-group">
                <label for="numero_documento">Documento de Identidad *</label>
                <input type="text" id="numero_documento" name="numero_documento" value="${estudiante.numero_documento}" required>
            </div>
            <div class="form-group">
                <label for="nombre">Nombre *</label>
                <input type="text" id="nombre" name="nombre" value="${estudiante.nombre}" required>
            </div>
            <div class="form-group">
                <label for="apellido">Apellido *</label>
                <input type="text" id="apellido" name="apellido" value="${estudiante.apellido}" required>
            </div>
            <div class="form-group">
                <label for="email">Correo Electrónico *</label>
                <input type="email" id="email" name="email" value="${estudiante.email}" required>
            </div>
            <div class="form-group">
                <label for="telefono">Teléfono *</label>
                <input type="text" id="telefono" name="telefono" value="${estudiante.telefono}" required>
            </div>
            <div class="form-group">
                <label for="genero">Género *</label>
                <select id="genero" name="genero" required>
                    <option value="">Seleccionar Género...</option>
                    <option value="Masculino" ${estudiante.genero === 'Masculino' ? 'selected' : ''}>Masculino</option>
                    <option value="Femenino" ${estudiante.genero === 'Femenino' ? 'selected' : ''}>Femenino</option>
                    <option value="No Binario" ${estudiante.genero === 'No Binario' ? 'selected' : ''}>No Binario</option>
                    <option value="Hombre Transgénero" ${estudiante.genero === 'Hombre Transgénero' ? 'selected' : ''}>Hombre Transgénero</option>
                    <option value="Mujer Transgénero" ${estudiante.genero === 'Mujer Transgénero' ? 'selected' : ''}>Mujer Transgénero</option>
                    <option value="Genderqueer" ${estudiante.genero === 'Genderqueer' ? 'selected' : ''}>Genderqueer</option>
                    <option value="Asexual" ${estudiante.genero === 'Asexual' ? 'selected' : ''}>Asexual</option>
                    <option value="Otro" ${estudiante.genero === 'Otro' ? 'selected' : ''}>Otro</option>
                    <option value="Prefiero no decir" ${estudiante.genero === 'Prefiero no decir' ? 'selected' : ''}>Prefiero no decir</option>
                </select>
            </div>
            <div class="form-group">
                <label for="facultad_id">Facultad *</label>
                <select id="facultad_id" name="facultad_id" required onchange="updateCarrerasFilter()">
                    <option value="">Seleccionar Facultad...</option>
                    ${facultades.map(f => `<option value="${f.id}" ${f.id === estudiante.facultad_id ? 'selected' : ''}>${f.nombre}</option>`).join('')}
                </select>
            </div>
            <div class="form-group">
                <label for="carrera_id">Programa o Carrera *</label>
                <select id="carrera_id" name="carrera_id" required>
                    ${carreras.map(c => `<option value="${c.id}" data-facultad="${c.facultad_id}" ${c.id === estudiante.carrera_id ? 'selected' : ''}>${c.nombre}</option>`).join('')}
                </select>
            </div>
            <div class="form-group">
                <label for="tiene_discapacidad">¿Presenta alguna discapacidad?</label>
                <select id="tiene_discapacidad" name="tiene_discapacidad" onchange="toggleDiscapacidadPersonalizada()">
                    <option value="" ${!estudiante.tiene_discapacidad ? 'selected' : ''}>No</option>
                    <option value="Discapacidad Auditiva" ${estudiante.tiene_discapacidad === 'Discapacidad Auditiva' ? 'selected' : ''}>Discapacidad Auditiva</option>
                    <option value="Discapacidad Visual" ${estudiante.tiene_discapacidad === 'Discapacidad Visual' ? 'selected' : ''}>Discapacidad Visual</option>
                    <option value="Discapacidad Motriz" ${estudiante.tiene_discapacidad === 'Discapacidad Motriz' ? 'selected' : ''}>Discapacidad Motriz</option>
                    <option value="Discapacidad Cognitiva" ${estudiante.tiene_discapacidad === 'Discapacidad Cognitiva' ? 'selected' : ''}>Discapacidad Cognitiva</option>
                    <option value="Discapacidad del Habla" ${estudiante.tiene_discapacidad === 'Discapacidad del Habla' ? 'selected' : ''}>Discapacidad del Habla</option>
                    <option value="Otra" ${estudiante.tiene_discapacidad === 'Otra' ? 'selected' : ''}>Otra (especificar)</option>
                </select>
            </div>
            <div class="form-group" id="discapacidad-personalizada-group" style="display: ${estudiante.tiene_discapacidad === 'Otra' ? 'block' : 'none'};">
                <label for="discapacidad_personalizada">Especificar discapacidad</label>
                <input type="text" id="discapacidad_personalizada" name="discapacidad_personalizada" value="${estudiante.discapacidad_personalizada || ''}" placeholder="Ej: Discapacidad específica...">
            </div>
            <div class="form-group">
                <label for="estado_practica">Estado de Práctica *</label>
                <select id="estado_practica" name="estado_practica" required>
                    <option value="Disponible" ${estudiante.estado_practica === 'Disponible' ? 'selected' : ''}>Disponible</option>
                    <option value="Contratado" ${estudiante.estado_practica === 'Contratado' ? 'selected' : ''}>Contratado</option>
                    <option value="Por Finalizar" ${estudiante.estado_practica === 'Por Finalizar' ? 'selected' : ''}>Por Finalizar</option>
                    <option value="Finalizó" ${estudiante.estado_practica === 'Finalizó' ? 'selected' : ''}>Finalizó</option>
                </select>
            </div>
        `;
        
        // Filtrar carreras por facultad seleccionada
        setTimeout(() => {
            updateCarrerasFilter();
        }, 100);
        
        modalForm.onsubmit = (e) => {
            e.preventDefault();
            submitForm('estudiantes', editingId);
        };
        
        modal.classList.add('active');
    } catch (error) {
        console.error('Error editing estudiante:', error);
        showToast('Error al cargar el formulario', true);
    }
}

async function deleteEstudiante(id) {
    if (!confirm('¿Estás seguro de que deseas eliminar este estudiante?')) return;
    
    try {
        const res = await fetch(`${API_BASE}/estudiantes/${id}`, { method: 'DELETE' });
        
        if (res.ok) {
            showToast('Estudiante eliminado exitosamente');
            loadEstudiantes();
            loadDashboard();
        } else {
            showToast('Error al eliminar estudiante', true);
        }
    } catch (error) {
        console.error('Error deleting estudiante:', error);
        showToast('Error al eliminar estudiante', true);
    }
}

// Carreras Management
async function loadCarreras() {
    try {
        const res = await fetch(`${API_BASE}/carreras/`);
        const data = await res.json();
        currentData = data.datos || [];
        renderCarreras(currentData);
    } catch (error) {
        console.error('Error loading carreras:', error);
        showToast('Error al cargar carreras', true);
    }
}

function renderCarreras(carreras) {
    const listContainer = document.getElementById('carreras-list');
    
    if (carreras.length === 0) {
        listContainer.innerHTML = '<div class="empty-state"><p>No hay carreras registradas</p></div>';
        return;
    }
    
    listContainer.innerHTML = carreras.map(carrera => `
        <div class="list-item">
            <div class="item-info">
                <div class="item-title">${carrera.nombre}</div>
                <div class="item-detail">Descripción: ${carrera.descripcion}</div>
                <div class="item-detail">Facultad ID: ${carrera.facultad_id}</div>
            </div>
            <div class="item-actions">
                <button class="btn btn-edit" onclick="editCarrera(${carrera.id})">Editar</button>
                <button class="btn btn-danger" onclick="deleteCarrera(${carrera.id})">Eliminar</button>
            </div>
        </div>
    `).join('');
}

function filterCarreras() {
    const search = (document.getElementById('search-carreras')?.value || '').toLowerCase();
    
    const filtered = currentData.filter(carrera => 
        carrera.nombre.toLowerCase().includes(search) ||
        carrera.descripcion.toLowerCase().includes(search)
    );
    
    renderCarreras(filtered);
}

async function editCarrera(id) {
    const carrera = currentData.find(c => c.id === id);
    if (!carrera) return;
    
    try {
        const facultadesRes = await fetch(`${API_BASE}/facultades/`);
        const facultadesData = await facultadesRes.json();
        const facultades = facultadesData.datos || [];
        
        editingId = id;
        document.getElementById('modal-title').textContent = 'Editar Carrera';
        
        const fieldsContainer = document.getElementById('form-fields');
        fieldsContainer.innerHTML = `
            <div class="form-group">
                <label for="nombre">Nombre de la Carrera *</label>
                <input type="text" id="nombre" name="nombre" value="${carrera.nombre}" required>
            </div>
            <div class="form-group">
                <label for="descripcion">Descripción</label>
                <textarea id="descripcion" name="descripcion">${carrera.descripcion}</textarea>
            </div>
            <div class="form-group">
                <label for="facultad_id">Facultad *</label>
                <select id="facultad_id" name="facultad_id" required>
                    <option value="">Seleccionar Facultad...</option>
                    ${facultades.map(f => `<option value="${f.id}" ${f.id === carrera.facultad_id ? 'selected' : ''}>${f.nombre}</option>`).join('')}
                </select>
            </div>
        `;
        
        modalForm.onsubmit = (e) => {
            e.preventDefault();
            submitForm('carreras', editingId);
        };
        
        modal.classList.add('active');
    } catch (error) {
        console.error('Error editing carrera:', error);
        showToast('Error al cargar el formulario', true);
    }
}

async function deleteCarrera(id) {
    if (!confirm('¿Estás seguro de que deseas eliminar esta carrera?')) return;
    
    try {
        const res = await fetch(`${API_BASE}/carreras/${id}`, { method: 'DELETE' });
        
        if (res.ok) {
            showToast('Carrera eliminada exitosamente');
            loadCarreras();
            loadDashboard();
        } else {
            showToast('Error al eliminar carrera', true);
        }
    } catch (error) {
        console.error('Error deleting carrera:', error);
        showToast('Error al eliminar carrera', true);
    }
}

// Facultades Management
async function loadFacultades() {
    try {
        const res = await fetch(`${API_BASE}/facultades/`);
        const data = await res.json();
        currentData = data.datos || [];
        renderFacultades(currentData);
    } catch (error) {
        console.error('Error loading facultades:', error);
        showToast('Error al cargar facultades', true);
    }
}

function renderFacultades(facultades) {
    const listContainer = document.getElementById('facultades-list');
    
    if (facultades.length === 0) {
        listContainer.innerHTML = '<div class="empty-state"><p>No hay facultades registradas</p></div>';
        return;
    }
    
    listContainer.innerHTML = facultades.map(facultad => `
        <div class="list-item">
            <div class="item-info">
                <div class="item-title">${facultad.nombre}</div>
                <div class="item-detail">Descripción: ${facultad.descripcion}</div>
                <div class="item-detail">Creada: ${new Date(facultad.fecha_creacion).toLocaleDateString()}</div>
            </div>
            <div class="item-actions">
                <button class="btn btn-edit" onclick="editFacultad(${facultad.id})">Editar</button>
                <button class="btn btn-danger" onclick="deleteFacultad(${facultad.id})">Eliminar</button>
            </div>
        </div>
    `).join('');
}

function filterFacultades() {
    const search = (document.getElementById('search-facultades')?.value || '').toLowerCase();
    
    const filtered = currentData.filter(facultad => 
        facultad.nombre.toLowerCase().includes(search) ||
        facultad.descripcion.toLowerCase().includes(search)
    );
    
    renderFacultades(filtered);
}

async function editFacultad(id) {
    const facultad = currentData.find(f => f.id === id);
    if (!facultad) return;
    
    editingId = id;
    document.getElementById('modal-title').textContent = 'Editar Facultad';
    
    const fieldsContainer = document.getElementById('form-fields');
    fieldsContainer.innerHTML = `
        <div class="form-group">
            <label for="nombre">Nombre de la Facultad *</label>
            <input type="text" id="nombre" name="nombre" value="${facultad.nombre}" required>
        </div>
        <div class="form-group">
            <label for="descripcion">Descripción</label>
            <textarea id="descripcion" name="descripcion">${facultad.descripcion}</textarea>
        </div>
    `;
    
    modalForm.onsubmit = (e) => {
        e.preventDefault();
        submitForm('facultades', editingId);
    };
    
    modal.classList.add('active');
}

async function deleteFacultad(id) {
    if (!confirm('¿Estás seguro de que deseas eliminar esta facultad?')) return;
    
    try {
        const res = await fetch(`${API_BASE}/facultades/${id}`, { method: 'DELETE' });
        
        if (res.ok) {
            showToast('Facultad eliminada exitosamente');
            loadFacultades();
            loadDashboard();
        } else {
            showToast('Error al eliminar facultad', true);
        }
    } catch (error) {
        console.error('Error deleting facultad:', error);
        showToast('Error al eliminar facultad', true);
    }
}

// Modal Functions
function openAddModal() {
    editingId = null;
    
    if (currentSection === 'estudiantes') {
        openAddEstudianteModal();
    } else if (currentSection === 'carreras') {
        openAddCarreraModal();
    } else if (currentSection === 'facultades') {
        openAddFacultadModal();
    }
}

async function openAddEstudianteModal() {
    try {
        const facultadesRes = await fetch(`${API_BASE}/facultades/`);
        const facultadesData = await facultadesRes.json();
        const facultades = facultadesData.datos || [];
        
        const carrerasRes = await fetch(`${API_BASE}/carreras/`);
        const carrerasData = await carrerasRes.json();
        const carreras = carrerasData.datos || [];
        
        editingId = null;
        document.getElementById('modal-title').textContent = 'Agregar Nuevo Estudiante';
        
        const fieldsContainer = document.getElementById('form-fields');
        fieldsContainer.innerHTML = `
            <div class="form-group">
                <label for="numero_documento">Documento de Identidad *</label>
                <input type="text" id="numero_documento" name="numero_documento" required placeholder="Ej: 12345678">
            </div>
            <div class="form-group">
                <label for="nombre">Nombre *</label>
                <input type="text" id="nombre" name="nombre" required placeholder="Ej: Juan">
            </div>
            <div class="form-group">
                <label for="apellido">Apellido *</label>
                <input type="text" id="apellido" name="apellido" required placeholder="Ej: Pérez">
            </div>
            <div class="form-group">
                <label for="email">Correo Electrónico *</label>
                <input type="email" id="email" name="email" required placeholder="Ej: juan@example.com">
            </div>
            <div class="form-group">
                <label for="telefono">Teléfono *</label>
                <input type="text" id="telefono" name="telefono" required placeholder="Ej: 3001234567">
            </div>
            <div class="form-group">
                <label for="genero">Género *</label>
                <select id="genero" name="genero" required>
                    <option value="">Seleccionar Género...</option>
                    <option value="Masculino">Masculino</option>
                    <option value="Femenino">Femenino</option>
                    <option value="No Binario">No Binario</option>
                    <option value="Hombre Transgénero">Hombre Transgénero</option>
                    <option value="Mujer Transgénero">Mujer Transgénero</option>
                    <option value="Genderqueer">Genderqueer</option>
                    <option value="Asexual">Asexual</option>
                    <option value="Otro">Otro</option>
                    <option value="Prefiero no decir">Prefiero no decir</option>
                </select>
            </div>
            <div class="form-group">
                <label for="facultad_id">Facultad *</label>
                <select id="facultad_id" name="facultad_id" required onchange="updateCarrerasFilter()">
                    <option value="">Seleccionar Facultad...</option>
                    ${facultades.map(f => `<option value="${f.id}">${f.nombre}</option>`).join('')}
                </select>
            </div>
            <div class="form-group">
                <label for="carrera_id">Programa o Carrera *</label>
                <select id="carrera_id" name="carrera_id" required>
                    <option value="">Seleccionar Carrera (primero selecciona facultad)...</option>
                    ${carreras.map(c => `<option value="${c.id}" data-facultad="${c.facultad_id}">${c.nombre}</option>`).join('')}
                </select>
            </div>
            <div class="form-group">
                <label for="tiene_discapacidad">¿Presenta alguna discapacidad?</label>
                <select id="tiene_discapacidad" name="tiene_discapacidad" onchange="toggleDiscapacidadPersonalizada()">
                    <option value="">No</option>
                    <option value="Discapacidad Auditiva">Discapacidad Auditiva</option>
                    <option value="Discapacidad Visual">Discapacidad Visual</option>
                    <option value="Discapacidad Motriz">Discapacidad Motriz</option>
                    <option value="Discapacidad Cognitiva">Discapacidad Cognitiva</option>
                    <option value="Discapacidad del Habla">Discapacidad del Habla</option>
                    <option value="Otra">Otra (especificar)</option>
                </select>
            </div>
            <div class="form-group" id="discapacidad-personalizada-group" style="display: none;">
                <label for="discapacidad_personalizada">Especificar discapacidad</label>
                <input type="text" id="discapacidad_personalizada" name="discapacidad_personalizada" placeholder="Ej: Discapacidad específica...">
            </div>
        `;
        
        modalForm.onsubmit = (e) => {
            e.preventDefault();
            submitForm('estudiantes', null);
        };
        
        modal.classList.add('active');
    } catch (error) {
        console.error('Error opening add estudiante modal:', error);
        showToast('Error al cargar el formulario', true);
    }
}

function updateCarrerasFilter() {
    const facultadId = document.getElementById('facultad_id').value;
    const carreraSelect = document.getElementById('carrera_id');
    const options = carreraSelect.querySelectorAll('option');
    
    options.forEach(option => {
        if (option.value === '') {
            option.style.display = 'block';
        } else {
            const optionFacultadId = option.dataset.facultad;
            option.style.display = optionFacultadId === facultadId ? 'block' : 'none';
        }
    });
    
    carreraSelect.value = '';
}

async function openAddCarreraModal() {
    try {
        const facultadesRes = await fetch(`${API_BASE}/facultades/`);
        const facultadesData = await facultadesRes.json();
        const facultades = facultadesData.datos || [];
        
        editingId = null;
        document.getElementById('modal-title').textContent = 'Agregar Nueva Carrera';
        
        const fieldsContainer = document.getElementById('form-fields');
        fieldsContainer.innerHTML = `
            <div class="form-group">
                <label for="nombre">Nombre de la Carrera *</label>
                <input type="text" id="nombre" name="nombre" required placeholder="Ej: Ingeniería de Sistemas">
            </div>
            <div class="form-group">
                <label for="descripcion">Descripción</label>
                <textarea id="descripcion" name="descripcion" placeholder="Descripción de la carrera..."></textarea>
            </div>
            <div class="form-group">
                <label for="facultad_id">Facultad *</label>
                <select id="facultad_id" name="facultad_id" required>
                    <option value="">Seleccionar Facultad...</option>
                    ${facultades.map(f => `<option value="${f.id}">${f.nombre}</option>`).join('')}
                </select>
            </div>
        `;
        
        modalForm.onsubmit = (e) => {
            e.preventDefault();
            submitForm('carreras', null);
        };
        
        modal.classList.add('active');
    } catch (error) {
        console.error('Error opening add carrera modal:', error);
        showToast('Error al cargar el formulario', true);
    }
}

async function openAddFacultadModal() {
    editingId = null;
    document.getElementById('modal-title').textContent = 'Agregar Nueva Facultad';
    
    const fieldsContainer = document.getElementById('form-fields');
    fieldsContainer.innerHTML = `
        <div class="form-group">
            <label for="nombre">Nombre de la Facultad *</label>
            <input type="text" id="nombre" name="nombre" required placeholder="Ej: Facultad de Ingeniería">
        </div>
        <div class="form-group">
            <label for="descripcion">Descripción</label>
            <textarea id="descripcion" name="descripcion" placeholder="Descripción de la facultad..."></textarea>
        </div>
    `;
    
    modalForm.onsubmit = (e) => {
        e.preventDefault();
        submitForm('facultades', null);
    };
    
    modal.classList.add('active');
}

async function submitForm(type, id = null) {
    const formData = new FormData(modalForm);
    const data = Object.fromEntries(formData);
    
    // Convert numeric fields
    if (data.facultad_id) data.facultad_id = parseInt(data.facultad_id);
    if (data.carrera_id) data.carrera_id = parseInt(data.carrera_id);
    
    // Validar que la carrera pertenece a la facultad seleccionada
    if (data.facultad_id && data.carrera_id) {
        const carreraSelect = document.getElementById('carrera_id');
        const selectedOption = carreraSelect.querySelector(`option[value="${data.carrera_id}"]`);
        if (selectedOption && parseInt(selectedOption.dataset.facultad) !== data.facultad_id) {
            showToast('La carrera seleccionada no pertenece a la facultad elegida', true);
            return;
        }
    }
    
    try {
        const url = id ? `${API_BASE}/${type}/${id}` : `${API_BASE}/${type}/`;
        const method = id ? 'PUT' : 'POST';
        
        const res = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (res.ok) {
            showToast(id ? 'Actualizado exitosamente' : 'Creado exitosamente');
            closeModal();
            
            if (type === 'estudiantes') {
                loadEstudiantes();
                loadDashboard();
            }
            else if (type === 'carreras') {
                loadCarreras();
                loadDashboard();
            }
            else if (type === 'facultades') {
                loadFacultades();
                loadDashboard();
            }
        } else {
            const errorData = await res.json();
            showToast(errorData.error || errorData.mensaje || 'Error al guardar', true);
        }
    } catch (error) {
        console.error('Error submitting form:', error);
        showToast('Error al guardar: ' + error.message, true);
    }
}

function closeModal() {
    modal.classList.remove('active');
    modalForm.reset();
    editingId = null;
}

// Utility Functions
function toggleDiscapacidadPersonalizada() {
    const tieneDiscapacidad = document.getElementById('tiene_discapacidad').value;
    const discapacidadGroup = document.getElementById('discapacidad-personalizada-group');
    
    if (tieneDiscapacidad === 'Otra') {
        discapacidadGroup.style.display = 'block';
        document.getElementById('discapacidad_personalizada').focus();
    } else {
        discapacidadGroup.style.display = 'none';
        document.getElementById('discapacidad_personalizada').value = '';
    }
}

function showToast(message, isError = false) {
    toast.textContent = message;
    toast.classList.add('show');
    if (isError) toast.classList.add('error');
    else toast.classList.remove('error');
    
    setTimeout(() => toast.classList.remove('show'), 3000);
}

function debounce(func, delay) {
    let timeoutId;
    return (...args) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func(...args), delay);
    };
}
