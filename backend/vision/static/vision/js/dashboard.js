function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

async function authFetch(url, options = {}) {
    const defaultHeaders = {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken,
    };
    const config = {
        ...options,
        credentials: 'include',
        headers: {
            ...defaultHeaders,
            ...options.headers,
        },
    };

    const response = await fetch(url, config);
    if (response.status === 403 || response.status === 401) {
        window.location.href = '/auth/login/';
        throw new Error('Authentication failed');
    }
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response;
}

document.addEventListener('DOMContentLoaded', () => {
    authFetch('/api/auth/api-keys/').then(() => {
        setupWebSocket();
        fetchAnalysisHistory();
        setupApiKeyManagement();
        document.getElementById('config-form').addEventListener('submit', handleConfigUpdate);
        document.getElementById('logout-btn').addEventListener('click', handleLogout);
    }).catch(error => {
        console.log("Redirecting to login page due to auth error.");
    });
});

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

const modal = document.getElementById('config-modal');
const closeBtn = document.querySelector('.close-button');
closeBtn.onclick = () => {
    modal.style.display = "none";
};
window.onclick = (event) => {
    if (event.target === modal) {
        modal.style.display = "none";
    }
};

async function openConfigModal(prefix, name) {
    document.getElementById('modal-key-name').textContent = name;
    document.getElementById('config-key-prefix').value = prefix;

    try {
        const [configResponse, modelsResponse] = await Promise.all([
            authFetch(`/api/auth/api-keys/${prefix}/config/`),
            authFetch('/api/vision/models/')
        ]);
        const [config, models] = await Promise.all([configResponse.json(), modelsResponse.json()]);

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

        modal.style.display = "block";
    } catch (error) {
        console.error("Failed to fetch configuration for key:", prefix, error);
        alert('خطا در دریافت تنظیمات دستگاه.');
    }
}

async function handleConfigUpdate(event) {
    event.preventDefault();
    const form = event.target;
    const prefix = document.getElementById('config-key-prefix').value;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    data.flash_enabled = document.getElementById('flash_enabled').checked;

    const statusEl = document.getElementById('config-status');
    statusEl.textContent = 'در حال ذخیره...';
    statusEl.style.color = 'var(--text-secondary)';

    try {
        await authFetch(`/api/auth/api-keys/${prefix}/config/`, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
        statusEl.textContent = 'تنظیمات با موفقیت ذخیره شد!';
        statusEl.style.color = 'var(--color-success)';
    } catch (error) {
        console.error("Failed to update configuration:", error);
        statusEl.textContent = 'خطا در ذخیره تنظیمات.';
        statusEl.style.color = 'var(--color-error)';
    } finally {
        setTimeout(() => {
            statusEl.textContent = '';
            modal.style.display = "none";
        }, 2000);
    }
}

async function fetchAnalysisHistory() {
    const historyContainer = document.getElementById('history-container');
    try {
        const response = await authFetch('/api/vision/logs/');
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
        setupLazyLoading();
    } catch (error) {
        console.error("Failed to fetch analysis history:", error);
        historyContainer.innerHTML = '<p>خطا در دریافت تاریخچه تحلیل‌ها.</p>';
    }
}

function createHistoryCard(log) {
    const card = document.createElement('div');
    card.className = 'history-card';
    const formattedDate = new Date(log.created_at).toLocaleString('fa-IR', {dateStyle: 'short', timeStyle: 'short'});
    card.innerHTML = `
        <div class="images">
            <a href="${log.image1_url}" target="_blank"><img class="lazy" loading="lazy" data-src="${log.image1_url}" src="[https://placehold.co/400x300/f8f9fa/dee2e6?text=Loading]..." alt="Before"></a>
            <a href="${log.image2_url}" target="_blank"><img class="lazy" loading="lazy" data-src="${log.image2_url}" src="[https://placehold.co/400x300/f8f9fa/dee2e6?text=Loading]..." alt="After"></a>
        </div>
        <div class="details">
            <p>${log.description || 'توضیحی ثبت نشده است.'}</p>
            <span><strong>زمان:</strong> ${formattedDate}</span>
            <span><strong>مدل استفاده شده:</strong> ${log.model_used}</span>
        </div>
    `;
    return card;
}

function setupLazyLoading() {
    const lazyImages = document.querySelectorAll('img.lazy');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const image = entry.target;
                const imageUrl = image.dataset.src;

                authFetch(imageUrl)
                    .then(response => response.blob())
                    .then(blob => {
                        image.src = URL.createObjectURL(blob);
                    })
                    .catch(error => {
                        console.error(`Could not load image: ${imageUrl}`, error);
                        image.alt = "Failed to load image";
                    });

                image.classList.remove('lazy');
                observer.unobserve(image);
            }
        });
    });
    lazyImages.forEach(image => imageObserver.observe(image));
}

