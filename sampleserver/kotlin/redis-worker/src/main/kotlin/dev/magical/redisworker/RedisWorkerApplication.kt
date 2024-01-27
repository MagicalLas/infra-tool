package dev.magical.redisworker

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication

@SpringBootApplication
class RedisWorkerApplication

fun main(args: Array<String>) {
	runApplication<RedisWorkerApplication>(*args)
}
