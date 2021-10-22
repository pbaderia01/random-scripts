**Steps:**

**Run a local docker registry:**

-> docker service create --name registry --publish published=5000,target=5000 registry:2

-> curl http://localhost:5000/v2/       #verify if working or not with empty response

**Run docker stack:**

Build an app image.

-> cd app/

-> docker build -t 127.0.0.1:5000/backend-users-go .

-> docker stack deploy -c docker-stack.yml myapp




**Derived from** https://github.com/brunaobh/go-mongodb-rest-api-crud

**Pending Tasks:**

-> Unit Tests

-> Documentation