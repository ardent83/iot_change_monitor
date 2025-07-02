document.addEventListener('DOMContentLoaded', () => {
    setupWebSocket();
    fetchConfigAndPopulateForm();
    fetchAnalysisHistory();

    const configForm = document.getElementById('config-form');
    configForm.addEventListener('submit', handleConfigUpdate);
});

// --- WebSocket for Live Logs ---
function setupWebSocket() {
    const logContainer = document.getElementById('log-container');
    const logSocket = new WebSocket(`ws://${window.location.host}/ws/logs/`);

    logSocket.onopen = (e) => addLogEntry('--- Connected to Log Server ---', '#007bff');
    logSocket.onmessage = (e) => {
        const data = JSON.parse(e.data);
        addLogEntry(data.message);
    };
    logSocket.onclose = (e) => addLogEntry('--- Connection lost. Please refresh. ---', '#dc3545');
    logSocket.onerror = (e) => addLogEntry('--- WebSocket Error ---', '#dc3545');

    function addLogEntry(text, color = '#212529') {
        const timestamp = new Date().toLocaleTimeString('fa-IR');
        const newLog = document.createElement('div');
        newLog.className = 'log-entry';
        newLog.style.color = color;
        newLog.innerHTML = `<span class="log-timestamp">${timestamp}</span>${text}`;
        logContainer.appendChild(newLog);
        logContainer.scrollTop = logContainer.scrollHeight;
    }
}

// --- Device Configuration ---
async function fetchConfigAndPopulateForm() {
    try {
        const [config, models] = await Promise.all([
            fetch('/api/vision/config/').then(res => res.json()),
            fetch('/api/vision/models/').then(res => res.json())
        ]);

        document.getElementById('flash_enabled').checked = config.flash_enabled;
        document.getElementById('delay_seconds').value = config.delay_seconds;
        document.getElementById('prompt_context').value = config.prompt_context || '';

        const modelSelect = document.getElementById('default_model');
        modelSelect.innerHTML = '';
        models.forEach(model => {
            const option = document.createElement('option');
            option.value = model.name;
            option.textContent = model.description;
            if (model.name === config.default_model) {
                option.selected = true;
            }
            modelSelect.appendChild(option);
        });

    } catch (error) {
        console.error("Failed to fetch configuration:", error);
        document.getElementById('config-status').textContent = 'خطا در دریافت تنظیمات.';
    }
}

async function handleConfigUpdate(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    data.flash_enabled = document.getElementById('flash_enabled').checked;

    const statusEl = document.getElementById('config-status');
    statusEl.textContent = 'در حال ذخیره...';
    statusEl.style.color = 'var(--text-secondary)';

    try {
        const response = await fetch('/api/vision/config/', {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`Server responded with ${response.status}`);
        }

        statusEl.textContent = 'تنظیمات با موفقیت ذخیره شد!';
        statusEl.style.color = 'var(--color-success)';

    } catch (error) {
        console.error("Failed to update configuration:", error);
        statusEl.textContent = 'خطا در ذخیره تنظیمات.';
        statusEl.style.color = 'var(--color-error)';
    } finally {
        setTimeout(() => statusEl.textContent = '', 3000);
    }
}

// --- Analysis History ---
async function fetchAnalysisHistory() {
    const historyContainer = document.getElementById('history-container');
    try {
        const response = await fetch('/api/vision/logs/');
        if (!response.ok) throw new Error('Network response was not ok.');

        const logs = await response.json();

        historyContainer.innerHTML = '';
        if (logs.length === 0) {
            historyContainer.innerHTML = '<p>هیچ تحلیل سابقی یافت نشد.</p>';
            return;
        }

        logs.forEach(log => {
            const card = createHistoryCard(log);
            historyContainer.appendChild(card);
        });

    } catch (error) {
        console.error("Failed to fetch analysis history:", error);
        historyContainer.innerHTML = '<p>خطا در دریافت تاریخچه تحلیل‌ها.</p>';
    }
}

function createHistoryCard(log) {
    const card = document.createElement('div');
    card.className = 'history-card';

    const formattedDate = new Date(log.created_at).toLocaleString('fa-IR', { dateStyle: 'short', timeStyle: 'short' });

    card.innerHTML = `
        <div class="images">
            <a href="${log.image1}" target="_blank"><img src="${log.image1}" alt="Before"></a>
            <a href="${log.image2}" target="_blank"><img src="${log.image2}" alt="After"></a>
        </div>
        <div class="details">
            <p>${log.description || 'توضیحی ثبت نشده است.'}</p>
            <span><strong>زمان:</strong> ${formattedDate}</span>
            <span><strong>مدل استفاده شده:</strong> ${log.model_used}</span>
        </div>
    `;
    return card;
}
