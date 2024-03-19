# Redis Server in Python

One day, while browsing my timeline in X, I found this [page](https://codingchallenges.fyi/challenges/challenge-redis/) of programming challenges.
On my way to improve my coding skills in Python and getting more knowledge about Redis, I decided to develop my own Redis version. I enjoy the journey a lot, and I'm very surprised (for good) at how well thought out was Redis and it's simplicity.

In this repo, you'll find a lite version of Redis Server (Non-Production) developed in Python using asyncio to support multiple concurrent connections.
I develop all the functionality using TDD, so you'll find a lot of tests covering the main functionality, and they'll help you to understand the Redis Serialisation Protocol (aka RESP), Data Structures, Expiration, Persistence, etc.

Below, you'll find all the commands supported by the server:

- [x] PING - test whether a connection is still alive
- [x] ECHO - returns message
- [x] SET - set key to hold the string value
- [x] GET - get the value of a key
- [x] EXISTS - check if a key is present.
- [x] DEL - delete one or more keys.
- [x] INCR - increment a stored number by one.
- [x] DECR - decrement a stored number by one.
- [x] LPUSH - insert all the values at the head of a list.
- [x] RPUSH - insert all the values at the tail of a list.
- [x] LRANGE - get the specified elements of the list stored at the supplied key.

## How to run it

Install [poetry](https://python-poetry.org/docs/#installation)

Run the server

```cmd
poetry run python -m pyredis
```

Install [Redis](https://redis.io/docs/install/install-redis/) and you can connect using `redis-cli`

Test a command

```cmd
redis-cli ping
PONG
```

## How to run tests

```cdm
poetry run pytest
```

# Performance

In this section, our goal is to use Redis Benchmark tool to test our server and try to improve it.

```commandline
redis-benchmark -t get,set,incr,lrange -n 100000 -q
```

## First Measure

```commandline
SET: 55218.11 requests per second, p50=0.839 msec
GET: 59453.03 requests per second, p50=0.791 msec
INCR: 60240.96 requests per second, p50=0.791 msec
LPUSH (needed to benchmark LRANGE): 23105.36 requests per second, p50=2.095 msec
LRANGE_100 (first 100 elements): 19164.43 requests per second, p50=2.487 msec
LRANGE_300 (first 300 elements): 8179.29 requests per second, p50=5.823 msec
LRANGE_500 (first 500 elements): 5302.51 requests per second, p50=8.935 msec
LRANGE_600 (first 600 elements): 4593.48 requests per second, p50=10.455 msec
```
