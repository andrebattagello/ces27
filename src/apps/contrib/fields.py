#!/usr/bin/python
# -*- coding: utf-8 -*-
from .widgets import TextInputFK
from django import forms


class CharFieldFK(forms.CharField):
    """

    The default field for a FK inside of a form is a choice field.

    This field allows a text input field to be used.
    This could be specially useful in autocomplete text fields.

    Note that a simple change on form declaration to use the
    django.forms.TextInput() field is not suficient.
    Django is gonna display only the FK object id
    in the form field input rendering

    This field allows the form to display any named attribute from the FK obj.
    The attribute to be displayed is specified in the *fk_attr* optional arg.
    It defaults to a simple call to '__unicode__()' if nothing is provided.

    The FK model to be used is given in the optional arg *fk_class*.
    If nothing provided, this field works just like
    a plain django.forms.CharField form field with a
    django.forms.TextInput field widget.

    """
    def __init__(self, *args, **kwargs):
        self._fk_class = kwargs.pop('fk_class', None)
        self._fk_attr = kwargs.pop('fk_attr', '__unicode__')
        self._clean_function = kwargs.pop('clean_function', None)
        kwargs['widget'] = TextInputFK(fk_attr=self._fk_attr,
                                       fk_class=self._fk_class)
        super(CharFieldFK, self).__init__(*args, **kwargs)

    def clean(self, value):
        value = super(CharFieldFK, self).clean(value)
        if self._clean_function:
            value = self._clean_function(value)
        return value
