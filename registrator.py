#!/usr/bin/env python2

import docker
import consul
import json


def service_id(container):
    return container.attrs['Name'].replace("/","")


def name(container):
    return container.attrs['Name'].replace("/","")


docker_client = docker.from_env()
consul_client = consul.Consul()

registered_services = consul_client.agent.services()
services = {}
for container in docker_client.containers.list():
    services[service_id(container)] = {'name': name(container)}

for key in registered_services.keys():
    if key not in services.keys():
        if key != "consul":
            print("Deregistering {}".format(key))
            print(consul_client.agent.service.deregister(key))

for key in services.keys():
    if key not in registered_services.keys():
        consul_client.agent.service.register(services[key]['name'], key)


def register(container):
    key = service_id(container)
    print("Registering {}".format(key))
    consul_client.agent.service.register(name(container), key)


def deregister(container):
    key = service_id(container)
    print("Deregistering {}".format(key))
    consul_client.agent.service.deregister(key)

for event_json in docker_client.events():
    event = json.loads(event_json)
    if event['Type'] == "container":
       id = event['id']
       if event['Action'] == 'start':
           register(docker_client.containers.get(id))
       if event['Action'] == 'stop' or event['Action'] == 'die':
           deregister(docker_client.containers.get(id))


