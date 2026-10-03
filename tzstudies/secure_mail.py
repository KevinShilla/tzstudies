"""Flask-Mail connection with certificate-verified TLS and bounded timeouts."""
import smtplib
import ssl

from flask import current_app
from flask_mail import Connection, Mail


class SecureConnection(Connection):
    def configure_host(self):
        context = ssl.create_default_context()
        if self.mail.use_ssl:
            host = smtplib.SMTP_SSL(self.mail.server, self.mail.port, timeout=15, context=context)
        elif self.mail.use_tls:
            host = smtplib.SMTP(self.mail.server, self.mail.port, timeout=15)
            try:
                host.ehlo()
                host.starttls(context=context)
                host.ehlo()
            except Exception:
                host.close()
                raise
        else:
            raise RuntimeError("Email delivery requires TLS.")
        try:
            if self.mail.username and self.mail.password:
                host.login(self.mail.username, self.mail.password)
        except Exception:
            host.close()
            raise
        return host


class SecureMail(Mail):
    def connect(self):
        app = getattr(self, "app", None) or current_app
        return SecureConnection(app.extensions["mail"])
