// Tea management functionality
document.addEventListener('DOMContentLoaded', function() {
    // Load teas on page load
    loadTeas();

    // Setup form handlers
    const saveButton = document.getElementById('save-tea');
    if (saveButton) {
        saveButton.addEventListener('click', addTea);
    }

    // Setup tea type change handler
    const teaTypeSelect = document.getElementById('teaType');
    if (teaTypeSelect) {
        teaTypeSelect.addEventListener('change', function() {
            updateDefaultValues(this.value);
        });
    }

    // Setup timer handlers
    const startButton = document.getElementById('start-timer');
    const resetButton = document.getElementById('reset-timer');
    if (startButton) {
        startButton.addEventListener('click', function() {
            const teaName = document.getElementById('tea-name-display').textContent;
            const seconds = parseInt(document.getElementById('steep-time').value) * 60;
            startTimer(teaName, seconds);
        });
    }
    if (resetButton) {
        resetButton.addEventListener('click', function() {
            clearInterval(timerInterval);
            document.getElementById('timer-display').textContent = '00:00';
        });
    }
});

function updateDefaultValues(teaType) {
    fetch('/api/defaults')
        .then(response => response.json())
        .then(defaults => {
            if (teaType in defaults) {
                const values = defaults[teaType];
                document.getElementById('steep-temperature').value = values.temperature;
                document.getElementById('steep-time').value = values.steep_time;
            }
        })
        .catch(error => console.error('Error loading defaults:', error));
}

function loadTeas() {
    fetch('/api/teas')
        .then(response => response.json())
        .then(teas => {
            const tableBody = document.getElementById('tea-list');
            if (!tableBody) return;

            tableBody.innerHTML = '';
            teas.forEach(tea => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${tea.name}</td>
                    <td>${tea.type}</td>
                    <td>${tea.temperature}°F</td>
                    <td>${tea.steep_time} minutes</td>
                    <td>${tea.steep_count || 'N/A'}</td>
                    <td>
                        <button class="btn btn-primary btn-sm" onclick="showTimer('${tea.name}', ${tea.steep_time})">
                            Start Timer
                        </button>
                        <button class="btn btn-danger btn-sm ms-2" onclick="deleteTea('${tea.id}')">
                            Delete
                        </button>
                    </td>
                `;
                tableBody.appendChild(row);
            });
        })
        .catch(error => console.error('Error loading teas:', error));
}

function addTea() {
    const tea = {
        name: document.getElementById('teaName').value,
        type: document.getElementById('teaType').value,
        temperature: parseInt(document.getElementById('steep-temperature').value),
        steep_time: parseInt(document.getElementById('steep-time').value)
    };

    fetch('/api/teas', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(tea)
    })
    .then(response => response.json())
    .then(() => {
        loadTeas();
        document.getElementById('add-tea-form').reset();
        const modal = bootstrap.Modal.getInstance(document.getElementById('addTeaModal'));
        if (modal) modal.hide();
    })
    .catch(error => console.error('Error adding tea:', error));
}

function deleteTea(teaId) {
    if (confirm('Are you sure you want to delete this tea?')) {
        fetch(`/api/teas/${teaId}`, {
            method: 'DELETE'
        })
        .then(() => loadTeas())
        .catch(error => console.error('Error deleting tea:', error));
    }
}

let timerInterval;

function showTimer(teaName, steepTime) {
    document.getElementById('tea-name-display').textContent = teaName;
    document.getElementById('timer-display').textContent = formatTime(steepTime * 60);
    const modal = new bootstrap.Modal(document.getElementById('timerModal'));
    modal.show();
}

function startTimer(teaName, seconds) {
    clearInterval(timerInterval);
    
    const timerDisplay = document.getElementById('timer-display');
    let remainingTime = seconds;

    function updateTimer() {
        if (remainingTime <= 0) {
            clearInterval(timerInterval);
            timerDisplay.textContent = 'Done!';
            // Show notification
            if (Notification.permission === 'granted') {
                new Notification('Tea Timer', {
                    body: `${teaName} is ready!`,
                    icon: '/static/img/tea-icon.png'
                });
            }
            return;
        }

        timerDisplay.textContent = formatTime(remainingTime);
        remainingTime--;
    }

    updateTimer();
    timerInterval = setInterval(updateTimer, 1000);
}

function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
}
