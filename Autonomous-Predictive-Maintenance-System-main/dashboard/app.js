/**
 * AutoPilot Maintenance Dashboard - JavaScript
 * Handles navigation, data loading, and real-time updates
 */

// Fleet data from telemetry
const fleetData = {
    VH001: { id: 'VH001', make: 'Tata', model: 'Nexon EV', status: 'normal', owner: 'Rajesh S.' },
    VH002: { id: 'VH002', make: 'Mahindra', model: 'XUV700', status: 'warning', owner: 'Priya P.' },
    VH003: { id: 'VH003', make: 'Maruti', model: 'Grand Vitara', status: 'normal', owner: 'Amit K.' },
    VH004: { id: 'VH004', make: 'Hyundai', model: 'Creta', status: 'warning', owner: 'Sunita R.' },
    VH005: { id: 'VH005', make: 'Kia', model: 'Seltos', status: 'normal', owner: 'Vikram S.' },
    VH006: { id: 'VH006', make: 'Toyota', model: 'Innova', status: 'critical', owner: 'Gurpreet K.' },
    VH007: { id: 'VH007', make: 'Honda', model: 'City', status: 'excellent', owner: 'Neha A.' },
    VH008: { id: 'VH008', make: 'Skoda', model: 'Kushaq', status: 'normal', owner: 'Rahul V.' },
    VH009: { id: 'VH009', make: 'MG', model: 'Hector', status: 'normal', owner: 'Sanjay D.' },
    VH010: { id: 'VH010', make: 'VW', model: 'Taigun', status: 'excellent', owner: 'Lakshmi R.' }
};

// Page titles for each view
const pageTitles = {
    owner: { title: 'Vehicle Owner Dashboard', subtitle: 'Monitor your vehicle\'s health and maintenance' },
    'service-center': { title: 'Service Center Dashboard', subtitle: 'Manage bookings, technicians, and inventory' },
    manufacturer: { title: 'Manufacturer Insights', subtitle: 'RCA/CAPA analysis and quality improvement' },
    fleet: { title: 'Fleet Status Overview', subtitle: 'Monitor all vehicles in real-time' },
    'agent-logs': { title: 'Agent Activity Monitor', subtitle: 'UEBA-secured agent interaction logs' }
};

// Navigation handling
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        const view = item.dataset.view;
        switchView(view);
    });
});

function switchView(viewName) {
    // Update nav active state
    document.querySelectorAll('.nav-item').forEach(nav => {
        nav.classList.remove('active');
        if (nav.dataset.view === viewName) {
            nav.classList.add('active');
        }
    });

    // Update page title
    const pageInfo = pageTitles[viewName];
    if (pageInfo) {
        document.getElementById('page-title').textContent = pageInfo.title;
        document.getElementById('page-subtitle').textContent = pageInfo.subtitle;
    }

    // Show correct view
    document.querySelectorAll('.view-section').forEach(section => {
        section.classList.remove('active');
    });

    const viewId = `${viewName}-view`;
    const viewElement = document.getElementById(viewId);
    if (viewElement) {
        viewElement.classList.add('active');
    }

    // Load view-specific data
    if (viewName === 'fleet') {
        loadFleetGrid();
    }
}

// Load fleet status grid
function loadFleetGrid() {
    const grid = document.getElementById('fleet-grid');
    if (!grid) return;

    grid.innerHTML = '';

    Object.values(fleetData).forEach(vehicle => {
        const card = document.createElement('div');
        card.className = `fleet-vehicle ${vehicle.status}`;
        card.innerHTML = `
            <h4>${vehicle.id}</h4>
            <p>${vehicle.make} ${vehicle.model}</p>
            <p>${vehicle.owner}</p>
        `;
        card.addEventListener('click', () => {
            showVehicleDetails(vehicle);
        });
        grid.appendChild(card);
    });
}

// Show vehicle details modal (simplified)
function showVehicleDetails(vehicle) {
    alert(`Vehicle: ${vehicle.id}\n${vehicle.make} ${vehicle.model}\nOwner: ${vehicle.owner}\nStatus: ${vehicle.status.toUpperCase()}`);
}

// Real-time telemetry simulation
function updateTelemetry() {
    const bars = document.querySelectorAll('.telemetry-fill');
    bars.forEach(bar => {
        const currentWidth = parseFloat(bar.style.width);
        const variance = (Math.random() - 0.5) * 5;
        const newWidth = Math.min(100, Math.max(0, currentWidth + variance));
        bar.style.width = `${newWidth}%`;
    });
}

// Agent activity log simulation
function addAgentLogEntry() {
    const log = document.getElementById('agent-activity-log');
    if (!log) return;

    const agents = [
        'data_analysis_agent',
        'diagnosis_agent',
        'scheduling_agent',
        'customer_outreach_agent',
        'feedback_agent'
    ];

    const actions = [
        'Analyzed telemetry for VH00X',
        'Predicted maintenance need',
        'Checked appointment availability',
        'Sent notification to owner',
        'Updated maintenance record'
    ];

    const now = new Date();
    const time = now.toTimeString().slice(0, 8);
    const agent = agents[Math.floor(Math.random() * agents.length)];
    const action = actions[Math.floor(Math.random() * actions.length)].replace('VH00X', `VH00${Math.floor(Math.random() * 9) + 1}`);

    const entry = document.createElement('div');
    entry.className = 'log-entry';
    entry.innerHTML = `
        <span class="log-time">${time}</span>
        <span class="log-agent">${agent}</span>
        <span class="log-action">${action}</span>
        <span class="log-status safe">✓ Normal</span>
    `;

    log.insertBefore(entry, log.firstChild);

    // Keep only last 20 entries
    while (log.children.length > 20) {
        log.removeChild(log.lastChild);
    }
}

// Search functionality
document.getElementById('vehicle-search')?.addEventListener('input', (e) => {
    const query = e.target.value.toUpperCase();
    if (query && fleetData[query]) {
        showVehicleDetails(fleetData[query]);
    }
});

// Schedule Service button handlers
document.querySelectorAll('.btn-primary').forEach(btn => {
    if (btn.textContent.includes('Schedule') || btn.textContent.includes('Confirm') || btn.textContent.includes('Book')) {
        btn.addEventListener('click', () => {
            showBookingConfirmation();
        });
    }
});

function showBookingConfirmation() {
    const confirmed = confirm('🚗 Schedule Service Appointment?\n\nVehicle: VH002 - XUV700\nService: Brake pad replacement, Coolant check\nDate: December 16, 2024\nTime: 9:00 AM\nLocation: QuickFix Bangalore\n\nProceed with booking?');

    if (confirmed) {
        alert('✅ Appointment Confirmed!\n\nBooking Reference: BK20241214120000\n\nYou will receive a confirmation notification shortly.');
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Load fleet grid if on fleet view
    loadFleetGrid();

    // Start real-time updates
    setInterval(updateTelemetry, 3000);
    setInterval(addAgentLogEntry, 5000);

    console.log('🚗 AutoPilot Maintenance Dashboard Initialized');
    console.log('📊 Monitoring 10 vehicles');
    console.log('🤖 13 AI Agents Active');
    console.log('🔒 UEBA Security Enabled');
});
