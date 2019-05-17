import pytest
import trafaret as t

from routes.schedules.validators import mwoffliner_flags_validator, config_validator


def make_mwoffliner_flags(**kwargs):
    flags = {
        'mwUrl': 'https://www.wikipedia.org',
        'adminEmail': 'contact@kiwix.org',
        'format': ['nopic', 'novid'],
        'useCache': True,
        'verbose': False,
        'speed': 1.0,
        'articleList': 'https://example.com',
        'customZimFavicon': 'https://example.com/icon.jpeg',
        'customZimTitle': 'Custom Title',
        'customZimDescription': 'Custom Description',
    }
    flags.update(kwargs)
    return flags


def make_config(**kwargs):
    config = {
        'task_name': 'offliner.mwoffliner',
        'queue': 'small',
        'warehouse_path': '/wikipedia',
        'image': {
            'name': 'openzim/mwoffliner',
            'tag': '1.8.0'
        },
        'flags': make_mwoffliner_flags()
    }
    config.update(kwargs)
    return config


class TestMWOfflinerFlagsValidator:
    def test_valid(self):
        flags = {'mwUrl': 'https://www.wikipedia.org', 'adminEmail': 'contact@kiwix.org'}
        mwoffliner_flags_validator.check(flags)

        flags = {'mwUrl': 'https://www.wikipedia.org',
                 'adminEmail': 'contact@kiwix.org',
                 'format': ['nopic', 'novid'],
                 'useCache': True,
                 'verbose': False,
                 'speed': 1.0}
        mwoffliner_flags_validator.check(flags)

        flags = make_mwoffliner_flags()
        mwoffliner_flags_validator.check(flags)

    @pytest.mark.parametrize('missing_key', ['mwUrl', 'adminEmail'])
    def test_missing_required(self, missing_key):
        with pytest.raises(t.DataError):
            flags = make_mwoffliner_flags()
            flags.pop(missing_key)
            mwoffliner_flags_validator.check(flags)

    def test_extra_key(self):
        with pytest.raises(t.DataError):
            flags = make_mwoffliner_flags()
            flags['extra'] = 'some_value'
            mwoffliner_flags_validator.check(flags)

    @pytest.mark.parametrize('data', [
        {'mwUrl': 'http:/example.com'}, {'adminEmail': 'user @example.com'},
        {'format': ['pic', 123]}, {'useCache': 'False'}, {'verbose': 'False'}, {'speed': 'zero'},
        {'articleList': 'abc'}, {'customZimFavicon': '123'},
        {'customZimTitle': 123}, {'customZimDescription': None},
    ])
    def test_invalid_field(self, data):
        with pytest.raises(t.DataError):
            flags = make_mwoffliner_flags(**data)
            mwoffliner_flags_validator.check(flags)

    @pytest.mark.parametrize('format, expected', [
        (['nopic', 'nopic'], ['nopic']),
        (['novid', 'novid', 'novid', 'nopic'], ['novid', 'nopic'])
    ])
    def test_duplicated_formats(self, format, expected):
        flags = make_mwoffliner_flags(format=format)
        result = mwoffliner_flags_validator.check(flags)
        assert set(result['format']) == set(expected)


class TestConfigValidator:
    def test_valid(self):
        config = make_config()
        config_validator.check(config)

    @pytest.mark.parametrize('missing_key', ['task_name', 'queue', 'warehouse_path', 'image', 'flags'])
    def test_missing_required(self, missing_key):
        with pytest.raises(t.DataError):
            config = make_config()
            config.pop(missing_key)
            config_validator.check(config)

    def test_extra_key(self):
        with pytest.raises(t.DataError):
            config = make_config()
            config['extra'] = 'some_value'
            config_validator.check(config)

    @pytest.mark.parametrize('data', [
        {'task_name': 'offliner.unknown'}, {'queue': 'minuscule'},
        {'warehouse_path': '/wikipedia/subdir'}, {'warehouse_path': '/bad_path'},
        {'image': {'name': 'unknown_offliner', 'tag': '1.0'}}, {'image': {'name': 'unknown_offliner'}},
        {'flags': make_mwoffliner_flags(mwUrl='bad_url')}
    ])
    def test_invalid_field(self, data):
        with pytest.raises(t.DataError):
            flags = make_mwoffliner_flags(**data)
            mwoffliner_flags_validator.check(flags)