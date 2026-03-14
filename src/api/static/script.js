// API Configuration
const API_BASE = '/api';

// Interceptor global: si cualquier respuesta es 401, redirigir al login
const _origFetch = window.fetch;
window.fetch = async function(...args) {
    const res = await _origFetch(...args);
    if (res.status === 401) {
        window.location.href = '/auth/login';
    }
    return res;
};

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
let currentUser = { role: 'anonymous' };

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const res = await _origFetch('/auth/me');
        const data = await res.json();
        currentUser = data;
    } catch (e) {
        console.error('Error loading user info:', e);
    }
    initializeEventListeners();
    loadDashboard();
    populateCarreraFilter();
    populateFacultadFilter();
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
    document.getElementById('search-programas')?.addEventListener('input', debounce(filterProgramas, 300));
    document.getElementById('search-facultades')?.addEventListener('input', debounce(filterFacultades, 300));
    document.getElementById('filter-estado')?.addEventListener('change', filterEstudiantes);
    document.getElementById('filter-carrera')?.addEventListener('change', filterEstudiantes);
    document.getElementById('filter-nivel')?.addEventListener('change', filterProgramas);
    document.getElementById('filter-facultad')?.addEventListener('change', filterProgramas);
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
        'programas': 'Gestión de Programas Académicos',
        'facultades': 'Gestión de Facultades',
        'asesores': 'Asesores de Prácticas'
    };

    pageTitle.textContent = titles[section] || section;
    addBtn.style.display = section === 'dashboard' ? 'none' : 'inline-flex';
    const importBtn = document.getElementById('import-btn');
    if (importBtn) importBtn.style.display = section === 'estudiantes' ? 'inline-flex' : 'none';

    // Load section data
    if (section === 'estudiantes') {
        loadEstudiantes();
    } else if (section === 'programas') {
        loadProgramas();
    } else if (section === 'facultades') {
        loadFacultades();
    } else if (section === 'asesores') {
        loadAsesores();
    }
}

// Dashboard
let _chartAsesorEst = null;
let _chartAsesorEstados = null;

async function _safeFetch(url, key) {
    try {
        const res = await fetch(url);
        const json = await res.json();
        return json[key] || [];
    } catch (e) {
        console.error(`Error fetching ${url}:`, e);
        return [];
    }
}

async function loadDashboard() {
    const [estudiantes, programas, facultades, asesores] = await Promise.all([
        _safeFetch(`${API_BASE}/estudiantes/`, 'datos'),
        _safeFetch(`${API_BASE}/programas/`, 'data'),
        _safeFetch(`${API_BASE}/facultades/`, 'datos'),
        _safeFetch(`${API_BASE}/asesores/`, 'datos'),
    ]);

    // ── Contadores ────────────────────────────────────────────────────────
    document.getElementById('total-estudiantes').textContent = estudiantes.length;
    document.getElementById('disponibles').textContent  = estudiantes.filter(e => e.estado_practica === 'Disponible').length;
    document.getElementById('contratados').textContent  = estudiantes.filter(e => e.estado_practica === 'Contratado').length;
    document.getElementById('finalizados').textContent  = estudiantes.filter(e => e.estado_practica === 'Finalizó').length;
    document.getElementById('total-programas').textContent  = programas.length;
    document.getElementById('total-facultades').textContent = facultades.length;

    // ── Estudiantes recientes ─────────────────────────────────────────────
    const recentList = document.getElementById('recent-list');
    const recent = estudiantes.slice(0, 5);
    recentList.innerHTML = recent.length === 0
        ? '<div class="empty-state"><p>No hay estudiantes registrados</p></div>'
        : recent.map(est => {
            const estado = est.estado_practica || 'desconocido';
            return `
                <div class="list-item">
                    <div class="item-info">
                        <div class="item-title">${est.nombre} ${est.apellido}</div>
                        <div class="item-detail">Documento: ${est.numero_documento}</div>
                        <div class="item-detail">Email: ${est.email}</div>
                        <span class="item-badge badge-${estado.toLowerCase().replace(' ', '-')}">${estado}</span>
                    </div>
                </div>`;
        }).join('');

    // ── Tortas de Asesores ────────────────────────────────────────────────
    _renderChartAsesorEstudiantes(asesores);
    _renderChartAsesorEstados(asesores);
}

const _CHART_PALETTE = [
    '#1B1464','#56ACDE','#27AE60','#F39C12','#E74C3C',
    '#8E44AD','#2980B9','#16A085','#D35400','#7F8C8D',
];

function _renderChartAsesorEstudiantes(asesores) {
    const activos = asesores.filter(a => a.activo && (a.estadisticas?.total_activos ?? 0) > 0);
    const canvas  = document.getElementById('chart-asesores-estudiantes');
    const empty   = document.getElementById('chart-asesores-empty');

    if (_chartAsesorEst) { _chartAsesorEst.destroy(); _chartAsesorEst = null; }

    if (!activos.length) {
        canvas.style.display = 'none';
        empty.style.display = 'block';
        return;
    }
    canvas.style.display = 'block';
    empty.style.display = 'none';

    _chartAsesorEst = new Chart(canvas, {
        type: 'doughnut',
        data: {
            labels: activos.map(a => a.nombre_completo),
            datasets: [{
                data: activos.map(a => a.estadisticas.total_activos),
                backgroundColor: activos.map((_, i) => _CHART_PALETTE[i % _CHART_PALETTE.length]),
                borderWidth: 2,
                borderColor: '#fff',
            }],
        },
        options: {
            cutout: '62%',
            plugins: {
                legend: { position: 'bottom', labels: { font: { size: 12 }, padding: 12 } },
                tooltip: {
                    callbacks: {
                        label: ctx => ` ${ctx.label}: ${ctx.parsed} estudiante${ctx.parsed !== 1 ? 's' : ''}`,
                    },
                },
            },
        },
    });
}

