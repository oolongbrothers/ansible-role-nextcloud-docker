#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves.urllib.parse import urlparse
import subprocess
import json
__metaclass__ = type


def set_config(module, binary, key, value_string, value_array):
    """Set a configuration."""
    global result
    if module._diff:
        result['diff'] = dict()
        result['diff']['before'] = dict()
        if does_config_exist(module, binary, key):
            result['diff']['before'][key] = get_config_value(
                module, binary, key)

    if value_string:
        command = "{0} config:system:set {1} --value={2}".format(
            binary, key, value_string)
        _occ_command(module, module.check_mode, command)
    elif value_array:
        delete_config(module, binary, key)
        for index, item in enumerate(value_array):
            command = "{0} config:system:set {1} {2} --value={3}".format(
                binary, key, index, item)
            _occ_command(module, module.check_mode, command)
    result['changed'] = True
    if module._diff:
        result['diff']['after'] = dict()
        result['diff']['after'][key] = value_string if value_string else value_array


def delete_config(module, binary, key):
    """Remove an existing configuration key."""
    global result
    command = "{0} config:system:delete {1}".format(binary, key)
    _occ_command(module, module.check_mode, command)
    result['changed'] = True


def is_config_correct(module, binary, key, value_string, value_array):
    """Check if the config is as expected."""
    if not does_config_exist(module, binary, key):
        return False
    actual_value = get_config_value(module, binary, key)
    comparative_value = value_string if value_string else value_array
    if actual_value == comparative_value:
        return True
    return False


def get_config_value(module, binary, key):
    """Get the value for a configuration key."""
    command = "{0} config:system:get {1} --output=json".format(binary, key)
    output, _ = _occ_command(module, False, command)
    actual_value = json.loads(output)
    return actual_value


def does_config_exist(module, binary, key):
    """Check if the config is as expected."""
    command = "{0} config:system:get {1} --output=json".format(binary, key)
    _, rc = _occ_command(module, False, command, ignore_failure=True)
    if rc == 0:
        return True
    return False


def _occ_command(module, noop, command, ignore_failure=False):
    global result
    if noop:
        result['rc'] = 0
        result['command'] = command
        return ""

    process = subprocess.Popen(
        command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_data, stderr_data = process.communicate()
    result['rc'] = process.returncode
    result['command'] = command
    result['stdout'] = to_native(stdout_data)
    result['stderr'] = to_native(stderr_data)
    if result['rc'] != 0 and not ignore_failure:
        module.fail_json(msg="Failed to execute occ command", **result)
    return to_native(stdout_data), result['rc']


def main():
    # This module supports check mode
    module = AnsibleModule(
        argument_spec=dict(
            key=dict(type='str', required=True),
            value_string=dict(type='str', default=None),
            value_array=dict(type='list', default=None),
            state=dict(type='str', default='present',
                       choices=['absent', 'present']),
            executable=dict(type='path', default='php occ')
        ),
        supports_check_mode=True,
    )

    key = module.params['key']
    value_string = module.params['value_string']
    value_array = module.params['value_array']
    state = module.params['state']
    executable = module.params['executable']
    binary = module.get_bin_path(executable.split()[0], None)

    global result
    result = dict(
        changed=False
    )

    # If the binary was not found, fail the operation
    if not binary:
        module.fail_json(
            msg="Executable '%s' was not found on the system." % executable, **result)
    if value_string and value_array:
        module.fail_json(
            msg="You can only set one of value_string and value_array, not both.", **result)

    if state == 'present' and not is_config_correct(module, executable, key, value_string, value_array):
        set_config(module, executable, key, value_string, value_array)
    elif state == 'absent' and does_config_exist(module, executable, key):
        delete_config(module, executable, key)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
