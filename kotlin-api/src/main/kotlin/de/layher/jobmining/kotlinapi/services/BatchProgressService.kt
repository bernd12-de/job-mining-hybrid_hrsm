package de.layher.jobmining.kotlinapi.services

import org.springframework.stereotype.Service
import java.time.Instant
import java.util.concurrent.atomic.AtomicReference

data class BatchProgress(
    val total: Int = 0,
    val processed: Int = 0,
    val percentage: Int = 0,
    val status: String = "idle", // idle|running|completed
    val startedAt: Long? = null,
    val finishedAt: Long? = null,
    val progressBar: String = ""
)

@Service
class BatchProgressService {
    private val ref = AtomicReference(BatchProgress())

    fun start() {
        ref.set(BatchProgress(status = "running", startedAt = Instant.now().toEpochMilli()))
    }

    fun setTotal(total: Int) {
        val cur = ref.get()
        ref.set(cur.copy(total = total))
    }

    fun update(processed: Int, percentage: Int, bar: String) {
        val cur = ref.get()
        ref.set(cur.copy(processed = processed, percentage = percentage, progressBar = bar))
    }

    fun finish() {
        val cur = ref.get()
        ref.set(cur.copy(status = "completed", percentage = 100, processed = cur.total, finishedAt = Instant.now().toEpochMilli(), progressBar = "██████████"))
    }

    fun snapshot(): BatchProgress = ref.get()
    fun reset() { ref.set(BatchProgress()) }
}