function _renderChartAsesorEstados(asesores) {
    const canvas = document.getElementById('chart-asesores-estados');
    const empty  = document.getElementById('chart-estados-empty');

    // Sumar todos los estados de todos los asesores activos
    const totales = {};
    asesores.filter(a => a.activo).forEach(a => {
        const porEstado = a.estadisticas?.por_estado || {};
        Object.entries(porEstado).forEach(([estado, cnt]) => {
            totales[estado] = (totales[estado] || 0) + cnt;
        });
    });

    if (_chartAsesorEstados) { _chartAsesorEstados.destroy(); _chartAsesorEstados = null; }

    const etiquetas = Object.keys(totales);
    if (!etiquetas.length) {
        canvas.style.display = 'none';
        empty.style.display = 'block';
        return;
    }
    canvas.style.display = 'block';
    empty.style.display = 'none';

    const coloresEstado = {
        'Disponible':    '#27AE60',
        'Contratado':    '#8E44AD',
        'Por Finalizar': '#F39C12',
        'Finalizó':      '#95A5A6',
    };

    _chartAsesorEstados = new Chart(canvas, {
        type: 'doughnut',
        data: {
            labels: etiquetas,
            datasets: [{
                data: etiquetas.map(e => totales[e]),
                backgroundColor: etiquetas.map(e => coloresEstado[e] || '#2980B9'),
                borderWidth: 2,
                borderColor: '#fff',
            }],
        },
        options: {
            cutout: '62%',
            plugins: {
                legend: { position: 'bottom', labels: { font: { size: 12 }, padding: 12 } },
                tooltip: {
                    callbacks: {
                        label: ctx => ` ${ctx.label}: ${ctx.parsed} estudiante${ctx.parsed !== 1 ? 's' : ''}`,
                    },
                },
            },
        },
    });
}

// ── Semáforo de contrato ──────────────────────────────────────────────────────
function calcularSemaforo(est) {
    if (!est.fecha_fin_contrato) return '';

    const ahora = new Date();
    const fin = new Date(est.fecha_fin_contrato);
    const inicio = est.fecha_inicio_contrato ? new Date(est.fecha_inicio_contrato) : null;
    const diasRestantes = Math.ceil((fin - ahora) / (1000 * 60 * 60 * 24));

    let color;
    if (diasRestantes > 30) {
        color = '#27AE60';
    } else if (diasRestantes > 0) {
        color = '#F39C12';
    } else {
        color = '#E74C3C';
    }

    let progreso = 100;
    if (inicio) {
        const total = fin - inicio;
        const transcurrido = ahora - inicio;
        progreso = Math.min(100, Math.max(0, Math.round((transcurrido / total) * 100)));
    }

    const finStr = fin.toLocaleDateString('es-CO');
    const inicioStr = inicio ? inicio.toLocaleDateString('es-CO') : '-';
    const diasLabel = diasRestantes > 0
        ? `${diasRestantes} día${diasRestantes !== 1 ? 's' : ''} restante${diasRestantes !== 1 ? 's' : ''}`
        : 'Contrato vencido';

    return `
        <div class="semaforo-contrato">
            <span class="semaforo-dot" style="background:${color};box-shadow:0 0 0 3px ${color}33;"></span>
            <div class="semaforo-info">
                <div class="semaforo-barra-bg">
                    <div class="semaforo-barra-fg" style="width:${progreso}%;background:${color};"></div>
                </div>
                <span class="semaforo-label" style="color:${color};">${diasLabel} &nbsp;·&nbsp; ${inicioStr} → ${finStr}</span>
            </div>
        </div>`;
}

// Estudiantes Management
async function loadEstudiantes() {
    // Actualizar automáticamente estados por vencimiento de contrato
    await fetch(`${API_BASE}/estudiantes/revisar-estados`, { method: 'POST' }).catch(() => {});

    try {
        const res = await fetch(`${API_BASE}/estudiantes/`);
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            console.error('Error API estudiantes:', err);
            showToast(`Error al cargar estudiantes: ${err.error || res.status}`, true);
            currentData = [];
            renderEstudiantes([]);
            return;
        }
        const data = await res.json();
        currentData = data.datos || [];
        renderEstudiantes(currentData);
    } catch (error) {
        console.error('Error loading estudiantes:', error);
        showToast('Error al cargar estudiantes', true);
        currentData = [];
        renderEstudiantes([]);
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
                ${est.asesor_nombre ? `<div class="item-detail">Asesor: ${est.asesor_nombre}</div>` : ''}
                <div>
                    <span class="item-badge badge-${(est.estado_practica||'desconocido').toLowerCase().replace(' ', '-')}">${est.estado_practica||'Desconocido'}</span>
                </div>
                ${calcularSemaforo(est)}
            </div>
            <div class="item-actions">
                <button class="btn btn-edit" onclick="editEstudiante(${est.id})">Editar</button>
                ${!['asesor','asesor_enlace'].includes(currentUser.role) ? `<button class="btn btn-danger" onclick="deleteEstudiante(${est.id})">Eliminar</button>` : ''}
                ${est.estado_practica === 'Disponible' ? `
                    <button class="btn btn-primary" onclick="abrirModalContrato(${est.id}, '${est.nombre} ${est.apellido}')">Contratar</button>
                ` : ''}
                ${est.tiene_cv ? `
                    <button class="btn btn-cv-ver" onclick="verCV(${est.id})" title="Ver CV">📄 CV</button>
                    <button class="btn btn-cv-del" onclick="eliminarCV(${est.id})" title="Eliminar CV">✕ CV</button>
                ` : `
                    <button class="btn btn-cv-up" onclick="abrirUploadCV(${est.id})" title="Subir CV">⬆ CV</button>
                `}
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
        const res = await fetch(`${API_BASE}/facultades/`);
        const data = await res.json();
        const facultades = data.datos || [];
        
        const select = document.getElementById('filter-carrera');
        if (select) {
            select.innerHTML = '<option value="">Todas las facultades</option>' + 
                facultades.map(f => `<option value="${f.id}">${f.nombre}</option>`).join('');
        }
    } catch (error) {
        console.error('Error loading facultades for filter:', error);
    }
}

