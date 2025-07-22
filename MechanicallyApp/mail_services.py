from django.core.mail import send_mail
from django.conf import settings
#w mailu jest odnośnik do nieistniejącego frontendu, z poziomu którego wychodziłby request POST do API
def send_activation_email(user, token):
    uuid = str(user.pk)

    subject = "Aktywacja konta i ustawienie hasła"
    message = f"""
Cześć {user.get_full_name()}!

Twoje konto zostało utworzone przez administratora.

Twoja nazwa użytkownika to: {user.username}

Aby aktywować konto i ustawić hasło, wyślij POST na:

  https://<frontend>.com?uuid={uuid}&token={token}


Jeśli nie próbowałeś aktywować konta – zignoruj tę wiadomość.
    """.strip()

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )
