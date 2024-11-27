import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ManagerNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Kullanıcıyı WebSocket grubuna ekle (kişisel bildirim grubu)
        self.user = self.scope['user']  # Kullanıcıyı scope'tan alıyoruz
        self.group_name = f"user_{self.user.id}"  # Kullanıcıya özel grup adı

        # Eğer yönetici ise, tüm yöneticiler için grup oluştur
        if self.user.is_manager:
            await self.channel_layer.group_add("managers", self.channel_name)
        else:
            # Personel ise, kişisel grup adı oluşturulur
            await self.channel_layer.group_add(
                self.group_name,  # Kişisel grup adı
                self.channel_name
            )

        await self.accept()

    async def disconnect(self, close_code):
        # Bağlantı kesildiğinde kullanıcıyı gruptan çıkar
        if self.user.is_manager:
            await self.channel_layer.group_discard("managers", self.channel_name)
        else:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # Bildirim gönderme işlemi
    async def send_notification(self, event):
        message = event['message']  # Mesajı event'ten alıyoruz
        await self.send(text_data=json.dumps({
            'message': message
        }))