async function populateFacultadFilter() {
    try {
        const res = await fetch(`${API_BASE}/programas/`);
        const data = await res.json();
        const programas = data.data || [];
        
        // Get unique facultades from programas
        const facultades = [...new Set(programas.map(p => ({
            id: p.facultad_id,
            nombre: p.facultad_nombre
        })).map(f => JSON.stringify(f)))].map(JSON.parse);
        
        const select = document.getElementById('filter-facultad');
        if (select) {
            select.innerHTML = '<option value="">Todas las facultades</option>' + 
                facultades.map(f => `<option value="${f.id}">${f.nombre}</option>`).join('');
        }
    } catch (error) {
        console.error('Error loading facultades for filter:', error);
    }
}

let _contratoEstudianteId = null;

function abrirModalContrato(id, nombre) {
    _contratoEstudianteId = id;
    document.getElementById('contrato-nombre').textContent = nombre;

    const today = new Date().toISOString().substring(0, 10);
    document.getElementById('contrato-fecha').value = today;

    const fin = new Date();
    fin.setMonth(fin.getMonth() + 6);
    document.getElementById('contrato-fecha-fin').value = fin.toISOString().substring(0, 10);

    // Actualizar fecha fin automáticamente al cambiar inicio
    document.getElementById('contrato-fecha').onchange = function () {
        if (this.value) {
            const inicio = new Date(this.value);
            inicio.setMonth(inicio.getMonth() + 6);
            document.getElementById('contrato-fecha-fin').value = inicio.toISOString().substring(0, 10);
        }
    };

    document.getElementById('modal-contrato').classList.add('active');
}

function cerrarModalContrato(event) {
    if (event && event.target !== document.getElementById('modal-contrato')) return;
    document.getElementById('modal-contrato').classList.remove('active');
    _contratoEstudianteId = null;
}

async function confirmarContrato() {
    const fechaInicio = document.getElementById('contrato-fecha').value;
    const fechaFin = document.getElementById('contrato-fecha-fin').value;
    if (!fechaInicio) {
        showToast('Selecciona una fecha de inicio', true);
        return;
    }
    document.getElementById('modal-contrato').classList.remove('active');
    await changeEstudianteStatus(_contratoEstudianteId, 'Contratado', fechaInicio, fechaFin || null);
    _contratoEstudianteId = null;
}

function toggleFechaContrato(estado) {
    const group = document.getElementById('fecha-contrato-group');
    if (group) group.style.display = ['Contratado', 'Por Finalizar'].includes(estado) ? 'block' : 'none';
}

