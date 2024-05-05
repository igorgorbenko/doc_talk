#!/bin/bash

service_name="postgres"
container_id=$(docker ps --format '{{.Names}} {{.ID}}' | grep "$service_name" | cut -d' ' -f2)

if [ -z "$container_id" ]; then
    echo "Container $service_name does not exist"
    exit 1
fi


cat migration.sql | docker exec -i $container_id psql -U admin -d proton
