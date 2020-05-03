import codecs
import os
import sys

from taskw.warrior import TaskWarrior
from taskw.taskrc import TaskRc
from taskw.fields import NumericField, ChoiceField


if sys.version_info >= (2, 7):
    from unittest import TestCase
else:
    from unittest2 import TestCase


class TestBasicLoading(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.path_to_taskrc = os.path.join(
            os.path.dirname(__file__),
            'data/default.taskrc',
        )

    def test_load_config(self):
        expected = {
            'data.': {
                'location': '~/.task'
            },
            'alpha': '12',
            'alpha.': {
                'one': 'yes',
                'two': '2',
            },
            'beta.': {
                'one': 'FALSE',
            },
            'gamma.': {
                'one': 'TRUE',
            },
            'omega.': {
                'one': 'X=X=X='
            },
            'uda.': {
                'a.': {
                    'type': 'numeric',
                    'label': 'Alpha',
                },
                'b.': {
                    'type': 'string',
                    'label': 'Beta',
                    'values': 'Strontium-90,Hydrogen-3',
                },
                'priority.': {
                    'label': 'Priority',
                    'type': 'string',
                    'values': 'H,M,L,'
                }
            }
        }

        config = TaskWarrior(self.path_to_taskrc).config
        subset = {k: v for k, v in config.items() if k in expected}
        self.assertEqual(subset, expected)


class TestTaskRc(TestCase):
    def setUp(self):
        self.path_to_taskrc = os.path.join(
            os.path.dirname(__file__),
            'data/default.taskrc',
        )
        with codecs.open(self.path_to_taskrc, 'r', 'utf8') as config_file:
            self.taskrc = TaskRc(config_file)

    def test_taskrc_parsing(self):
        expected_config = {
            'data.': {
                'location': '~/.task'
            },
            'alpha': '12',
            'alpha.': {
                'one': 'yes',
                'two': '2',
            },
            'beta.': {
                'one': 'FALSE',
            },
            'gamma.': {
                'one': 'TRUE',
            },
            'omega.': {
                'one': 'X=X=X='
            },
            'uda.': {
                'a.': {
                    'type': 'numeric',
                    'label': 'Alpha',
                },
                'b.': {
                    'type': 'string',
                    'label': 'Beta',
                    'values': 'Strontium-90,Hydrogen-3',
                }
            }
        }

        self.assertEqual(self.taskrc, expected_config)

    def test_get_udas(self):
        expected_udas = {
            'a': NumericField(label='Alpha'),
            'b': ChoiceField(
                label='Beta',
                choices=['Strontium-90', 'Hydrogen-3'],
            ),
        }
        actual_udas = self.taskrc.get_udas()

        self.assertEqual(actual_udas, expected_udas)
