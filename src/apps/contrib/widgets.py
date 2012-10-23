#!/usr/bin/python
# -*- coding: utf-8 -*-
from django import forms


class TextInputFK(forms.TextInput):
    """
    Base Widget for .fields.CharFieldFK form field.

    See notes on .fields.CharFieldFK doc for more info.

    """
    def __init__(self, *args, **kwargs):
        self._fk_class = kwargs.pop('fk_class', None)
        self._fk_attr = kwargs.pop('fk_attr', '__unicode__')
        super(TextInputFK, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        try:
            obj = self._fk_class.objects.get(pk=value)
            value = getattr(obj, self._fk_attr, None)
            if callable(value):
                value = value()
        except:
            pass
        return super(TextInputFK, self).render(name, value, attrs)
