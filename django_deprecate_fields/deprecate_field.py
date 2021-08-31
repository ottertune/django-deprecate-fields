import logging
import sys
import warnings

logger = logging.getLogger(__file__)

def __deprecate_warn_get_name(self, obj):
    """
    Try to find this field's name in the model class
    """
    for k, v in type(obj).__dict__.items():
        if v is self:
            return k
    return "<unknown>"

def __deprecate_warn_and_return_substitute__get__(self, obj, type=None):
    msg = "accessing deprecated field %s.%s" % (
        obj.__class__.__name__,
        self._get_name(obj),
    )
    warnings.warn(msg, DeprecationWarning, stacklevel=2)
    logger.warning(msg)
    if not callable(self.__patched_return_value):
        return self.__patched_return_value
    return self.__patched_return_value()

def __deprecate_warn__set__(self, obj, val):
    msg = "writing to deprecated field %s.%s" % (
        obj.__class__.__name__,
        self._get_name(obj),
    )
    warnings.warn(msg, DeprecationWarning, stacklevel=2)
    logger.warning(msg)
    self.__original_set(val)
    
def monkey_patch_deprecated_methods(field_instance, return_replacement):
    field_instance.__patched_return_value = return_replacement
    field_instance._get_name = __deprecate_warn_get_name
    field_instance.__get__ = __deprecate_warn_and_return_substitute__get__
    field_instance.__original_set = field.instance.__set__
    field_instance.__set__ = __deprecate_warn__set__
    return field_instance

def deprecate_field(field_instance, return_instead=None):
    """
    Can be used in models to delete a Field in a Backwards compatible manner.
    The process for deleting old model Fields is:
    1. Mark a field as deprecated by wrapping the field with this function
    2. Wait until (1) is deployed to every relevant server/branch
    3. Delete the field from the model.

    For (1) and (3) you need to run ./manage.py makemigrations:
    :param field_instance: The field to deprecate
    :param return_instead: A value or function that
    the field will pretend to have
    """
    field_instance.null = True
    if not set(sys.argv) & {"makemigrations", "migrate", "showmigrations"}:
        monkey_patch_deprecated_methods(field_instance)

    return field_instance
