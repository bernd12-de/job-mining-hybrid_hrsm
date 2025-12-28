package de.layher.jobmining.kotlinapi.services

import org.springframework.stereotype.Service
import java.time.Instant
import java.util.concurrent.atomic.AtomicReference
import com.fasterxml.jackson.annotation.JsonProperty

data class BatchProgress(
    val total: Int = 0,
    val processed: Int = 0,
    val percentage: Int = 0,
    val status: String = "idle", // idle|running|completed|cancelled
    val startedAt: Long? = null,
    val finishedAt: Long? = null,
    val progressBar: String = "",
    // Neue Felder für erweiterte Info
    @JsonProperty("current_file")
    val currentFile: String = "",
    @JsonProperty("estimated_seconds_remaining")
    val estimatedSecondsRemaining: Long = 0,
    @JsonProperty("failed_count")
    val failedCount: Int = 0,
    @JsonProperty("skipped_count")
    val skippedCount: Int = 0
)

@Service
class BatchProgressService {
    private val ref = AtomicReference(BatchProgress())
    @Volatile
    private var cancellationRequested = false

    fun start() {
        cancellationRequested = false
        ref.set(BatchProgress(status = "running", startedAt = Instant.now().toEpochMilli()))
    }

    fun setTotal(total: Int) {
        val cur = ref.get()
        ref.set(cur.copy(total = total))
    }

    fun update(
        processed: Int,
        percentage: Int,
        bar: String,
        currentFile: String = "",
        failedCount: Int = 0,
        skippedCount: Int = 0
    ) {
        val cur = ref.get()
        val elapsedSeconds = if (cur.startedAt != null) {
            (Instant.now().toEpochMilli() - cur.startedAt) / 1000
        } else 0
        
        // ETA berechnen: wenn noch etwas zu tun ist
        val eta = if (processed > 0 && cur.total > processed) {
            val secondsPerItem = elapsedSeconds / processed
            val itemsRemaining = cur.total - processed
            secondsPerItem * itemsRemaining
        } else 0
        
        ref.set(cur.copy(
            processed = processed,
            percentage = percentage,
            progressBar = bar,
            currentFile = currentFile,
            estimatedSecondsRemaining = eta,
            failedCount = failedCount,
            skippedCount = skippedCount
        ))
    }

    fun finish() {
        val cur = ref.get()
        ref.set(cur.copy(
            status = "completed",
            percentage = 100,
            processed = cur.total,
            finishedAt = Instant.now().toEpochMilli(),
            progressBar = "██████████"
        ))
    }

    fun cancel() {
        cancellationRequested = true
        val cur = ref.get()
        ref.set(cur.copy(status = "cancelled"))
    }

    fun isCancellationRequested(): Boolean = cancellationRequested

    fun snapshot(): BatchProgress = ref.get()
    fun reset() {
        cancellationRequested = false
        ref.set(BatchProgress())
    }
}
