Backend implemented in FastApi for CRUD stuff with ArangoDB.

### Attributions

- FastAPI:    https://github.com/fastapi/fastapi
- ArangoDB:  https://arangodb.com/

# Quickstart - Docker Compose

Fairly easy installation using Docker Compose

## Prerequisites

- Install it according to the documentation: https://docs.docker.com/engine/install/
-

Create a directory somewhere and cd into it:

```bash
$ mkdir /path/to/project && cd /path/to/project
```

Create a docker-compose.yml

#### Nano

```sh
$ nano docker-compose.yml
```

Copy the following contents into docker-compose.yml

```yml
services:
  circusbackend:
    image: registry.erikhorn.de/circusbackend:latest
    restart: always
    pull_policy: always
    container_name: "circusbackend"
    hostname: "circusbackend"
    env_file:
      - '.env'
    ports:
      - "8079:8080"
    environment:
      - PROD_BASE_URL=${PROD_BASE_URL}

    networks:
      - database-tier
#=========================
      - proxy # This project requires a proxy / SSL certificate! 
#=========================
    depends_on:
      - "db"
  db:
    image: arangodb/arangodb
    container_name: "db"
    hostname: "circusdb"
    env_file:
      - '.env'
    environment:
      - ARANGO_ROOT_PASSWORD=${ARANGO_ROOT_PW}
      - JWTSECRET=${JWTSECRET}
    ports:
      - '8529:8529'
      - '8530:8530'
    command:
      - arangod
      - --server.endpoint=tcp://0.0.0.0:8529
      - --server.endpoint=ssl://0.0.0.0:8530
      - --server.jwt-secret-keyfile=/var/lib/secrets/JWTSECRET
      - --ssl.keyfile=/var/lib/secrets/server.pem
      - --ssl.session-cache
      - --query.cache-mode=on
      - --hund
      - --fortune
    volumes:
      - ./arangodb/services:/var/lib/arangodb3-apps/
      - ./arangodb/secrets:/var/lib/secrets
      - ./arangodb/data:/var/lib/arangodb3
    networks:
      - database-tier
networks:
  database-tier:
    external: false
```

I hope you noticed the "proxy" network. Currently, this project is only configured to work behind a proxy
OR
an SSL Certificate. Which option suits you better is up to you. Make sure to disable CORS when developing locally to
save yourself from a lot of brain damage:

#### macOS

```bash
open -n 'path/to/chrome.app' --disable-web-security
```

This allows a local instance to run on https.

Copy .example.env and change all parameters to your liking.

```bash
$ cp .example.env .env
```

Then start the stack:

```bash
docker-compose up -d
```

### Related:

- Angular Frontend: Comin Soon!
