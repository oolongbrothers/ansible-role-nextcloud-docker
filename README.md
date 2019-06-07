# Ansible Role Nextcloud Docker

[![Build Status](https://travis-ci.com/ctorgalson/ansible-role-nextcloud-docker.svg?branch=master)](https://travis-ci.com/ctorgalson/ansible-role-nextcloud-docker)

This role builds a Nexcloud instance on Ubuntu 16.04 using Docker containers.

The role (which should probably work on other Linux distros and releases) is based on [this helpfule blog post at blog.ssdnodes.com](https://blog.ssdnodes.com/blog/installing-nextcloud-docker/). 

## Requirements

This role uses [`docker_container_info` tasks](https://docs.ansible.com/ansible/latest/modules/docker_container_info_module.html#docker-container-info-module), and so requires [Ansible 2.8](https://docs.ansible.com/ansible/2.8/) or later.

## Role Variables

### nextcloud_config vars

These variables are used to configure the Nextcloud application itself. Some of them--such as e.g. the database variables--are also used in constructing the containers.

    nextcloud_config_domain: "example.local"

The principal domain that the Nextcloud instance will be accessed at.

    nextcloud_config_db_root_password: "root"

The mariadb root password. This is an insecure default.

    nextcloud_config_db_database: "mysql"

The type of database engine to be used. This role is currently untested with othe db engines supported by Nextcloud.

    nextcloud_config_db_database_name: "nextcloud"

The name of the Nextcloud database.

    nextcloud_config_db_database_user: "nextcloud"

The name of the database user for the Nextcloud database.

    nextcloud_config_db_database_password: "mysql"

The Nextcloud database password. This is an insecure default.

    nextcloud_config_trusted_domains:
      - "localhost"
      - "{{ nextcloud_config_domain }}"

The list of trusted domains from which Nextcloud can be accessed.

    nextcloud_config_admin_user: "admin"

The Nextcloud admin user name.

    nextcloud_config_admin_password: "pass"

The nextcloud admin user password. This is an insecure default.

    nextcloud_encryption_module: "encryption"

The encryption module to use in Nextcloud.

### nextcloud_app_container vars

These variables are used to configure the container that runs the Nextcloud application itself. Many of them map directly to the [`docker_container` task](https://docs.ansible.com/ansible/latest/modules/docker_container_module.html#docker-container-module) used to create the container.

    nextcloud_app_container_env:
      - key: "VIRTUAL_HOST"
        value: "{{ nextcloud_config_domain }}"

The list of environment vars for the Nextcloud App container.

    nextcloud_app_container_image: "nextcloud:latest"

The specific Nextcloud container image to use.

    nextcloud_app_container_name: "nextcloud-app"

The name for the running nextcloud container.

    nextcloud_app_container_restart: true

[`docker_container` module](https://docs.ansible.com/ansible/latest/modules/docker_container_module.html#docker-container-module) `restart` setting for this container.

    nextcloud_app_container_state: started

[`docker_container` module](https://docs.ansible.com/ansible/latest/modules/docker_container_module.html#docker-container-module) `started` setting for this container.

    nextcloud_app_container_volumes:
      - "nextcloud:/var/www/html"
      - "./app/config:/var/www/html/config"
      - "./app/custom_apps:/var/www/html/custom_apps"
      - "./app/data:/var/www/html/data"
      - "./app/themes:/var/www/html/themes"
      - "/etc/localtime:/etc/localtime:ro"

Volumes for Nextcloud app container.

### nextcloud_mariadb_container vars

These variables are used to configure the container that runs mariadb. Many of them map directly to the [`docker_container` task](https://docs.ansible.com/ansible/latest/modules/docker_container_module.html#docker-container-module) used to create the container.

    nextcloud_mariadb_container_image: "mariadb"

The specific mariadb container image to use.

    nextcloud_mariadb_container_name: "nextcloud-mariadb"

The name for the running mariadb container.

    nextcloud_mariadb_container_restart: true

[`docker_container` module](https://docs.ansible.com/ansible/latest/modules/docker_container_module.html#docker-container-module) `restart` setting for this container.

    nextcloud_mariadb_container_state: started

[`docker_cyyontainer` module](https://docs.ansible.com/ansible/latest/modules/docker_container_module.html#docker-container-module) `started` setting for this container.

    nextcloud_mariadb_container_volumes:
      - "db:/var/lib/mysql"
      - "/etc/localtime:/etc/localtime:ro"

Volumes for mariadb app container.

    nextcloud_mariadb_container_env:
      - key: "MYSQL_ROOT_PASSWORD"
        value: "{{ nextcloud_config_db_root_password }}"
      - key: "MYSQL_PASSWORD"
        value: "{{ nextcloud_config_db_database_password }}"
      - key: "MYSQL_DATABASE"
        value: "{{ nextcloud_config_db_database_name }}"
      - key: "MYSQL_USER"
        value: "{{ nextcloud_config_db_database_user }}"
      - key: "MYSQL_HOST"
        value: "{{ nextcloud_mariadb_container_name }}"

Volumes for mariadb app container.

### nextcloud_nginx_container vars

These variables are used to configure the container that runs nginx-proxy. Many of them map directly to the [`docker_container` task](https://docs.ansible.com/ansible/latest/modules/docker_container_module.html#docker-container-module) used to create the container.

    nextcloud_nginx_container_image: "jwilder/nginx-proxy:alpine"

The specific nginx-proxy container image to use.

    nextcloud_nginx_container_name: "nextcloud-nginx"

The name for the running nginx-proxy container.

    nextcloud_nginx_container_ports:
      - "80:80"
      - "443:443"

The list of ports for the nginx-proxy container to listen on.

    nextcloud_nginx_container_restart: true

[`docker_container` module](https://docs.ansible.com/ansible/latest/modules/docker_container_module.html#docker-container-module) `restart` setting for this container.

    nextcloud_nginx_container_state: started

[`docker_container` module](https://docs.ansible.com/ansible/latest/modules/docker_container_module.html#docker-container-module) `restart` setting for this container.

    nextcloud_nginx_container_volumes:
      - "./proxy/conf.d:/etc/nginx/conf.d:rw"
      - "./proxy/vhost.d:/etc/nginx/vhost.d:rw"
      - "./proxy/html:/usr/share/nginx/html:rw"
      - "./proxy/certs:/etc/nginx/certs:ro"
      - "/etc/localtime:/etc/localtime:ro"
      - "/var/run/docker.sock:/tmp/docker.sock:ro"

Volumes for nginx-proxy container.

### nextcloud_network vars.

These variables are used to configure the Docker network used in the Nextcloud setup. They are used to configure the [`docker_network` task](https://docs.ansible.com/ansible/latest/modules/docker_network_module.html#docker-network-module) used to create the network.

    nextcloud_network_name: "nextcloud_network"

The name for the running Docker network that containers use for communication.

    nextcloud_network_connected:
      - "{{ nextcloud_app_container_name }}"
      - "{{ nextcloud_mariadb_container_name }}"
      - "{{ nextcloud_nginx_container_name }}"

The list of containers that must be connected to the Docker newtork.

### Nextcloud volume vars.

This variable is used to create the persistent Docker volumes used in the Nextcloud setup. It is passed directly to the [`docker_volume` task](https://docs.ansible.com/ansible/latest/modules/docker_volume_module.html#docker-volume-module) used to create those volumes.

    nextcloud_volumes:
      - "nextcloud"
      - "mariadb"

The list of nextcloud volumes to create. If created, these are used by the `nextcloud-app` and `nextcloud-mariadb` containers (above). If not created, it's necessary to provide a path in place of the volume name to the `nextcloud_app_container_volumes` or `nextcloud_mariadb_container_volumes` variable(s).

### Nextcloud cli install vars

These variables are used to configure the command that's used to complete the Nextcloud install on the role's initial run.

    nextcloud_occ_prefix: "docker exec --user www-data {{ nextcloud_app_container_name }}"

The prefix used to specify the Docker container to run `occ` commands on, and also the user to run the commands as.

    nextcloud_occ_install: >
      php occ maintenance:install
      --database="{{ nextcloud_config_db_database }}"
      --database-name="{{ nextcloud_config_db_database_name }}"
      --database-user="{{ nextcloud_config_db_database_user }}"
      --database-pass="{{ nextcloud_config_db_database_password }}"
      --database-host="{{ nextcloud_mariadb_container_name }}"
      --admin-user="{{ nextcloud_config_admin_user }}"
      --admin-pass="{{ nextcloud_config_admin_password }}"

The actual command used to install the Nextcloud instance.

## Example Playbook

Including an example of how to use your role (for instance, with variables
passed in as parameters) is always nice for users too:

    - hosts: servers
      roles:
         - { role: ansible-role-nextcloud-docker, x: 42 }

## License

GPLv2
