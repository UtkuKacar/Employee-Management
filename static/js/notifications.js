// WebSocket bağlantısı başlat
const notificationSocket = new WebSocket('ws://' + window.location.host + '/ws/notifications/');

// Mesaj alındığında çağrılır
notificationSocket.onmessage = function (event) {
    const data = JSON.parse(event.data);
    const notificationList = document.getElementById('notification-list');
    const newNotification = document.createElement('li');
    newNotification.textContent = data.message;
    notificationList.appendChild(newNotification);
};

// WebSocket bağlantısı kapandığında çağrılır
notificationSocket.onclose = function (event) {
    console.error('WebSocket bağlantısı kapandı.');
};

// WebSocket hata durumunda
notificationSocket.onerror = function (error) {
    console.error('WebSocket Hatası:', error);
};
