import os

import testinfra.utils.ansible_runner

import pytest

import re

import json

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


@pytest.mark.parametrize('container', [
    'nextcloud-app',
    'nextcloud-mariadb',
    'nextcloud-nginx',
])
def test_container_status(host, container):
    c = 'docker ps --all --quiet --format "{{.Names}}" --filter status=running'
    r = host.run(c)

    assert container in r.stdout


def test_nextcloud_status(host):
    c = ('docker exec --user www-data nextcloud-app '
         'php occ status --output=json')
    r = host.run(c)
    n = json.loads(r.stdout)

    assert n['installed']


def test_encryption_status(host):
    c = ('docker exec --user www-data nextcloud-app '
         'php occ encryption:status --output=json')
    r = host.run(c)
    e = json.loads(r.stdout)

    assert e['enabled']


def test_encryption_module_status(host):
    c = ('docker exec --user www-data nextcloud-app '
         'php occ app:list --output=json')
    r = host.run(c)
    e = json.loads(r.stdout)
    p = re.compile('\\d+\\.\\d+\\.\\d+')

    assert p.match(e['enabled']['encryption'])