async function changeEstudianteStatus(id, newStatus, fechaInicio = null, fechaFin = null) {
    try {
        const body = { estado: newStatus };
        if (fechaInicio) body.fecha_inicio_contrato = fechaInicio;
        if (fechaFin) body.fecha_fin_contrato = fechaFin;
        const res = await fetch(`${API_BASE}/estudiantes/${id}/estado`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
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
        const [facultadesData, carrerasData, asesoresData] = await Promise.all([
            fetch(`${API_BASE}/facultades/`).then(r => r.json()),
            fetch(`${API_BASE}/carreras/`).then(r => r.json()),
            fetch(`${API_BASE}/asesores/?activos=true`).then(r => r.json()),
        ]);
        const facultades = facultadesData.datos || [];
        const carreras = carrerasData.datos || [];
        const asesores = (asesoresData.datos || []).filter(a => a.activo);
        
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
                <select id="estado_practica" name="estado_practica" required onchange="toggleFechaContrato(this.value)">
                    <option value="Disponible" ${estudiante.estado_practica === 'Disponible' ? 'selected' : ''}>Disponible</option>
                    <option value="Contratado" ${estudiante.estado_practica === 'Contratado' ? 'selected' : ''}>Contratado</option>
                    <option value="Por Finalizar" ${estudiante.estado_practica === 'Por Finalizar' ? 'selected' : ''}>Por Finalizar</option>
                    <option value="Finalizó" ${estudiante.estado_practica === 'Finalizó' ? 'selected' : ''}>Finalizó</option>
                </select>
            </div>
            <div class="form-group" id="fecha-contrato-group" style="display: ${['Contratado', 'Por Finalizar'].includes(estudiante.estado_practica) ? 'block' : 'none'};">
                <label for="fecha_inicio_contrato">Fecha de inicio del contrato</label>
                <input type="date" id="fecha_inicio_contrato" name="fecha_inicio_contrato"
                    value="${estudiante.fecha_inicio_contrato ? estudiante.fecha_inicio_contrato.substring(0, 10) : ''}">
                <label for="fecha_fin_contrato" style="margin-top:8px;display:block;">Fecha de fin del contrato</label>
                <input type="date" id="fecha_fin_contrato" name="fecha_fin_contrato"
                    value="${estudiante.fecha_fin_contrato ? estudiante.fecha_fin_contrato.substring(0, 10) : ''}">
            </div>
            <div class="form-group">
                <label for="asesor_id">Asesor asignado</label>
                <select id="asesor_id" name="asesor_id">
                    <option value="">Sin asesor</option>
                    ${asesores.map(a => `<option value="${a.id}" ${a.id === estudiante.asesor_id ? 'selected' : ''}>${a.nombre_completo}${a.tipo === 'asesor_enlace' ? ' (Enlace)' : ''}</option>`).join('')}
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

// Programas Management
async function loadProgramas() {
    try {
        const res = await fetch(`${API_BASE}/programas/`);
        const data = await res.json();
        currentData = data.data || [];
        renderProgramas(currentData);
        populateFacultadFilter();
    } catch (error) {
        console.error('Error loading programas:', error);
        showToast('Error al cargar programas', true);
    }
}

function renderProgramas(programas) {
    const listContainer = document.getElementById('programas-list');
    
    if (programas.length === 0) {
        listContainer.innerHTML = '<div class="empty-state"><p>No hay programas registrados</p></div>';
        return;
    }
    
    listContainer.innerHTML = programas.map(programa => `
        <div class="list-item">
            <div class="item-info">
                <div class="item-title">${programa.nombre || ''}</div>
                <div class="item-detail">
                    <span class="badge">${programa.nivel || ''}</span>
                    ${programa.duracion ? `<span class="badge" style="margin-left: 8px;">${programa.duracion}</span>` : ''}
                    ${programa.acreditada ? '<span class="badge" style="margin-left: 8px; background: #4CAF50;">Acreditada</span>' : ''}
                    ${programa.virtual ? '<span class="badge" style="margin-left: 8px; background: #2196F3;">Virtual</span>' : ''}
                </div>
                <div class="item-detail">Facultad: ${programa.facultad_nombre || 'Sin facultad'}</div>
                ${programa.perfil_profesional ? `<div class="item-detail">Perfil: ${programa.perfil_profesional}</div>` : ''}
            </div>
            <div class="item-actions">
                <button class="btn btn-info" onclick="viewPrograma(${programa.id})">Ver</button>
            </div>
        </div>
    `).join('');
}

function filterProgramas() {
    const search = (document.getElementById('search-programas')?.value || '').toLowerCase();
    const nivel = document.getElementById('filter-nivel')?.value || '';
    const facultad = document.getElementById('filter-facultad')?.value || '';

    const filtered = currentData.filter(programa => {
        const nombre = (programa.nombre || '').toLowerCase();
        const perfil = (programa.perfil_profesional || '').toLowerCase();
        const matchSearch = !search || nombre.includes(search) || perfil.includes(search);
        const matchNivel = !nivel || programa.nivel === nivel;
        const matchFacultad = !facultad || programa.facultad_id == facultad;
        return matchSearch && matchNivel && matchFacultad;
    });

    renderProgramas(filtered);
}

function viewPrograma(id) {
    const programa = currentData.find(p => p.id === id);
    if (programa) {
        alert(`${programa.nombre}\n\nNivel: ${programa.nivel}\nDuración: ${programa.duracion}\nFacultad: ${programa.facultad_nombre}\n\nPerfil: ${programa.perfil_profesional}`);
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
    } else if (currentSection === 'asesores') {
        openAddAsesorModal();
    }
}

async function openAddEstudianteModal() {
    try {
        const [facultadesData, carrerasData, asesoresData] = await Promise.all([
            fetch(`${API_BASE}/facultades/`).then(r => r.json()),
            fetch(`${API_BASE}/carreras/`).then(r => r.json()),
            fetch(`${API_BASE}/asesores/?activos=true`).then(r => r.json()),
        ]);
        const facultades = facultadesData.datos || [];
        const carreras = carrerasData.datos || [];
        const asesores = (asesoresData.datos || []).filter(a => a.activo);
        
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
            <div class="form-group">
                <label for="asesor_id">Asesor asignado</label>
                <select id="asesor_id" name="asesor_id">
                    <option value="">Sin asesor</option>
                    ${asesores.map(a => `<option value="${a.id}">${a.nombre_completo}${a.tipo === 'asesor_enlace' ? ' (Enlace)' : ''}</option>`).join('')}
                </select>
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
    const currentValue = carreraSelect.value;

    carreraSelect.querySelectorAll('option').forEach(option => {
        if (option.value === '') {
            option.style.display = 'block';
        } else {
            option.style.display = option.dataset.facultad === facultadId ? 'block' : 'none';
        }
    });

    // Solo resetear si la carrera actual no pertenece a la facultad seleccionada
    const selectedOption = carreraSelect.querySelector(`option[value="${currentValue}"]`);
    if (!currentValue || !selectedOption || selectedOption.style.display === 'none') {
        carreraSelect.value = '';
    }
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
    if (data.asesor_id) data.asesor_id = parseInt(data.asesor_id); else delete data.asesor_id;
    
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

// ── Import CSV/Excel ──────────────────────────────────────────────────────────

function openImportModal() {
    resetImportModal();
    document.getElementById('import-modal').classList.add('active');
}

function closeImportModal() {
    document.getElementById('import-modal').classList.remove('active');
    resetImportModal();
}

function resetImportModal() {
    document.getElementById('import-step-upload').style.display = 'block';
    document.getElementById('import-step-results').style.display = 'none';
    document.getElementById('import-file').value = '';
    document.getElementById('import-file-name').style.display = 'none';
    document.getElementById('import-file-name').textContent = '';
    document.getElementById('import-submit-btn').disabled = true;
    document.getElementById('import-summary').innerHTML = '';
    document.getElementById('import-errors').innerHTML = '';
}

(function initImportDropzone() {
    document.addEventListener('DOMContentLoaded', () => {
        const dropzone = document.getElementById('import-dropzone');
        const fileInput = document.getElementById('import-file');
        if (!dropzone || !fileInput) return;

        dropzone.addEventListener('click', () => fileInput.click());

        fileInput.addEventListener('change', () => {
            const file = fileInput.files[0];
            if (file) {
                const nameEl = document.getElementById('import-file-name');
                nameEl.textContent = file.name;
                nameEl.style.display = 'block';
                document.getElementById('import-submit-btn').disabled = false;
            }
        });

        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('dragover');
        });
        dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));
        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
            const file = e.dataTransfer.files[0];
            if (file) {
                const dt = new DataTransfer();
                dt.items.add(file);
                fileInput.files = dt.files;
                const nameEl = document.getElementById('import-file-name');
                nameEl.textContent = file.name;
                nameEl.style.display = 'block';
                document.getElementById('import-submit-btn').disabled = false;
            }
        });

        document.getElementById('import-modal').addEventListener('click', (e) => {
            if (e.target === document.getElementById('import-modal')) closeImportModal();
        });
    });
})();

