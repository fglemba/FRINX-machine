from __future__ import print_function

import requests
import json
from string import Template
from frinx_rest import odl_url_base, odl_headers, odl_credentials, parse_response

odl_url_unified_oper_shallow = odl_url_base + "/operational/network-topology:network-topology/topology/unified?depth=3"
odl_url_unified_oper = odl_url_base + "/operational/network-topology:network-topology/topology/unified"
odl_url_unified_mount = odl_url_base + "/config/network-topology:network-topology/topology/unified/node/"


def execute_read_unified_topology_operational(task):
    response_code, response_json = read_all_devices(odl_url_unified_oper)

    if response_code == requests.codes.ok:
        return {'status': 'COMPLETED', 'output': {'url': odl_url_unified_oper,
                                                  'response_code': response_code,
                                                  'response_body': response_json},
                'logs': []}
    else:
        return {'status': 'FAILED', 'output': {'url': odl_url_unified_oper,
                                               'response_code': response_code,
                                               'response_body': response_json},
                'logs': []}


def read_all_devices(url):
    r = requests.get(url, headers=odl_headers, auth=odl_credentials, verify=False)
    response_code, response_json = parse_response(r)

    actual_nodes = response_json['topology'][0]['node']
    filtered_nodes = []

    for node in actual_nodes:
        if node['unified-topology:connection-status'] == "connected":
            filtered_nodes.append(node)

    response_json['topology'][0].pop('node')
    response_json['topology'][0].update({'node': filtered_nodes})

    return response_code, response_json


task_body_template = {
    "name": "sub_task",
    "taskReferenceName": "",
    "type": "SUB_WORKFLOW",
    "subWorkflowParam": {
        "name": "",
        "version": 1
    }
}


def get_all_devices_as_tasks(task):
    subworkflow = task['inputData']['task']
    add_params = task['inputData']['task_params']
    add_params = json.loads(add_params) if isinstance(add_params, basestring) else (add_params if add_params else {})

    response_code, response_json = read_all_devices(odl_url_unified_oper_shallow)

    if response_code == requests.codes.ok:
        print(response_json)
        ids = map(lambda x: x["node-id"], response_json["topology"][0]["node"])
        print(ids)

        dynamic_tasks_i = {}
        for device_id in ids:
            per_device_params = dict(add_params)
            per_device_params.update({"id": device_id})
            dynamic_tasks_i.update({device_id: per_device_params})

        dynamic_tasks = []
        for device_id in ids:
            task_body = task_body_template.copy()
            task_body["taskReferenceName"] = device_id
            task_body["subWorkflowParam"]["name"] = subworkflow
            dynamic_tasks.append(task_body)

        return {'status': 'COMPLETED', 'output': {'url': odl_url_unified_oper_shallow,
                                                  'dynamic_tasks_i': dynamic_tasks_i,
                                                  'dynamic_tasks': dynamic_tasks},
                'logs': []}
    else:
        return {'status': 'FAILED', 'output': {'url': odl_url_unified_oper_shallow,
                                               'response_code': response_code,
                                               'response_body': response_json},
                'logs': []}


def read_structured_data(task):
    device_id = task['inputData']['id']
    uri = task['inputData']['uri']

    id_url = odl_url_unified_mount + device_id + "/yang-ext:mount" + (uri if uri else "")

    r = requests.get(id_url, headers=odl_headers, auth=odl_credentials, verify=False)
    response_code, response_json = parse_response(r)

    if response_code == requests.codes.ok:
        return {'status': 'COMPLETED', 'output': {'url': id_url,
                                                  'response_code': response_code,
                                                  'response_body': response_json},
                'logs': ["Mountpoint with ID %s read successfully" % device_id]}
    else:
        return {'status': 'FAILED', 'output': {'url': id_url,
                                               'response_code': response_code,
                                               'response_body': response_json},
                'logs': ["Unable to read device with ID %s" % device_id]}


def write_structured_data(task):
    device_id = task['inputData']['id']
    uri = task['inputData']['uri']
    template = task['inputData']['template']
    params = task['inputData']['params'] if task['inputData']['params'] else {}

    data_json = template if isinstance(template, basestring) else json.dumps(template if template else {})
    data_json = Template(data_json).substitute(params)

    id_url = odl_url_unified_mount + device_id + "/yang-ext:mount" + (uri if uri else "")
    id_url = Template(id_url).substitute(params)

    r = requests.put(id_url, data=data_json, headers=odl_headers, auth=odl_credentials, verify=False)
    response_code, response_json = parse_response(r)

    if response_code == requests.codes.ok or response_code == requests.codes.created:
        return {'status': 'COMPLETED', 'output': {'url': id_url,
                                                  'request_url': id_url,
                                                  'response_code': response_code,
                                                  'response_body': response_json},
                'logs': ["Mountpoint with ID %s updated successfully" % device_id]}
    else:
        return {'status': 'FAILED', 'output': {'url': id_url,
                                               'request_url': id_url,
                                               'response_code': response_code,
                                               'response_body': response_json},
                'logs': ["Unable to update device with ID %s" % device_id]}


def delete_structured_data(task):
    device_id = task['inputData']['id']
    uri = task['inputData']['uri']

    id_url = odl_url_unified_mount + device_id + "/yang-ext:mount" + (uri if uri else "")

    r = requests.delete(id_url, headers=odl_headers, auth=odl_credentials, verify=False)
    response_code, response_json = parse_response(r)

    if response_code == requests.codes.ok:
        return {'status': 'COMPLETED', 'output': {'url': id_url,
                                                  'request_url': id_url,
                                                  'response_code': response_code,
                                                  'response_body': response_json},
                'logs': ["Mountpoint with ID %s updated successfully" % device_id]}
    else:
        return {'status': 'FAILED', 'output': {'url': id_url,
                                               'request_url': id_url,
                                               'response_code': response_code,
                                               'response_body': response_json},
                'logs': ["Unable to update device with ID %s" % device_id]}


def start(cc):
    print('Starting Unified workers')

    cc.start('UNIFIED_read_unified_topology_operational', execute_read_unified_topology_operational, False)
    cc.start('UNIFIED_get_all_devices_as_tasks', get_all_devices_as_tasks, False)
    cc.start('UNIFIED_read_structured_device_data', read_structured_data, False)
    cc.start('UNIFIED_write_structured_device_data', write_structured_data, False)
    cc.start('UNIFIED_delete_structured_device_data', delete_structured_data, False)
