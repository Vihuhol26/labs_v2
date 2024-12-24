// Функция для отправки JSON-RPC запросов
async function jsonRpcRequest(method, params = {}) {
    const response = await fetch('/api/jsonrpc', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            jsonrpc: '2.0',
            method: method,
            params: params,
            id: Math.random().toString(36).substr(2, 9) // Уникальный ID запроса
        })
    });

    const data = await response.json();

    if (data.error) {
        console.error('Ошибка JSON-RPC:', data.error);
        alert('Ошибка: ' + data.error.message);
        return null;
    }

    return data.result;
}

// Функция для проверки формы перевода
function validateTransferForm(form) {
    const amountInput = form.querySelector('input[name="amount"]');
    const amount = parseFloat(amountInput.value);

    if (amount <= 0) {
        alert('Сумма перевода должна быть больше нуля');
        return false; // Предотвращаем отправку формы
    }

    return true; // Форма прошла проверку
}

// Привязка проверки к форме перевода
document.addEventListener('DOMContentLoaded', function () {
    const transferForm = document.getElementById('transferForm');

    if (transferForm) {
        transferForm.addEventListener('submit', function (event) {
            if (!validateTransferForm(transferForm)) {
                event.preventDefault(); // Предотвращаем отправку формы, если проверка не пройдена
            }
        });
    }
});

// Для получения списка пользователей
async function loadUsers() {
    const users = await jsonRpcRequest('get_users');
    if (users) {
        const usersList = document.getElementById('users-list');
        usersList.innerHTML = ''; // Очищаем список
        users.forEach(user => {
            const row = document.createElement('div');
            row.textContent = `ID: ${user.id}, ФИО: ${user.full_name}`;
            row.style.cursor = 'pointer';
            row.addEventListener('click', () => {
                document.getElementById('receiver_id').value = user.id;
                modal.style.display = 'none';
            });
            usersList.appendChild(row);
        });
    }
}

// Для создания пользователя
async function createUser(full_name, username, password, phone, account_number, user_type) {
    const result = await jsonRpcRequest('create_user_rpc', {
        full_name: full_name,
        username: username,
        password: password,
        phone: phone,
        account_number: account_number,
        user_type: user_type
    });

    if (result) {
        alert('Пользователь успешно создан!');
        loadUsers(); // Обновляем список пользователей
    }
}

// Для удаления пользователя
async function deleteUser(user_id) {
    const result = await jsonRpcRequest('delete_user_rpc', { user_id: user_id });
    if (result) {
        alert('Пользователь успешно удален!');
        loadUsers(); // Обновляем список пользователей
    }
}