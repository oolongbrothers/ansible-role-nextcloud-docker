import os

import testinfra.utils.ansible_runner

import pytest

import re

import json

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


@pytest.mark.parametrize('string,existence', [
    ('POSTGRES_DB=nextcloud', True),
    ('POSTGRES_PASSWORD=postgres-password', True),
    ('POSTGRES_USER=nextcloud', True),
])
def test_db_env_file(host, string, existence):
    f = host.file('/tmp/nextcloud/db.env')

    assert f.exists
    assert f.is_file
    assert existence is (string in f.content_string)


@pytest.mark.parametrize('string,existence', [
    ('443', False),
    ('cert', False),
    ('letsencrypt', False),
    ('POSTGRES_HOST=db', True),
    ('REDIS_HOST=redis', True),
    ('REDIS_HOST_PASSWORD=redis-host-password', True),
    ('REDIS_HOST_PORT=6379', True),
    ('VIRTUAL_HOST=instance', True),
])
def test_docker_compose_file(host, string, existence):
    f = host.file('/tmp/nextcloud/docker-compose.yml')

    assert f.exists
    assert f.is_file
    assert existence is (string in f.content_string)


@pytest.mark.parametrize('container', [
    'nextcloud_app_1',
    'nextcloud_cron_1',
    'nextcloud_db_1',
    'nextcloud_redis_1',
    'nextcloud_proxy_1',
])
def test_container_status(host, container):
    c = 'docker ps --all --quiet --format "{{.Names}}" --filter status=running'
    r = host.run(c)

    assert container in r.stdout


@pytest.mark.parametrize('network', [
    'nextcloud_default',
    'nextcloud_proxy-tier',
])
def test_network_status(host, network):
    c = 'docker network ls --quiet --format "{{.Name}}"'
    r = host.run(c)

    assert network in r.stdout


@pytest.mark.parametrize('volume', [
    'nextcloud_db',
    'nextcloud_html',
    'nextcloud_nextcloud',
    'nextcloud_vhost.d',
])
def test_volume_status(host, volume):
    c = 'docker volume ls --quiet'
    r = host.run(c)

    assert volume in r.stdout


@pytest.mark.parametrize('nextcloud_directory', [
    'config',
    'custom_apps',
    'data',
    'themes',
])
def test_nextcloud_volume_directory(host, nextcloud_directory):
    c = 'ls -hal /var/nextcloud'
    r = host.run(c)

    assert nextcloud_directory in r.stdout


@pytest.mark.parametrize('trusted_domain', [
  'localhost',
  'instance',
])
def test_trusted_domains(host, trusted_domain):
    c = ('docker exec --user www-data nextcloud_app_1 php occ '
         'config:system:get trusted_domains')
    r = host.run(c)

    assert trusted_domain in r.stdout


@pytest.mark.parametrize('config_line', [
  '\'dbtype\' => \'pgsql\','
])
def test_nextcloud_configuration(host, config_line):
    c = 'cat /var/nextcloud/config/config.php'
    r = host.run(c)

    assert config_line in r.stdout


def test_nextcloud_status(host):
    c = ('docker exec --user www-data nextcloud_app_1 '
         'php occ status --output=json')
    r = host.run(c)
    n = json.loads(r.stdout)

    assert n['installed']


def test_encryption_status(host):
    c = ('docker exec --user www-data nextcloud_app_1 '
         'php occ encryption:status --output=json')
    r = host.run(c)
    e = json.loads(r.stdout)

    assert e['enabled']


def test_encryption_module_status(host):
    c = ('docker exec --user www-data nextcloud_app_1 '
         'php occ app:list --output=json')
    r = host.run(c)
    e = json.loads(r.stdout)
    p = re.compile('\\d+\\.\\d+\\.\\d+')

    assert p.match(e['enabled']['encryption'])


def test_crontab_task(host):
    c = 'docker exec nextcloud_cron_1 crontab -l'
    c = ('docker exec --user www-data nextcloud_cron_1 '
         'busybox cat /var/spool/cron/crontabs/www-data')
    r = host.run(c)

    assert 'php -f /var/www/html/cron.php' in r.stdout


@pytest.mark.parametrize('property,result', [
    ('redis', 'host: redis'),
    ('memcache.distributed', '\\OC\\Memcache\\Redis'),
])
def test_nextcloud_redis_config(host, property, result):
    c = ('docker exec --user www-data nextcloud_app_1 '
         'php occ config:system:get {}'.format(property))
    r = host.run(c)

    assert result in r.stdout