async function submitImport() {
    const fileInput = document.getElementById('import-file');
    const file = fileInput.files[0];
    if (!file) return;

    const submitBtn = document.getElementById('import-submit-btn');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Importando...';

    try {
        const formData = new FormData();
        formData.append('archivo', file);

        const res = await fetch(`${API_BASE}/importar/estudiantes`, {
            method: 'POST',
            body: formData,
        });

        const data = await res.json();

        if (!res.ok) {
            showToast(data.error || 'Error al importar', true);
            submitBtn.disabled = false;
            submitBtn.textContent = 'Importar';
            return;
        }

        renderImportResults(data);
        document.getElementById('import-step-upload').style.display = 'none';
        document.getElementById('import-step-results').style.display = 'block';

        if (data.exitosos > 0) {
            loadEstudiantes();
            loadDashboard();
        }
    } catch (error) {
        console.error('Import error:', error);
        showToast('Error al importar: ' + error.message, true);
        submitBtn.disabled = false;
        submitBtn.textContent = 'Importar';
    }
}

function renderImportResults(data) {
    const summaryEl = document.getElementById('import-summary');
    summaryEl.innerHTML = `
        <div class="import-summary-cards">
            <div class="summary-card summary-total">
                <span class="summary-number">${data.total_filas}</span>
                <span class="summary-label">Filas procesadas</span>
            </div>
            <div class="summary-card summary-success">
                <span class="summary-number">${data.exitosos}</span>
                <span class="summary-label">Importados</span>
            </div>
            <div class="summary-card summary-error">
                <span class="summary-number">${data.con_errores}</span>
                <span class="summary-label">Con errores</span>
            </div>
        </div>
    `;

    const errorsEl = document.getElementById('import-errors');
    if (!data.errores || data.errores.length === 0) {
        errorsEl.innerHTML = '<p class="import-success-msg">Todos los registros fueron importados correctamente.</p>';
        return;
    }

    errorsEl.innerHTML = `
        <h3 class="import-errors-title">Filas con errores (${data.errores.length})</h3>
        <div class="import-errors-list">
            ${data.errores.map(fila => `
                <div class="import-error-row">
                    <div class="import-error-row-header">Fila ${fila.fila}</div>
                    <ul class="import-error-fields">
                        ${fila.errores.map(e => `
                            <li>
                                <span class="error-field">${e.campo}</span>
                                ${e.valor ? `<span class="error-value">"${e.valor}"</span>` : ''}
                                <span class="error-msg">${e.mensaje}</span>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            `).join('')}
        </div>
    `;
}

// ── CV Functions ──────────────────────────────────────────────────────────────

function verCV(estudianteId) {
    window.open(`${API_BASE}/estudiantes/${estudianteId}/cv`, '_blank');
}

async function eliminarCV(estudianteId) {
    if (!confirm('¿Eliminar el CV de este estudiante?')) return;
    try {
        const res = await fetch(`${API_BASE}/estudiantes/${estudianteId}/cv`, { method: 'DELETE' });
        const data = await res.json();
        if (res.ok) {
            showToast('CV eliminado');
            loadEstudiantes();
        } else {
            showToast(data.error || 'Error al eliminar CV', true);
        }
    } catch {
        showToast('Error al eliminar CV', true);
    }
}

function abrirUploadCV(estudianteId) {
    const existing = document.getElementById('cv-upload-modal');
    if (existing) existing.remove();

    const modal = document.createElement('div');
    modal.id = 'cv-upload-modal';
    modal.className = 'modal active';
    modal.innerHTML = `
        <div class="modal-content" style="max-width:460px">
            <span class="close" onclick="cerrarUploadCV()">&times;</span>
            <h2 style="margin-bottom:20px;color:var(--primary-color)">Subir CV</h2>
            <p style="font-size:14px;color:var(--text-light);margin-bottom:20px">
                Solo se aceptan archivos <strong>PDF</strong> (máx. 5 MB).
            </p>
            <div class="import-dropzone" id="cv-dropzone" onclick="document.getElementById('cv-file-input').click()">
                <div class="dropzone-icon">⬆</div>
                <p>Arrastra el PDF aquí o haz clic para seleccionar</p>
                <p class="dropzone-hint">PDF · máx. 5 MB</p>
                <input type="file" id="cv-file-input" accept=".pdf" style="display:none"
                       onchange="handleCVFileSelect(this)">
            </div>
            <div id="cv-file-name" style="display:none" class="import-file-name"></div>
            <div style="display:flex;gap:12px;justify-content:flex-end;margin-top:20px">
                <button class="btn btn-secondary" onclick="cerrarUploadCV()">Cancelar</button>
                <button class="btn btn-primary" id="cv-submit-btn" onclick="subirCV(${estudianteId})" disabled>Subir</button>
            </div>
        </div>
    `;
    modal.addEventListener('click', e => { if (e.target === modal) cerrarUploadCV(); });

    const dropzone = modal.querySelector('#cv-dropzone');
    dropzone.addEventListener('dragover', e => { e.preventDefault(); dropzone.classList.add('dragover'); });
    dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));
    dropzone.addEventListener('drop', e => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        const file = e.dataTransfer.files[0];
        if (file) setCVFile(file);
    });

    document.body.appendChild(modal);
}

function handleCVFileSelect(input) {
    if (input.files[0]) setCVFile(input.files[0]);
}

function setCVFile(file) {
    const nameEl = document.getElementById('cv-file-name');
    const submitBtn = document.getElementById('cv-submit-btn');
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        showToast('Solo se permiten archivos PDF', true);
        return;
    }
    if (file.size > 5 * 1024 * 1024) {
        showToast('El archivo supera los 5 MB', true);
        return;
    }
    nameEl.textContent = file.name;
    nameEl.style.display = 'block';
    submitBtn.disabled = false;
    submitBtn._cvFile = file;
}

async function subirCV(estudianteId) {
    const submitBtn = document.getElementById('cv-submit-btn');
    const file = submitBtn._cvFile;
    if (!file) return;

    submitBtn.disabled = true;
    submitBtn.textContent = 'Subiendo...';

    try {
        const formData = new FormData();
        formData.append('cv', file);

        const res = await fetch(`${API_BASE}/estudiantes/${estudianteId}/cv`, {
            method: 'POST',
            body: formData,
        });
        const data = await res.json();

        if (res.ok) {
            showToast('CV subido exitosamente');
            cerrarUploadCV();
            loadEstudiantes();
        } else {
            showToast(data.error || 'Error al subir CV', true);
            submitBtn.disabled = false;
            submitBtn.textContent = 'Subir';
        }
    } catch {
        showToast('Error al subir CV', true);
        submitBtn.disabled = false;
        submitBtn.textContent = 'Subir';
    }
}

function cerrarUploadCV() {
    const modal = document.getElementById('cv-upload-modal');
    if (modal) modal.remove();
}

// ─────────────────────────────────────────────────────────────────────────────

function debounce(func, delay) {
    let timeoutId;
    return (...args) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func(...args), delay);
    };
}

// ── ASESORES ──────────────────────────────────────────────────────────────────

const ESTADO_COLOR = {
    'Disponible':    '#27AE60',
    'En proceso':    '#2980B9',
    'Contratado':    '#8E44AD',
    'Por Finalizar': '#F39C12',
    'Finalizado':    '#95A5A6',
};

let todosAsesores = [];

async function loadAsesores() {
    const container = document.getElementById('asesores-list');
    container.innerHTML = '<p style="color:#999;padding:20px;">Cargando asesores...</p>';
    try {
        const res = await fetch(`${API_BASE}/asesores/`);
        const data = await res.json();
        todosAsesores = data.datos || [];
        renderAsesores(todosAsesores);
    } catch {
        container.innerHTML = '<p style="color:red;padding:20px;">Error al cargar asesores.</p>';
    }
}

function renderAsesores(lista) {
    const container = document.getElementById('asesores-list');
    if (!lista.length) {
        container.innerHTML = '<p style="color:#999;padding:20px;">No hay asesores registrados.</p>';
        return;
    }
    container.innerHTML = lista.map(a => {
        const stats = a.estadisticas || {};
        const activos = stats.total_activos ?? 0;
        const historico = stats.total_historico ?? 0;
        const porEstado = stats.por_estado || {};

        const barras = Object.entries(porEstado).map(([estado, cnt]) => {
            const color = ESTADO_COLOR[estado] || '#ccc';
            const pct = historico ? Math.round(cnt / historico * 100) : 0;
            return `<div class="asesor-barra-seg" style="width:${pct}%;background:${color};" title="${estado}: ${cnt}"></div>`;
        }).join('');

        const badges = Object.entries(porEstado).map(([estado, cnt]) => {
            const color = ESTADO_COLOR[estado] || '#ccc';
            return `<span class="asesor-badge" style="border-color:${color};color:${color};">${estado} <strong>${cnt}</strong></span>`;
        }).join('');

        const estadoLabel = a.activo
            ? '<span class="asesor-activo">Activo</span>'
            : '<span class="asesor-inactivo">Inactivo</span>';

        return `
        <div class="asesor-card" data-id="${a.id}">
            <div class="asesor-card-header">
                <div class="asesor-avatar">${a.nombre[0]}${a.apellido[0]}</div>
                <div class="asesor-info">
                    <h3>${a.nombre_completo} ${a.tipo === 'asesor_enlace' ? '<span style="font-size:11px;background:#e8f4fd;color:#2980B9;padding:2px 7px;border-radius:10px;font-weight:600;">Enlace</span>' : a.tipo === 'administrador' ? '<span style="font-size:11px;background:#fdf3e8;color:#e67e22;padding:2px 7px;border-radius:10px;font-weight:600;">Admin</span>' : ''}</h3>
                    <span class="asesor-email">${a.email}</span>
                    ${a.telefono ? `<span class="asesor-tel">${a.telefono}</span>` : ''}
                    ${a.tipo === 'asesor_enlace' && a.facultad_nombre ? `<span style="font-size:11px;color:#888;">Facultad: ${a.facultad_nombre}</span>` : ''}
                </div>
                <div class="asesor-card-actions">
                    ${estadoLabel}
                    <button class="btn-icon" onclick="editAsesor(${a.id})" title="Editar">✏️</button>
                    <button class="btn-icon" onclick="toggleAsesor(${a.id}, ${a.activo})" title="${a.activo ? 'Desactivar' : 'Activar'}">
                        ${a.activo ? '🔴' : '🟢'}
                    </button>
                    ${!['asesor','asesor_enlace'].includes(currentUser.role) ? `<button class="btn-icon" onclick="eliminarAsesor(${a.id}, '${a.nombre_completo.replace(/'/g, '&#39;')}')" title="Eliminar permanentemente">🗑️</button>` : ''}
                </div>
            </div>
            <div class="asesor-stats">
                <div class="asesor-stat">
                    <span class="asesor-stat-num">${activos}</span>
                    <span class="asesor-stat-label">Activos</span>
                </div>
                <div class="asesor-stat">
                    <span class="asesor-stat-num">${historico}</span>
                    <span class="asesor-stat-label">Histórico</span>
                </div>
            </div>
            ${historico > 0 ? `
            <div class="asesor-barra-bg">${barras}</div>
            <div class="asesor-badges">${badges}</div>` : ''}
            <button class="asesor-ver-btn" onclick="verEstudiantesAsesor(${a.id}, '${a.nombre_completo}')">
                Ver estudiantes
            </button>
        </div>`;
    }).join('');
}

document.getElementById('search-asesores')?.addEventListener('input', function() {
    const q = this.value.toLowerCase();
    renderAsesores(todosAsesores.filter(a =>
        `${a.nombre} ${a.apellido} ${a.email}`.toLowerCase().includes(q)
    ));
});

async function openAddAsesorModal() {
    editingId = null;
    const facultadesData = await fetch(`${API_BASE}/facultades/`).then(r => r.json()).catch(() => ({}));
    const facultades = facultadesData.datos || [];
    document.getElementById('modal-title').textContent = 'Nuevo Asesor';
    document.getElementById('form-fields').innerHTML = `
        <div class="form-group">
            <label>Nombre *</label>
            <input type="text" name="nombre" required>
        </div>
        <div class="form-group">
            <label>Apellido *</label>
            <input type="text" name="apellido" required>
        </div>
        <div class="form-group">
            <label>Email *</label>
            <input type="email" name="email" required>
        </div>
        <div class="form-group">
            <label>Teléfono</label>
            <input type="text" name="telefono">
        </div>
        <div class="form-group">
            <label>Tipo *</label>
            <select name="tipo" id="asesor-tipo" onchange="toggleAsesorFacultad()">
                ${_tipoOptions('asesor')}
            </select>
        </div>
        <div class="form-group" id="asesor-facultad-group" style="display:none;">
            <label>Facultad (requerida para Asesor Enlace)</label>
            <select name="facultad_id">
                <option value="">Seleccionar facultad...</option>
                ${facultades.map(f => `<option value="${f.id}">${f.nombre}</option>`).join('')}
            </select>
        </div>`;
    modalForm.onsubmit = (e) => _submitAsesorForm(e, null);
    document.getElementById('modal').style.display = 'flex';
}

async function editAsesor(id) {
    editingId = id;
    const [asesorData, facultadesData] = await Promise.all([
        fetch(`${API_BASE}/asesores/${id}`).then(r => r.json()),
        fetch(`${API_BASE}/facultades/`).then(r => r.json()).catch(() => ({})),
    ]);
    const a = asesorData.datos;
    const facultades = facultadesData.datos || [];
    document.getElementById('modal-title').textContent = 'Editar Asesor';
    document.getElementById('form-fields').innerHTML = `
        <div class="form-group">
            <label>Nombre *</label>
            <input type="text" name="nombre" value="${a.nombre}" required>
        </div>
        <div class="form-group">
            <label>Apellido *</label>
            <input type="text" name="apellido" value="${a.apellido}" required>
        </div>
        <div class="form-group">
            <label>Email *</label>
            <input type="email" name="email" value="${a.email}" required>
        </div>
        <div class="form-group">
            <label>Teléfono</label>
            <input type="text" name="telefono" value="${a.telefono || ''}">
        </div>
        <div class="form-group">
            <label>Tipo *</label>
            <select name="tipo" id="asesor-tipo" onchange="toggleAsesorFacultad()">
                ${_tipoOptions(a.tipo || 'asesor')}
            </select>
        </div>
        <div class="form-group" id="asesor-facultad-group" style="display:${a.tipo === 'asesor_enlace' ? 'block' : 'none'};">
            <label>Facultad (requerida para Asesor Enlace)</label>
            <select name="facultad_id">
                <option value="">Seleccionar facultad...</option>
                ${facultades.map(f => `<option value="${f.id}" ${f.id === a.facultad_id ? 'selected' : ''}>${f.nombre}</option>`).join('')}
            </select>
        </div>`;
    modalForm.onsubmit = (e) => _submitAsesorForm(e, id);
    document.getElementById('modal').style.display = 'flex';
}

function toggleAsesorFacultad() {
    const tipo = document.getElementById('asesor-tipo')?.value;
    const grupo = document.getElementById('asesor-facultad-group');
    if (grupo) grupo.style.display = tipo === 'asesor_enlace' ? 'block' : 'none';
}

function _tipoOptions(selected) {
    const opts = [
        ['asesor', 'Asesor'],
        ['asesor_enlace', 'Asesor Enlace'],
        ['administrador', 'Administrador'],
    ];
    return opts.map(([v, l]) => `<option value="${v}" ${selected === v ? 'selected' : ''}>${l}</option>`).join('');
}

async function toggleAsesor(id, activo) {
    const res = await fetch(`${API_BASE}/asesores/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ activo: !activo }),
    });
    if (res.ok) {
        showToast(activo ? 'Asesor desactivado' : 'Asesor activado');
        loadAsesores();
    } else {
        showToast('Error al actualizar asesor', true);
    }
}

