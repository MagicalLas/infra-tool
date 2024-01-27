redis-cli --cluster create 127.0.0.1:6001 127.0.0.1:6002 127.0.0.1:6003 127.0.0.1:6004 127.0.0.1:6005 127.0.0.1:6006 --cluster-replicas 1



redis-cli --cluster call 127.0.0.1:6001 config set loglevel verbose
redis-cli --cluster call 127.0.0.1:6001 config set cluster-announce-hostname ""

redis-cli -p 6004 cluster failover
