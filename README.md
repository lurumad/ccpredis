# Redis Server in Python

A lite version of Redis Server in Python using asyncio to support multiple concurrent connections.

```bash
luru@Luiss-MacBook-Pro: ~/Developer/redis-server: redis-benchmark -t SET,GET -n 10000 -q
WARNING: Could not fetch server CONFIG
SET: 50505.05 requests per second, p50=0.807 msec
GET: 66666.66 requests per second, p50=0.743 msec
```

All the functionality supported by the server (work in progress):

- [x] PING - test whether a connection is still alive
- [x] ECHO - returns message
- [x] SET - set key to hold the string value
- [x] GET - get the value of a key
- [x] EXISTS - check if a key is present.
- [x] DEL - delete one or more keys.
- [x] INCR - increment a stored number by one.
- [ ] DECR - decrement a stored number by one.
- [ ] LPUSH - insert all the values at the head of a list.
- [ ] RPUSH - insert all the values at the tail of a list.
- [ ] LRANGE - get the specified elements of the list stored at the supplied key.



