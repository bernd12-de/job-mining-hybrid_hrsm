package de.layher.jobmining.kotlinapi.infrastructure

import de.layher.jobmining.kotlinapi.domain.EscoSkill
import de.layher.jobmining.kotlinapi.infrastructure.io.IOService
import org.springframework.stereotype.Repository
import org.springframework.beans.factory.annotation.Value
import java.util.concurrent.ConcurrentHashMap
import jakarta.annotation.PostConstruct
import java.io.File // 🚨 WICHTIG: Behebt 'Unresolved reference: File'

@Repository
class EscoDataRepository(
    private val ioService: IOService,
    @Value("\${app.esco.data-path:./data/esco}") private val escoFolderPath: String
) {
    private val skillMap = ConcurrentHashMap<String, EscoSkill>()

    @PostConstruct
    fun init() {
        val totalLoaded = loadAllFromFolder()
        // Integritätscheck für wissenschaftliche Validität
        if (totalLoaded < 10000) {
            throw IllegalStateException("Integritätscheck fehlgeschlagen: Nur $totalLoaded ESCO-Labels gefunden!")
        }
        println("✅ ESCO-Wissensbasis erfolgreich geladen: $totalLoaded Einträge aus allen CSVs.")
    }

    fun loadAllFromFolder(): Int {
        var totalLoadedCount = 0
        val folder = File(escoFolderPath)

        if (!folder.exists() || !folder.isDirectory) {
            println("❌ Fehler: ESCO-Verzeichnis nicht gefunden unter: \${folder.absolutePath}")
            return 0
        }

        // Scannt alle 14+ Dateien (Digital, Green, Research etc.)
        val csvFiles = folder.listFiles { file ->
            file.extension.lowercase() == "csv" && !file.name.lowercase().startsWith("occupation")
        } ?: emptyArray()

        println("🔎 Gefundene CSV-Dateien: \${csvFiles.size}")

        csvFiles.forEach { file ->
            try {
                file.bufferedReader().useLines { lines ->
                    // Überspringt die Header-Zeile
                    lines.drop(1).forEach { line ->
                        if (line.isBlank()) return@forEach

                        try {
                            // 🚨 DER FIX: Flexibles Splitten für unterschiedliche CSV-Formate
                            var cols = line.split(";")
                            if (cols.size < 2) {
                                cols = line.split(",")
                            }

                            if (cols.size >= 2) {
                                // Bereinigung von Anführungszeichen (oft in ESCO-Exports vorhanden)
                                val uri = cols[0].replace("\"", "").trim()
                                val label = cols[1].replace("\"", "").trim()

                                if (label.isNotEmpty()) {
                                    val skill = EscoSkill(
                                        uri = uri,
                                        preferredLabel = label,
                                        altLabels = emptyList()
                                    )

                                    // Deduplizierung über alle 14 Dateien hinweg
                                    val key = label.lowercase()
                                    if (!skillMap.containsKey(key)) {
                                        skillMap[key] = skill
                                        totalLoadedCount++
                                    }
                                }
                            }
                        } catch (e: Exception) {
                            // Einzelne fehlerhafte Zeilen (wie deine Zeile 15) überspringen
                        }
                    }
                }
            } catch (e: Exception) {
                println("⚠️ Fehler beim Lesen der Datei \${file.name}: \${e.message}")
            }
        }
        return totalLoadedCount
    }


    fun findAllLoadedSkills(): List<EscoSkill> {
        return skillMap.values.toList()
    }

    fun getSkillByLabel(label: String): EscoSkill? = skillMap[label.lowercase()]
}