async function eliminarAsesor(id, nombre) {
    const m = document.createElement('div');
    m.className = 'modal';
    m.style.cssText = 'display:flex;z-index:2000;';
    m.innerHTML = `
        <div class="modal-content" style="max-width:420px;">
            <h2>Eliminar asesor</h2>
            <p style="margin:12px 0 20px;">¿Estás seguro de que deseas eliminar a <strong>${nombre}</strong>?
               Esta acción desvincula al asesor del sistema. Los estudiantes asignados quedarán sin asesor.</p>
            <div style="display:flex;gap:10px;justify-content:flex-end;">
                <button class="btn btn-secondary" id="_del_cancel">Cancelar</button>
                <button class="btn btn-danger"    id="_del_confirm">Eliminar</button>
            </div>
        </div>`;
    document.body.appendChild(m);
    m.querySelector('#_del_cancel').addEventListener('click', () => m.remove());
    m.addEventListener('click', e => { if (e.target === m) m.remove(); });
    m.querySelector('#_del_confirm').addEventListener('click', async () => {
        m.remove();
        const res = await fetch(`${API_BASE}/asesores/${id}`, { method: 'DELETE' });
        if (res.ok) {
            showToast('Asesor eliminado');
            loadAsesores();
            loadDashboard();
        } else {
            const d = await res.json().catch(() => ({}));
            showToast(d.error || 'Error al eliminar asesor', true);
        }
    });
}