async function setupApiKeyManagement() {
    const generateBtn = document.getElementById('generate-key-btn');
    const apiKeyListContainer = document.getElementById('api-key-list');
    generateBtn.addEventListener('click', handleGenerateKey);
    apiKeyListContainer.addEventListener('click', (event) => {
        if (event.target.classList.contains('delete-key-btn')) {
            const keyPrefix = event.target.dataset.prefix;
            if (confirm(`آیا از حذف کلید با پیشوند ${keyPrefix} مطمئن هستید؟`)) {
                handleDeleteKey(keyPrefix);
            }
        }
        if (event.target.classList.contains('config-btn')) {
            const prefix = event.target.dataset.prefix;
            const name = event.target.dataset.name;
            openConfigModal(prefix, name);
        }
    });
    fetchApiKeys();
}

async function fetchApiKeys() {
    const apiKeyListContainer = document.getElementById('api-key-list');
    try {
        const response = await authFetch('/api/auth/api-keys/');
        const keys = await response.json();
        apiKeyListContainer.innerHTML = '';
        if (keys.length === 0) {
            apiKeyListContainer.innerHTML = '<p>هیچ کلید API ساخته نشده است.</p>';
            return;
        }
        const list = document.createElement('ul');
        list.className = 'key-list';
        keys.forEach(key => {
            const item = document.createElement('li');
            const formattedDate = new Date(key.created).toLocaleDateString('fa-IR');
            item.innerHTML = `
                <div>
                    <span class="key-name">${key.name}</span>
                    <span class="key-prefix">پیشوند: ${key.prefix}</span>
                </div>
                <div>
                    <span class="key-date">ساخته شده در: ${formattedDate}</span>
                    <button class="button button-secondary config-btn" data-prefix="${key.prefix}" data-name="${key.name}">تنظیمات</button>
                    <button class="button button-danger delete-key-btn" data-prefix="${key.prefix}">حذف</button>
                </div>
            `;
            list.appendChild(item);
        });
        apiKeyListContainer.appendChild(list);
    } catch (error) {
        console.error("Failed to fetch API keys:", error);
        apiKeyListContainer.innerHTML = '<p>خطا در دریافت لیست کلیدها.</p>';
    }
}

async function handleGenerateKey() {
    const keyNameInput = document.getElementById('api-key-name');
    const name = keyNameInput.value.trim() || 'new-esp32-device';
    try {
        const response = await authFetch('/api/auth/api-keys/', {
            method: 'POST',
            body: JSON.stringify({name: name})
        });
        const newKeyData = await response.json();
        const newKeyContainer = document.getElementById('new-api-key-container');
        const newKeyElement = document.getElementById('new-api-key');
        newKeyElement.textContent = newKeyData.key;
        newKeyContainer.style.display = 'block';
        keyNameInput.value = '';
        fetchApiKeys();
    } catch (error) {
        console.error("Failed to generate API key:", error);
        alert('خطا در ساخت کلید جدید.');
    }
}

async function handleDeleteKey(prefix) {
    try {
        await authFetch(`/api/auth/api-keys/${prefix}/`, {
            method: 'DELETE',
        });
        fetchApiKeys();
    } catch (error) {
        console.error(`Failed to delete key ${prefix}:`, error);
        alert('خطا در حذف کلید.');
    }
}

async function handleLogout() {
    try {
        await authFetch('/api/auth/logout/', {method: 'POST'});
        window.location.href = '/auth/login/';
    } catch (error) {
        console.error('Logout failed:', error);
        alert('خروج از سیستم با خطا مواجه شد.');
    }
}