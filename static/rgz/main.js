document.addEventListener('DOMContentLoaded', function () {
    const user = JSON.parse(localStorage.getItem('user'));
    if (!user) {
        alert('Пожалуйста, авторизуйтесь');
        window.location.href = "/rgz/login";
    }

    const transferForm = document.getElementById('transfer-form');
    transferForm.addEventListener('submit', function (event) {
        event.preventDefault();
        transferFunds();
    });

    // Функция для отображения формы логина
    function showLoginForm() {
        const loginForm = document.getElementById('login-form');
        loginForm.style.display = 'block';

        // Обработчик формы логина
        loginForm.addEventListener('submit', function (event) {
            event.preventDefault();

            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;

            // Отправляем запрос на сервер для авторизации
            authenticateUser(username, password);
        });
    }

    // Функция для авторизации пользователя
    async function authenticateUser(username, password) {
        const response = await fetch('/rgz/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
            credentials: 'include'
        });
    
        const data = await response.json();
    
        if (data.error) {
            alert(data.error);
        } else {
            // Сохраняем данные пользователя в localStorage
            localStorage.setItem('user', JSON.stringify(data));
            if (data.redirect) {
                window.location.href = data.redirect;
            } else {
                window.location.href = "/rgz/dashboard";
            }
        }
    }

    // Загружаем данные пользователя после авторизации
    async function loadUserData(user) {
        const response = await fetch(`${apiUrl}users/${user.id}`, {
            credentials: 'include'  // Включаем cookies
        });

        const data = await response.json();

        if (data.error) {
            alert(data.error);
        } else {
            renderUserDashboard(data);
        }
    }

    // Отображаем данные пользователя на главной странице
    function renderUserDashboard(user) {
        const dashboard = document.getElementById('dashboard');
        dashboard.innerHTML = `
            <h1>Здравствуйте, ${user.full_name}</h1>
            <p>Баланс: ${user.balance} ₽</p>
            <p>Телефон: ${user.phone}</p>
            <p>Номер счета: ${user.account_number}</p>
            <button id="logout">Выйти</button>
        `;
    
        const logoutButton = document.getElementById('logout');
        logoutButton.addEventListener('click', logout);
    
        // Отображаем действия в зависимости от типа пользователя
        if (user.user_type === 'user') {
            renderClientActions(user);
        } else if (user.user_type === 'manager') {
            renderManagerActions(user);
        }
    }

    // Действия для клиента
    function renderClientActions(user) {
        const actions = document.getElementById('actions');
        actions.innerHTML = `
            <h2>Перевод средств</h2>
            <form id="transfer-form">
                <input type="text" id="recipient-account" placeholder="Номер счета получателя" required>
                <input type="number" id="amount" placeholder="Сумма перевода" required>
                <button type="submit">Перевести</button>
            </form>
            <h2>История операций</h2>
            <button id="show-history">Показать историю</button>
            <div id="history"></div>
        `;

        // Обработчик формы перевода средств
        const transferForm = document.getElementById('transfer-form');
        transferForm.addEventListener('submit', function (event) {
            event.preventDefault();
            const recipientAccount = document.getElementById('recipient-account').value;
            const amount = parseFloat(document.getElementById('amount').value);
            transferMoney(user.id, recipientAccount, amount);
        });

        // Обработчик для показа истории
        const showHistoryButton = document.getElementById('show-history');
        showHistoryButton.addEventListener('click', function () {
            loadTransactionHistory(user.id);
        });
    }

    async function transferMoney(userId, recipientAccount, amount) {
        try {
            const response = await fetch('/rgz/transfer', {  // Используем /rgz/transfer
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sender_id: userId, receiver_id: recipientAccount, amount }),
                credentials: 'include',
                signal: AbortSignal.timeout(5000)
            });
    
            if (!response.ok) {
                const errorData = await response.json();
                console.error("Ошибка при переводе средств:", errorData.error || response.statusText);
                throw new Error(errorData.error || "Ошибка при переводе средств");
            }
    
            const data = await response.json();
            console.log("Перевод выполнен успешно:", data.message);
            return data;
        } catch (error) {
            console.error("Ошибка при выполнении запроса:", error.message);
            throw error;
        }
    }

    // Функция для загрузки истории операций
    async function loadTransactionHistory(userId) {
        const response = await fetch(`${apiUrl}transaction_history`, {
            credentials: 'include'  // Включаем cookies
        });
    
        const data = await response.json();
    
        if (data.error) {
            alert(data.error);
        } else {
            const historyList = document.getElementById('history');
            historyList.innerHTML = '<h2>История переводов:</h2>';
            data.forEach(transaction => {
                historyList.innerHTML += `
                    <p>${transaction.date}: ${transaction.amount} ₽ (Получено от ${transaction.sender_id})</p>
                `;
            });
        }
    }

    // Действия для менеджера
    function renderManagerActions(user) {
        const actions = document.getElementById('actions');
        actions.innerHTML = `
            <h2>Управление пользователями</h2>
            <button id="create-user">Создать пользователя</button>
            <div id="user-list"></div>
        `;

        const createUserButton = document.getElementById('create-user');
        createUserButton.addEventListener('click', function () {
            showCreateUserModal();
        });

        loadUsers();
    }

    // Функция для отображения модального окна создания пользователя
    function showCreateUserModal() {
        const modal = document.getElementById('create-user-modal');
        modal.style.display = 'block';

        const createUserForm = document.getElementById('create-user-form');
        createUserForm.addEventListener('submit', function (event) {
            event.preventDefault();
            createUser();
        });
    }

    // Функция для создания пользователя
    async function createUser() {
        const fullName = document.getElementById('full-name').value;
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const phone = document.getElementById('phone').value;
        const accountNumber = document.getElementById('account-number').value;
        const balance = document.getElementById('balance').value;
        const userType = document.getElementById('user-type').value;
    
        const response = await fetch('/rgz/users', {
            method: 'POST',  // Убедитесь, что используется POST
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                full_name: fullName,
                username: username,
                password: password,
                phone: phone,
                account_number: accountNumber,
                balance: balance,
                user_type: userType
            })
        });
    
        const data = await response.json();
        if (response.ok) {
            alert('Пользователь успешно создан');
        } else {
            alert(data.error || 'Ошибка при создании пользователя');
        }
    }

    // Функция для загрузки списка всех пользователей
    async function loadUsers() {
        try {
            const response = await fetch('/rgz/users', {
                credentials: 'include'  // Включаем куки
            });
    
            if (!response.ok) {
                throw new Error('Ошибка при загрузке пользователей');
            }
    
            const data = await response.json();
            if (data.error) {
                alert(data.error);
            } else {
                const userList = document.getElementById('user-list');
                userList.innerHTML = '<h3>Список пользователей:</h3>';
                data.users.forEach(user => {  // Используем data.users
                    userList.innerHTML += `
                        <p>${user.full_name} (${user.username})</p>
                    `;
                });
            }
        } catch (error) {
            console.error('Ошибка:', error);
        }
    }

    // Функция для редактирования пользователя
    async function editUser(userId) {
        const fullName = prompt('Введите новое имя:');
        const balance = prompt('Введите новый баланс:');
        
        const response = await fetch(`${apiUrl}users/${userId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ full_name: fullName, balance }),
            credentials: 'include'  // Включаем cookies
        });

        const data = await response.json();

        if (data.error) {
            alert(data.error);
        } else {
            alert('Пользователь успешно отредактирован');
            loadUsers();
        }
    }

    // Функция для удаления пользователя
    async function deleteUser(userId) {
        const response = await fetch(`${apiUrl}users/${userId}`, {
            method: 'DELETE',
            credentials: 'include'  // Включаем cookies
        });

        const data = await response.json();

        if (data.error) {
            alert(data.error);
        } else {
            alert('Пользователь успешно удален');
            loadUsers();
        }
    }

    // Функция для выхода
    function logout() {
        fetch('/rgz/logout', { method: 'POST', credentials: 'include' })
            .then(response => {
                if (response.ok) {
                    localStorage.removeItem('user');  // Очищаем данные пользователя
                    window.location.href = '/rgz/login';
                }
            });
    }

    // Функция для скрытия модального окна
    function hideModal() {
        const modal = document.getElementById('create-user-modal');
        modal.style.display = 'none';
    }
});

function viewTransactionHistory() {
    window.location.href = '/rgz/transaction_history'; 
}

async function transferFunds() {
    const receiverPhone = document.getElementById('receiver-phone').value;
    const amount = parseFloat(document.getElementById('amount').value);

    if (!receiverPhone || !amount || amount <= 0) {
        alert('Пожалуйста, заполните все поля корректно.');
        return;
    }

    const transferButton = document.getElementById('transfer-button');
    const loadingDiv = document.getElementById('loading');
    transferButton.disabled = true;
    loadingDiv.style.display = 'block';

    try {
        const response = await fetch("/rgz/transfer", {  // Используем /rgz/transfer
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ receiver_phone: receiverPhone, amount: amount })
        });

        const result = await response.json();
        const resultDiv = document.getElementById('transfer-result');

        if (response.ok) {
            resultDiv.innerText = 'Перевод успешно выполнен';
            document.getElementById('receiver-phone').value = '';
            document.getElementById('amount').value = '';
        } else {
            resultDiv.innerText = result.error || 'Ошибка при переводе средств';
        }
    } catch (error) {
        console.error('Ошибка:', error);
        document.getElementById('transfer-result').innerText = 'Ошибка при выполнении запроса';
    } finally {
        transferButton.disabled = false;
        loadingDiv.style.display = 'none';
    }
}

async function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    const response = await fetch('/rgz/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
        credentials: 'include'  // Включаем cookies
    });
    const data = await response.json();
    if (response.ok) {
        localStorage.setItem('user', JSON.stringify(data));  // Сохранение данных пользователя
        window.location.href = '/rgz/dashboard';
    } else {
        alert(data.error);
    }
}

function logout() {
    fetch('/rgz/logout', { method: 'POST', credentials: 'include' })
        .then(response => {
            if (response.ok) {
                window.location.href = '/rgz/login';
            }
        });
}