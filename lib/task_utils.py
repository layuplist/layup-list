import socket
import traceback
from functools import wraps

from django.conf import settings
from django.core.mail import send_mail

from lib import constants


def email_if_fails(fn):
    @wraps(fn)
    def decorated(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except:
            if not settings.DEBUG:
                try:
                    fnName = fn.func_name
                except AttributeError:
                    fnName = fn.__name__
                send_error_email(
                    fnName, args, kwargs, socket.gethostname(),
                    traceback.format_exc())
            raise
    return decorated


def send_error_email(fnName, args, kwargs, host, formatted_exc):
    formatted_exc = formatted_exc.strip()
    contents = (
        "Task: {fnName}\nArgs: {args}\nKwargs: {kwargs}\nHost: {host}\n"
        "Error: {error}".format(
            fnName=fnName,
            args=args,
            kwargs=kwargs,
            host=host,
            error=formatted_exc,
        ))
    short_exc = formatted_exc.rsplit('\n')[-1]
    subject = '[celery-error] {host} {fnName} {short_exc}'.format(
        host=host,
        fnName=fnName,
        short_exc=short_exc,
    )
    send_mail(
        subject,
        contents,
        constants.SUPPORT_EMAIL,
        [email for _, email in settings.ADMINS],
        fail_silently=False,
    )
