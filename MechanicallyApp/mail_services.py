from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
#w mailu jest odnośnik do nieistniejącego frontendu, z poziomu którego wychodziłby request POST do API
def send_activation_email(user):
    uuid = str(user.pk)
    token = default_token_generator.make_token(user)

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
