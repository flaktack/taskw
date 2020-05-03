import codecs
import logging
import os

from taskw.fields import (
    ChoiceField,
    DateField,
    DurationField,
    NumericField,
    StringField
)


logger = logging.getLogger(__name__)


def sanitize(line):
    comment_position = line.find('#')
    if comment_position < 0:
        return line.strip()
    return line[:comment_position].strip()


class TaskRc(dict):
    """ Access the user's taskRC using a dictionary-like interface.

        Sub-keys are stored with a `.` postfix.
    """

    UDA_TYPE_MAP = {
        'date': DateField,
        'duration': DurationField,
        'numeric': NumericField,
        'string': StringField,
    }

    def __init__(self, stream=None, overrides=None):
        self.overrides = overrides if overrides else {}
        if stream:
            config = self._read(stream)
        else:
            self.path = None
            config = {}
        super(TaskRc, self).__init__(config)

    def _add_to_tree(self, config, key, value):
        key_parts = key.split('.')
        cursor = config
        for part in key_parts[0:-1]:
            key = part + '.'
            if key not in cursor:
                cursor[key] = {}
            cursor = cursor[key]
        cursor[key_parts[-1]] = value
        return config

    def _read(self, config_file):
        config = {}
        for raw_line in config_file.readlines():
            line = sanitize(raw_line)
            if not line:
                continue
            else:
                try:
                    left, right = line.split('=', maxsplit=1)
                    key = left.strip()
                    value = right.strip()
                    config = self._add_to_tree(config, key, value)
                except ValueError:
                    logger.exception(
                        "Error encountered while processing configuration "
                        "setting '%s' (from TaskRc file at '%s')",
                        line,
                        self.path,
                    )

        return config

    def __delitem__(self, *args):
        raise TypeError('TaskRc objects are immutable')

    def __setitem__(self, item, value):
        raise TypeError('TaskRc objects are immutable')

    def update(self, value):
        raise TypeError('TaskRc objects are immutable')

    def get_udas(self):
        raw_udas = self.get('uda.', {})
        udas = {}

        for k, v in raw_udas.items():
            name = k.rstrip('.')
            tw_type = v.get('type', '')
            label = v.get('label', None)
            choices = v.get('values', None)

            kwargs = {}
            cls = self.UDA_TYPE_MAP.get(tw_type, StringField)
            if choices:
                cls = ChoiceField
                kwargs['choices'] = choices.split(',')
            if label:
                kwargs['label'] = label

            udas[name] = cls(**kwargs)

        return udas

    def __unicode__(self):
        return 'TaskRc file at {path}'.format(
            path=self.path
        )

    def __str__(self):
        return self.__unicode__().encode('utf-8', 'REPLACE')
