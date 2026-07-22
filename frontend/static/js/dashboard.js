// Dashboard functionality

document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
});

async function loadDashboardData() {
    try {
        // Load appointments and radiographs data in parallel
        const [appointments, radiographs] = await Promise.all([
            API.get('/appointments/'),
            API.get('/patients/radiographs')
        ]);
        
        updateDashboardStats(appointments, radiographs);
        displayRecentAppointments(appointments);
        displayRecentRadiographs(radiographs);
        
    } catch (error) {
        console.error('Failed to load dashboard data:', error);
        showDashboardError();
    }
}

function updateDashboardStats(appointments, radiographs) {
    // Update appointment count
    document.getElementById('appointmentCount').textContent = appointments.length;
    
    // Update radiograph count
    document.getElementById('radiographCount').textContent = radiographs.length;
    
    // Calculate days to next appointment
    const nextAppointment = getNextAppointment(appointments);
    const nextAppointmentElement = document.getElementById('nextAppointment');
    
    if (nextAppointment) {
        const daysToNext = Math.ceil((new Date(nextAppointment.appointment_date) - new Date()) / (1000 * 60 * 60 * 24));
        nextAppointmentElement.textContent = daysToNext > 0 ? daysToNext : 'Today';
    } else {
        nextAppointmentElement.textContent = 'None';
    }
}

function getNextAppointment(appointments) {
    const now = new Date();
    const upcomingAppointments = appointments
        .filter(apt => new Date(apt.appointment_date) >= now && apt.status !== 'cancelled')
        .sort((a, b) => new Date(a.appointment_date) - new Date(b.appointment_date));
    
    return upcomingAppointments[0] || null;
}

function displayRecentAppointments(appointments) {
    const container = document.getElementById('recentAppointments');
    
    if (appointments.length === 0) {
        container.innerHTML = `
            <div class="text-center py-4">
                <i class="fas fa-calendar-plus fa-3x text-muted mb-3"></i>
                <p class="text-muted">No appointments scheduled</p>
                <a href="/appointments#book" class="btn btn-primary">Book Your First Appointment</a>
            </div>
        `;
        return;
    }
    
    // Show next 3 upcoming appointments
    const now = new Date();
    const upcomingAppointments = appointments
        .filter(apt => new Date(apt.appointment_date) >= now && apt.status !== 'cancelled')
        .sort((a, b) => new Date(a.appointment_date) - new Date(b.appointment_date))
        .slice(0, 3);
    
    if (upcomingAppointments.length === 0) {
        container.innerHTML = `
            <div class="text-center py-4">
                <i class="fas fa-calendar-check fa-3x text-muted mb-3"></i>
                <p class="text-muted">No upcoming appointments</p>
                <a href="/appointments#book" class="btn btn-primary">Book New Appointment</a>
            </div>
        `;
        return;
    }
    
    container.innerHTML = upcomingAppointments.map(appointment => {
        const date = new Date(appointment.appointment_date);
        const statusColor = getAppointmentStatusColor(appointment.status);
        
        return `
            <div class="appointment-card card mb-3" onclick="viewAppointment(${appointment.id})">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6 class="card-title mb-1">${Utils.capitalize(appointment.appointment_type)}</h6>
                            <p class="card-text text-muted mb-2">
                                <i class="fas fa-calendar me-2"></i>${Utils.formatDate(appointment.appointment_date)}
                            </p>
                            ${appointment.notes ? `<p class="card-text"><small class="text-muted">${appointment.notes}</small></p>` : ''}
                        </div>
                        <span class="badge bg-${statusColor}">${Utils.capitalize(appointment.status)}</span>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function displayRecentRadiographs(radiographs) {
    const container = document.getElementById('recentRadiographs');
    
    if (radiographs.length === 0) {
        container.innerHTML = `
            <div class="text-center py-4">
                <i class="fas fa-x-ray fa-2x text-muted mb-2"></i>
                <p class="text-muted mb-2">No radiographs uploaded</p>
                <a href="/radiographs#upload" class="btn btn-sm btn-outline-primary">Upload X-Ray</a>
            </div>
        `;
        return;
    }
    
    // Show most recent 3 radiographs
    const recentRadiographs = radiographs
        .sort((a, b) => new Date(b.upload_date) - new Date(a.upload_date))
        .slice(0, 3);
    
    container.innerHTML = recentRadiographs.map(radiograph => `
        <div class="radiograph-item mb-3" onclick="viewRadiograph(${radiograph.id})">
            <div class="radiograph-thumbnail">
                <i class="fas fa-x-ray fa-2x text-primary"></i>
            </div>
            <div class="text-center">
                <small class="text-muted d-block">${radiograph.original_filename}</small>
                <small class="text-muted">${new Date(radiograph.upload_date).toLocaleDateString()}</small>
            </div>
        </div>
    `).join('');
}

function getAppointmentStatusColor(status) {
    switch (status) {
        case 'scheduled':
            return 'primary';
        case 'completed':
            return 'success';
        case 'cancelled':
            return 'danger';
        default:
            return 'secondary';
    }
}

function viewAppointment(appointmentId) {
    window.location.href = `/appointments#${appointmentId}`;
}

function viewRadiograph(radiographId) {
    window.location.href = `/radiographs#${radiographId}`;
}

function showDashboardError() {
    const recentAppointments = document.getElementById('recentAppointments');
    const recentRadiographs = document.getElementById('recentRadiographs');
    
    const errorMessage = `
        <div class="alert alert-warning" role="alert">
            <i class="fas fa-exclamation-triangle me-2"></i>
            Unable to load data. <button class="btn btn-sm btn-outline-primary ms-2" onclick="loadDashboardData()">Try Again</button>
        </div>
    `;
    
    if (recentAppointments) {
        recentAppointments.innerHTML = errorMessage;
    }
    
    if (recentRadiographs) {
        recentRadiographs.innerHTML = errorMessage;
    }
    
    // Reset stats to loading state
    document.getElementById('appointmentCount').textContent = '-';
    document.getElementById('radiographCount').textContent = '-';
    document.getElementById('nextAppointment').textContent = '-';
}