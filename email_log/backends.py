from django.core.mail import get_connection
from django.core.mail.backends.base import BaseEmailBackend

from .conf import settings
from .models import Email


class EmailBackend(BaseEmailBackend):

    """Wrapper email backend that records all emails in a database model"""

    def __init__(self, **kwargs):
        super(EmailBackend, self).__init__(**kwargs)
        self.connection = get_connection(settings.EMAIL_LOG_BACKEND, **kwargs)
        self.exclude_django_emails = settings.EXCLUDE_DJANGO_EMAILS

    def send_messages(self, email_messages):
        num_sent = 0
        if self.exclude_django_emails:
            email_messages = filter(lambda x: not x.subject.startswith('[Django]'), email_messages)
        for message in email_messages:
            recipients = '; '.join(message.to)
            email = Email.objects.create(
                from_email=message.from_email,
                recipients=recipients,
                subject=message.subject,
                body=message.body,
            )
            message.connection = self.connection
            num_sent += message.send()
            if num_sent > 0:
                email.ok = True
                email.save()
        return num_sent
