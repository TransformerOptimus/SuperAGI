# Docker Compose

This `Docker Compose` file is used to define and run multiple-container Docker applications.

## Services
There are several services defined, which are as follows:

- **Backend**: This service uses the `"superagidev/superagi:main"` image, and is dependent on both the `super__redis` and `super__postgres` services. It also uses a config YAML file for environment variables, and awaits for the postgres service to start running before executing its own command at `/app/entrypoint.sh`.
- **Celery**: This service also uses the `"superagidev/superagi:main"` image with similar dependencies as the backend. Instead of waiting for the postgres service, it runs the script at `/app/entrypoint_celery.sh`.
- **GUI**: This service uses the `"superagidev/superagi-frontend:main"` image and sets the `NEXT_PUBLIC_API_BASE_URL` environment variable to `/api` for the API base URL.
- **Super__Redis**: This service uses the `"redis/redis-stack-server:latest"` image to provide a Redis cache and used as a vector store service.
- **Super__Postgres**: This service uses the `postgres` image to provide a PostgreSQL database service, with some environment variables for PostgreSQL configuration.
- **Proxy**: This service uses the `nginx:stable-alpine` image to proxy connections to either the backend or GUI. It also exposes its port 80 to the host's port 3000.

## Networks
A network `super_network` is defined under which all services are running so they can communicate with each other easily.

## Volumes
Two volumes (`superagi_postgres_data`, `redis_data`) are defined for data persistence for the postgres and redis services, respectively.

## Ports
You'll notice some sections for exposing ports are commented out. Uncomment these if you wish to directly access these services from your host machine. The GUI is already set up to expose its port 80 to the host's port 3000 via the Proxy service.

The docker-compose file will orchestrate all these services together. When you run `docker-compose up`, it will start all these services in the order defined by their `depends_on` fields. It automatically handles the networking, volume mounting, and order of service startup for you.