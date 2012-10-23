#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Super general email sender

"""
from django.template.loader import render_to_string
from django.conf import settings


def send_email(recipients_list, subject, template_name,
               ctx_dict=None, initial_lines=None, final_lines=None):
    """
    Sends email to all the emails in recipients_list
    Prepend initial_lines at the beginning of the message
    Append final_lines at the end of the message

    """
    if not ctx_dict:
        ctx_dict = {}
    message = render_to_string(template_name, ctx_dict)

    #prepend and append special important lines
    if initial_lines:
        extra = '\n'.join(initial_lines)
        message = extra + '\n' + message
    if final_lines:
        extra = '\n'.join(final_lines)
        message = message + '\n' + extra

    #try to use django-mailer, if available
    if "mailer" in settings.INSTALLED_APPS:
        from mailer import send_mail
    else:
        from django.core.mail import send_mail

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipients_list)
