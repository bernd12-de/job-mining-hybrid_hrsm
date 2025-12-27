package de.layher.jobmining.kotlinapi.infrastructure.config

import de.layher.jobmining.kotlinapi.adapters.PythonAnalysisClient
import de.layher.jobmining.kotlinapi.infrastructure.DomainRuleRepository
import org.springframework.beans.factory.annotation.Value
import org.springframework.boot.ApplicationArguments
import org.springframework.boot.ApplicationRunner
import org.springframework.stereotype.Component
import org.springframework.web.client.HttpClientErrorException
import org.springframework.web.client.ResourceAccessException
import org.springframework.web.client.RestTemplate
import javax.sql.DataSource
import java.net.InetAddress


@Component
class StartupCheckRunner(
    private val dataSource: DataSource,
    private val pythonClient: PythonAnalysisClient,
    private val domainRuleRepository: DomainRuleRepository,
    @Value("\${python.api.base-url:http://localhost:8000}")
    private val pythonBaseUrl: String
) : ApplicationRunner {
    private val restTemplate = RestTemplate()
    override fun run(args: ApplicationArguments) { // FIX: Ohne '?'
        val ip = java.net.InetAddress.getLocalHost().hostAddress
        println("\n" + "=".repeat(45))
        println("🚀 SYSTEM-CHECK | KOTLIN-IP: $ip")

        checkPython()
        checkApiPoints()
        println("=".repeat(45) + "\n")

        checkDatabase()

        println("-".repeat(100))
    }

    private fun checkPython() {
        val pythonUrl = "http://localhost:8000/health/status"

        try {
            val response = restTemplate.getForEntity(pythonUrl, Map::class.java)
            val body = response.body
            if (body != null) {
                println("✅ PYTHON-ENGINE: ${body["status"]} (Labels: ${body["esco_labels"]})")
            }
        } catch (e: Exception) {
            println("⚠️ PYTHON-ENGINE: Offline auf Port 8000")
        }
    }


    private fun checkApiPoints() {
        val myIp = InetAddress.getLocalHost().hostAddress

        println("\n" + "=".repeat(100))
        println(" 🚀 SYSTEM-INTEGRATION TEST | HOST: $myIp")
        println(" 🎯 Ziel-Python: $pythonBaseUrl")
        println("-".repeat(100))
        println(String.format("%-40s | %-10s | %s", "ENDPUNKT (PFAD)", "METHODE", "LIVE-STATUS"))
        println("-".repeat(100))

        // Hier definieren wir die Pfade, die im 'PythonAnalysisClient' genutzt werden.
        // Wir testen sie jetzt live gegen das laufende Python-System.

        checkEndpoint("/analyse/file", "POST")           // Upload
        checkEndpoint("/analyse/scrape-url", "POST") // Scraper
        checkEndpoint("/batch-process", "POST")      // Batch
        checkEndpoint("/internal/admin/refresh-knowledge", "POST") // Refresh
        checkEndpoint("/system/status", "GET")       // Health Check
        checkEndpoint("/role-mappings", "GET") // Testet ob der Controller auf die DB zugreifen kann

        println("=".repeat(100) + "\n")
    }

    private fun checkEndpoint(path: String, method: String) {
        val url = "$pythonBaseUrl$path"
        var statusIcon = "❓"
        var statusText = "Unbekannt"

        try {
            if (method == "GET") {
                // Bei GET erwarten wir echten Erfolg (200 OK)
                restTemplate.getForEntity(url, String::class.java)
                statusIcon = "✅"
                statusText = "200 OK (Erreichbar)"
            } else {
                // TRICK: Bei POST senden wir absichtlich GET.
                // Wenn 405 (Method Not Allowed) kommt, WISSEN wir, dass der Pfad existiert!
                // Wenn 404 kommt, existiert er nicht.
                restTemplate.getForEntity(url, String::class.java)
            }
        } catch (e: HttpClientErrorException) {
            // Analyse des Fehlercodes
            when (e.statusCode.value()) {
                404 -> {
                    statusIcon = "❌"
                    statusText = "404 NOT FOUND (Pfad falsch!)"
                }
                405 -> {
                    // Method Not Allowed -> Das ist GUT! Der Endpunkt existiert.
                    statusIcon = "✅"
                    statusText = "Gefunden (405 Verified)"
                }
                422 -> {
                    // Unprocessable Entity -> Auch GUT! Er wartet auf Daten.
                    statusIcon = "✅"
                    statusText = "422 Verified (Wartet auf Daten)"
                }
                else -> {
                    statusIcon = "⚠️"
                    statusText = "Code ${e.statusCode.value()}"
                }
            }
        } catch (e: ResourceAccessException) {
            statusIcon = "🚫"
            statusText = "OFFLINE (Keine Verbindung)"
        } catch (e: Exception) {
            statusIcon = "💥"
            statusText = "Error: ${e.message}"
        }

        println(String.format("%-40s | %-10s | %s %s", path, method, statusIcon, statusText))
    }


    private fun checkDatabase() {
        print(String.format("%-40s | ", "🔌 POSTGRES DATENBANK (Docker)"))

        try {
            // A) Verbindungstest (Ping)
            val connection = dataSource.connection
            val metaData = connection.metaData
            val dbProduct = metaData.databaseProductName
            val dbVersion = metaData.databaseProductVersion
            val dbName = metaData.url.substringAfterLast("/").substringBefore("?")
            
            // B) Daten-Test (Sind die V4 Regeln da?)
            val ruleCount = domainRuleRepository.count()
            
            // C) Zähle Daten in allen wichtigen Tabellen
            val statement = connection.createStatement()
            val jobCount = try {
                val rs = statement.executeQuery("SELECT COUNT(*) FROM job_postings")
                if (rs.next()) rs.getLong(1) else 0L
            } catch (e: Exception) { 0L }
            
            val escoCount = try {
                val rs = statement.executeQuery("SELECT COUNT(*) FROM esco_data")
                if (rs.next()) rs.getLong(1) else 0L
            } catch (e: Exception) { 0L }
            
            statement.close()
            connection.close()

            if (ruleCount > 0) {
                // Alles perfekt: Verbunden UND Daten da
                println("✅ ONLINE ($dbProduct $dbVersion)")
                println(String.format("%-40s | ✅ DATEN-CHECK: %d Regeln geladen (V4 OK)", "", ruleCount))
                println(String.format("%-40s | 📊 DB '$dbName': %d Jobs | %d ESCO-Skills | %d Rules", 
                    "", jobCount, escoCount, ruleCount))
            } else {
                // Verbunden, aber Tabelle leer (V4 fehlgeschlagen oder Tabelle falsch gemappt)
                println("⚠️ LEER ($dbProduct)")
                println(String.format("%-40s | ❌ WARNUNG: Tabelle 'domain_rule' ist leer!", ""))
                println(String.format("%-40s | 📊 DB '$dbName': %d Jobs | %d ESCO-Skills", 
                    "", jobCount, escoCount))
            }

        } catch (e: Exception) {
            println("❌ OFFLINE")
            println(String.format("%-40s | Fehler: %s", "", e.message))
        }
    }


    private fun printRow(feature: String, method: String, path: String, isSystemOnline: Boolean) {
        // Wenn das System online ist, gehen wir davon aus, dass die Routen funktionieren (da hardcoded)
        val status = if (isSystemOnline) "\u001B[32m✅ BEREIT\u001B[0m" else "\u001B[31m❌ WARTEN\u001B[0m"
        println(String.format("%-25s | %-8s | %-40s | %s", feature, method, path, status))
    }
}

annotation class Value(val value: String)