async function verEstudiantesAsesor(id, nombre) {
    const res = await fetch(`${API_BASE}/asesores/${id}/estudiantes`);
    const data = await res.json();
    const lista = data.datos || [];

    const filas = lista.length
        ? lista.map(e => `
            <tr>
                <td>${e.nombre} ${e.apellido}</td>
                <td>${e.numero_documento}</td>
                <td><span style="color:${ESTADO_COLOR[e.estado_practica]||'#666'}">${e.estado_practica}</span></td>
                <td>${e.carrera_id ? (e.carrera_nombre || e.carrera_id) : '—'}</td>
            </tr>`).join('')
        : '<tr><td colspan="4" style="text-align:center;color:#999;">Sin estudiantes asignados</td></tr>';

    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.style.display = 'flex';
    modal.innerHTML = `
        <div class="modal-content" style="max-width:700px;max-height:80vh;overflow-y:auto;">
            <span class="close" onclick="this.closest('.modal').remove()">&times;</span>
            <h2>Estudiantes de ${nombre}</h2>
            <table class="asesor-tabla-est">
                <thead><tr><th>Nombre</th><th>Documento</th><th>Estado</th><th>Programa</th></tr></thead>
                <tbody>${filas}</tbody>
            </table>
            <div style="margin-top:16px;text-align:right;">
                <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">Cerrar</button>
            </div>
        </div>`;
    document.body.appendChild(modal);
}

