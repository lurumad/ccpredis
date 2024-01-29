# Redis Server in Python

One day, while browsing my timeline in X, I found this [page](https://codingchallenges.fyi/challenges/challenge-redis/) of programming challenges. 
On my way to improve my coding skills in Python and getting more knowledge about Redis, I decided to develop my own Redis version.

In this repo, you'll find a lite version of Redis Server developed in Python using asyncio to support multiple concurrent connections.
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






