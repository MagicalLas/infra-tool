package dev.magical.redisworker.controller

import io.lettuce.core.RedisClient
import io.lettuce.core.cluster.ClusterClientOptions
import io.lettuce.core.cluster.ClusterTopologyRefreshOptions
import io.lettuce.core.cluster.RedisClusterClient
import io.lettuce.core.cluster.api.StatefulRedisClusterConnection
import io.lettuce.core.event.EventPublisherOptions
import io.lettuce.core.metrics.MicrometerCommandLatencyRecorder
import io.lettuce.core.metrics.MicrometerOptions
import io.lettuce.core.resource.ClientResources
import jakarta.annotation.PreDestroy
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController
import java.lang.Thread.sleep
import java.time.Duration
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import kotlin.random.Random


@RestController
class SimpleController(

) {

    // RedisClusterClient 설정
    final val client: RedisClusterClient = RedisClusterClient.create("redis://127.0.0.1:6001")

    // 클러스터 토폴로지 리프레시 옵션 설정
    final val topologyRefreshOptions: ClusterTopologyRefreshOptions = ClusterTopologyRefreshOptions.builder()
            .enablePeriodicRefresh(Duration.ofMillis(100)) // 주기적 리프레시 활성화
            .enableAllAdaptiveRefreshTriggers() // 모든 적응형 리프레시 트리거 활성화
            .build()

    // 스레드 개수
    private final val mThreads = 40
    val executor: ExecutorService = Executors.newFixedThreadPool(mThreads)
    val r = Random(114123)
    @PreDestroy
    fun destroy() {
        executor.shutdownNow()
        executor.close()
    }

    init {
        client.setOptions(ClusterClientOptions.builder()
                .topologyRefreshOptions(topologyRefreshOptions)
                .build())
    }

    @RequestMapping("/redis")
    @GetMapping
    fun get() {
        repeat(mThreads) { threadNum ->
            executor.execute {
                // 클라이언트 사용 예시
                val connection = client.connect()
                val syncCommands = connection.sync()
                connection.use {
                    while (isRunning(connection, threadNum)) {
                        val key = "key-$threadNum-${r.nextInt(0,1000)}"
                        val value = "valuevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevalue"

                        syncCommands.setex(key, 10000, value)
//                        println("${Thread.currentThread().name} set: $key = $value")

                        val retrievedValue = syncCommands.get(key)
//                        println("${Thread.currentThread().name} get: $key = $retrievedValue")
                        sleep(1)
                    }
                }
            }
        }

        executor.shutdown()
        executor.awaitTermination(1, TimeUnit.HOURS)
    }

    fun isRunning(client: StatefulRedisClusterConnection<String, String>, threadNum: Int): Boolean {
        return client.sync().get("worker$threadNum-working").startsWith("running")
    }

    @RequestMapping("/redis/start")
    @GetMapping
    fun start() {
        val connection = client.connect()
        repeat(mThreads) { threadNum ->
            connection.async().set("worker$threadNum-working", "running")
        }
    }

    @RequestMapping("/redis/stop")
    @GetMapping
    fun stop() {
        val connection = client.connect()
        repeat(mThreads) { threadNum ->
            connection.async().set("worker$threadNum-working", "not-run")
        }
    }
}