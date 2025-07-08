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

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(loginForm);
            const data = Object.fromEntries(formData.entries());
            const errorMessageEl = document.getElementById('error-message');
            errorMessageEl.textContent = '';

            try {
                const response = await fetch('/api/auth/login/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken,
                    },
                    credentials: 'include',
                    body: JSON.stringify(data),
                });
                if (response.ok) {
                    window.location.href = '/dashboard/';
                } else {
                    const errorData = await response.json();
                    errorMessageEl.textContent = errorData.detail || 'نام کاربری یا رمز عبور اشتباه است.';
                }
            } catch (error) {
                errorMessageEl.textContent = 'خطا در برقراری ارتباط با سرور.';
            }
        });
    }

    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(registerForm);
            const data = Object.fromEntries(formData.entries());
            const errorMessageEl = document.getElementById('error-message');
            errorMessageEl.textContent = '';

            try {
                const response = await fetch('/api/auth/register/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken,
                    },
                    credentials: 'include',
                    body: JSON.stringify(data),
                });
                if (response.ok) {
                    alert('ثبت نام با موفقیت انجام شد! اکنون می‌توانید وارد شوید.');
                    window.location.href = '/auth/login/';
                } else {
                    const errorData = await response.json();
                    const errors = Object.values(errorData).flat().join('\n');
                    errorMessageEl.textContent = errors || 'خطا در ثبت نام.';
                }
            } catch (error) {
                errorMessageEl.textContent = 'خطا در برقراری ارتباط با سرور.';
            }
        });
    }
});