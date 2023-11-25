from django.utils.translation import gettext_lazy as _

def password_validator(password_1, password_2):
    errors = []
    special_syms = '~!@#$%^&*()_-+={[}]:;<,>.?'

    if any((
        char not in special_syms) and
        not (char >= 'a' and char <= 'z') and
        not (char >= 'A' and char <= 'Z') and 
        not (char >= '0' and char <= '9') for char in password_1
    ):
        errors.append(_('password_only_contains_these_characters'))
    

    if len(password_1) < 8:
        errors.append(_('password_at_lest_eight_chars'))

    if len(password_1) > 50:
        errors.append(_('password_not_more_than_50_chars'))

    if not any(char.isdigit() for char in password_1):
        errors.append(_('password_at_lest_one_digit'))

    if not any(char.isupper() for char in password_1):
        errors.append(_('password_at_lest_one_uppercase'))
         
    if not any(char.islower() for char in password_1):
        errors.append(_('password_at_lest_one_lowercase'))
         
    if not any(char in special_syms for char in password_1):
        errors.append(_('password_at_lest_one_special'))

    if password_1 != password_2:
        errors.append(_('passwords_do_not_match'))

    return errors