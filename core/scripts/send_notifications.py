from django.core.mail import send_mail

def send_notification(subject, message, recipient_email):
    send_mail(
        subject,
        message,
        'admin@example.com',
        [recipient_email],
        fail_silently=False
    )
