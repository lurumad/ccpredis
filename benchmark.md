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

## Change for loop by List Comprehension

```commandline
SET: 56882.82 requests per second, p50=0.815 msec
GET: 63251.11 requests per second, p50=0.775 msec
INCR: 60459.49 requests per second, p50=0.799 msec
LPUSH (needed to benchmark LRANGE): 23078.70 requests per second, p50=2.119 msec
LRANGE_100 (first 100 elements): 19673.42 requests per second, p50=2.407 msec
LRANGE_300 (first 300 elements): 8745.08 requests per second, p50=5.551 msec
LRANGE_500 (first 500 elements): 5738.55 requests per second, p50=8.479 msec
LRANGE_600 (first 600 elements): 4922.23 requests per second, p50=9.879 msec
```




 