async function _submitAsesorForm(e, asesorId) {
    e.preventDefault();
    const fd = new FormData(modalForm);
    const body = Object.fromEntries(fd.entries());
    if (body.facultad_id) body.facultad_id = parseInt(body.facultad_id);
    else delete body.facultad_id;
    const url = asesorId ? `${API_BASE}/asesores/${asesorId}` : `${API_BASE}/asesores/`;
    const method = asesorId ? 'PUT' : 'POST';
    const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    });
    const data = await res.json();
    if (res.ok) {
        document.getElementById('modal').style.display = 'none';
        loadAsesores();
        if (!asesorId && data.datos?.username) {
            _showCredencialesModal(data.datos);
        } else {
            showToast('Asesor actualizado');
        }
    } else {
        showToast(data.error || 'Error al guardar asesor', true);
    }
}

function _showCredencialesModal(asesor) {
    const emailBadge = asesor.email_enviado
        ? `<span style="color:#27AE60;font-weight:600;">✓ Correo enviado a ${asesor.email}</span>`
        : `<span style="color:#E74C3C;font-weight:600;">✗ No se pudo enviar el correo — guarda estos datos manualmente</span>`;

    const m = document.createElement('div');
    m.className = 'modal';
    m.style.cssText = 'display:flex;z-index:2000;';
    m.innerHTML = `
        <div class="modal-content" style="max-width:480px;">
            <h2 style="margin-bottom:4px;">Asesor creado</h2>
            <p style="color:#666;font-size:13px;margin-bottom:16px;">${emailBadge}</p>

            <div style="background:#f4f6fa;border:1px solid #dde3ef;border-radius:8px;padding:16px 20px;margin-bottom:16px;">
                <div style="margin-bottom:12px;">
                    <span style="font-size:12px;color:#888;display:block;margin-bottom:2px;">USUARIO</span>
                    <span id="_cred_user" style="font-family:monospace;font-size:17px;font-weight:700;color:#1B1464;">${asesor.username}</span>
                    <button onclick="navigator.clipboard.writeText('${asesor.username}')" title="Copiar"
                        style="margin-left:8px;background:none;border:none;cursor:pointer;color:#56ACDE;font-size:13px;">📋</button>
                </div>
                <div>
                    <span style="font-size:12px;color:#888;display:block;margin-bottom:2px;">CONTRASEÑA TEMPORAL</span>
                    <span id="_cred_pw" style="font-family:monospace;font-size:17px;font-weight:700;color:#1B1464;">${asesor.password_temporal}</span>
                    <button onclick="navigator.clipboard.writeText('${asesor.password_temporal}')" title="Copiar"
                        style="margin-left:8px;background:none;border:none;cursor:pointer;color:#56ACDE;font-size:13px;">📋</button>
                </div>
            </div>

            <p style="font-size:12px;color:#999;margin-bottom:20px;">
                Esta contraseña no se volverá a mostrar. El asesor puede iniciar sesión de inmediato con estas credenciales.
            </p>
            <div style="text-align:right;">
                <button class="btn btn-primary" onclick="this.closest('.modal').remove()">Entendido</button>
            </div>
        </div>`;
    document.body.appendChild(m);
    m.addEventListener('click', e => { if (e.target === m) m.remove(); });
}
