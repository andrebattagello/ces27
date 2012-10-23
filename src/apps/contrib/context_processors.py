"""
Context processors are meant to be added
into the settings.TEMPLATE_CONTEXT_PROCESSORS tuple
"""
# -*- coding: utf-8 -*-
from django.conf import settings


def facebook(request):
    """
    Defines additional context variables
    available to use in any template across the project

    """
    context_extras = {}
    context_extras['FB_APP_NS'] = settings.PROJECT_NAME
    context_extras['FB_APP_ID'] = settings.FACEBOOK_APP_ID
    return context_extras
