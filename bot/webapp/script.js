const catalog = [
    { vendor_id: 1, vendor_name: "Рога и копыта", vendor_type: "Ресторан", item_name: "Суп Шурпа", cost: 180, url_picture: "" },
    { vendor_id: 1, vendor_name: "Рога и копыта", vendor_type: "Ресторан", item_name: "Суп Лагман", cost: 200, url_picture: "" },
    { vendor_id: 1, vendor_name: "Рога и копыта", vendor_type: "Ресторан", item_name: "Шашлык", cost: 250, url_picture: "" },
    { vendor_id: 1, vendor_name: "Рога и копыта", vendor_type: "Ресторан", item_name: "Самса", cost: 200, url_picture: "" },
    { vendor_id: 1, vendor_name: "Рога и копыта", vendor_type: "Ресторан", item_name: "Чебурек", cost: 100, url_picture: "" },
    { vendor_id: 2, vendor_name: "Яхтинг", vendor_type: "Яхтинг", item_name: "Яхта Надежда", cost: 10000, url_picture: "" },
    { vendor_id: 2, vendor_name: "Яхтинг", vendor_type: "Яхтинг", item_name: "Яхта Екатерина", cost: 12000, url_picture: "" },
    { vendor_id: 2, vendor_name: "Яхтинг", vendor_type: "Яхтинг", item_name: "Яхта Изольда", cost: 16000, url_picture: "" },
    { vendor_id: 2, vendor_name: "Яхтинг", vendor_type: "Яхтинг", item_name: "Яхта Светлана", cost: 20000, url_picture: "" }
];

const cart = [];
let tg = window.Telegram.WebApp;

function renderCatalog() {
    const catalogContainer = document.getElementById('catalog');
    catalog.forEach(item => {
        const itemDiv = document.createElement('div');
        itemDiv.classList.add('item');
        itemDiv.innerHTML = `
            <h3>${item.item_name}</h3>
            <p>Цена: ${item.cost} руб.</p>
            <button onclick="addToCart('${item.item_name}', ${item.cost})">Добавить в корзину</button>
        `;
        catalogContainer.appendChild(itemDiv);
    });
}

function addToCart(item_name, cost) {
    cart.push({ item_name, cost });
    renderCart();
}

function renderCart() {
    const cartItemsContainer = document.getElementById('cart-items');
    cartItemsContainer.innerHTML = '';
    cart.forEach(item => {
        const li = document.createElement('li');
        li.textContent = `${item.item_name} - ${item.cost} руб.`;
        cartItemsContainer.appendChild(li);
    });
}

function checkout() {
    if (cart.length === 0) {
        alert('Ваша корзина пуста!');
        return;
    }

    // Получение данных пользователя из Telegram WebApp
    const user = window.Telegram.WebApp.initDataUnsafe;
    if (!user) {
        alert('Не удалось получить данные пользователя');
        return;
    }

    // Отправка данных заказа в Telegram бот
    const orderData = {
        user: {
            // id: user.id,
            // first_name: user.first_name,
            // last_name: user.last_name,
            // username: user.username
            id: tg.initDataUnsafe.id,
            first_name: tg.initDataUnsafe.first_name,
            last_name: tg.initDataUnsafe.last_name,
            username: tg.initDataUnsafe.username,
            test: "test"
        },
        items: cart
    };

    fetch('https://a73b-2001-8f8-1b2f-a514-60c4-e1d4-82a6-7c52.ngrok-free.app/order', {  // Измените URL на ваш HTTPS URL от ngrok
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(orderData)
    })
    .then(response => response.json())
    .then(data => {
        alert('Ваш заказ оформлен!');
        cart.length = 0;
        renderCart();
        // Закрытие WebApp после оформления заказа
        Telegram.WebApp.close();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Ошибка при оформлении заказа. Попробуйте еще раз.');
    });
}

document.getElementById('checkout-button').addEventListener('click', checkout);

// Инициализация каталога
renderCatalog();
