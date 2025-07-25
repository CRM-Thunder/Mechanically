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

Aby aktywować konto i ustawić hasło, kliknij w link i wprowadź hasło:

  https://<frontend>.com/activate/?uuid={uuid}&token={token}


Jeśli nie próbowałeś aktywować konta – zignoruj tę wiadomość.
    """.strip()

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )

def send_reset_password_email(user, token):
    uuid = str(user.pk)

    subject = "Resetowanie hasła"
    message = f"""
    Cześć {user.get_full_name()}!

    Przyjęliśmy twoją prośbę dotyczącą resetu hasła.

    Aby ustawić nowe hasło hasło, kliknij w link i wprowadź nowe hasło:

      https://<frontend>.com?/reset-password/uuid={uuid}&token={token}


    Jeśli nie próbowałeś aktywować konta – zignoruj tę wiadomość.
        """.strip()

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )