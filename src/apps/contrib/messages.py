# -*- coding: utf-8 -*-


def get_form_error_msgs(form):
    """
    Given a form, capture and return all field errors

    """
    errors = [u"Corrija os campos abaixo:"]
    nerrors = 0
    for field in form:
        for error in field.errors:
            error_string = field.label + ": " + error
            errors.append(error_string)
            nerrors = nerrors + 1
    if nerrors == 0:
        errors = []

    errors.extend(form.non_field_errors())
    return errors
