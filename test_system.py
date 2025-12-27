#!/usr/bin/env python3
"""
Comprehensive system test suite for Job Mining Projekt
Tests both Python and Kotlin APIs with health checks and API endpoints
"""

import subprocess
import time
import requests
import json
import sys
import threading
from pathlib import Path

class SystemTester:
    def __init__(self):
        self.kotlin_pid = None
        self.python_pid = None
        self.results = {
            "python_import": False,
            "kotlin_compile": False,
            "kotlin_start": False,
            "python_start": False,
            "python_health": False,
            "kotlin_health": False,
            "api_tests": []
        }
        self.base_dir = Path(__file__).parent
        
    def test_python_import(self):
        """Test: Python module imports"""
        print("\n=== TEST 1: Python Module Imports ===")
        try:
            result = subprocess.run(
                ["python", "-c", "from main import app; print('OK')"],
                cwd=self.base_dir / "python-backend",
                capture_output=True,
                timeout=10,
                text=True
            )
            if result.returncode == 0 and "OK" in result.stdout:
                print("✅ Python modules loaded successfully")
                self.results["python_import"] = True
                return True
            else:
                print(f"❌ Python import failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Exception: {e}")
            return False

    def test_kotlin_compile(self):
        """Test: Kotlin API compilation"""
        print("\n=== TEST 2: Kotlin API Compilation ===")
        try:
            result = subprocess.run(
                ["./gradlew", "clean", "build", "-x", "test"],
                cwd=self.base_dir / "kotlin-api",
                capture_output=True,
                timeout=120,
                text=True
            )
            if result.returncode == 0:
                print("✅ Kotlin API compiled successfully")
                self.results["kotlin_compile"] = True
                return True
            else:
                print(f"❌ Kotlin compilation failed")
                print(result.stderr[-500:] if result.stderr else "No error output")
                return False
        except Exception as e:
            print(f"❌ Exception: {e}")
            return False

    def start_kotlin_api(self):
        """Start Kotlin API in background"""
        print("\n=== Starting Kotlin API (Port 8080) ===")
        try:
            jar_path = self.base_dir / "kotlin-api/build/libs/kotlin-api-0.0.1-SNAPSHOT.jar"
            if not jar_path.exists():
                print("❌ JAR file not found")
                return False
                
            self.kotlin_proc = subprocess.Popen(
                ["java", "-jar", str(jar_path), "--server.port=8080"],
                cwd=self.base_dir / "kotlin-api",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print(f"✅ Kotlin API process started (PID: {self.kotlin_proc.pid})")
            return True
        except Exception as e:
            print(f"❌ Failed to start Kotlin API: {e}")
            return False

    def start_python_api(self):
        """Start Python API in background"""
        print("\n=== Starting Python API (Port 8000) ===")
        try:
            self.python_proc = subprocess.Popen(
                ["python", "-m", "uvicorn", "main:app", "--port", "8000"],
                cwd=self.base_dir / "python-backend",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print(f"✅ Python API process started (PID: {self.python_proc.pid})")
            return True
        except Exception as e:
            print(f"❌ Failed to start Python API: {e}")
            return False

    def trigger_knowledge_refresh(self):
        """Trigger knowledge base refresh via POST to /internal/admin/refresh-knowledge"""
        print("\n=== TEST 5: Triggering Knowledge Refresh ===")
        try:
            response = requests.post("http://localhost:8000/internal/admin/refresh-knowledge", timeout=30)
            if response.status_code == 200:
                data = response.json()
                skills = data.get("skills", 0)
                print(f"✅ Knowledge refreshed: {skills} skills loaded")
                return True
            else:
                print(f"⚠️ Refresh returned HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"⚠️ Knowledge refresh failed: {e}")
            return False

    def wait_for_service(self, port, max_retries=60, delay=1):
        """Wait for a service to be ready"""
        url = f"http://localhost:{port}/docs" if port == 8000 else f"http://localhost:{port}/actuator/health"
        
        for attempt in range(max_retries):
            try:
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    return True
            except:
                pass
            
            if attempt % 10 == 0:
                print(f"  Waiting for port {port}... ({attempt}s)")
            time.sleep(delay)
        
        return False

    def test_python_health(self):
        """Test: Python API health check"""
        print("\n=== TEST 3: Python API Health ===")
        try:
            response = requests.get("http://localhost:8000/docs", timeout=5)
            if response.status_code == 200:
                print("✅ Python API responding")
                self.results["python_health"] = True
                return True
            else:
                print(f"❌ Python API returned {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Python API not accessible: {e}")
            return False

    def refresh_python_knowledge(self):
        """Trigger knowledge refresh once Python API is up"""
        try:
            r = requests.post("http://localhost:8000/internal/admin/refresh-knowledge", timeout=15)
            if r.status_code == 200:
                print("✅ Python knowledge refreshed")
                return True
            print(f"⚠️ Refresh returned HTTP {r.status_code}")
            return False
        except Exception as e:
            print(f"⚠️ Refresh failed: {e}")
            return False

    def test_kotlin_health(self):
        """Test: Kotlin API health check"""
        print("\n=== TEST 4: Kotlin API Health ===")
        try:
            response = requests.get("http://localhost:8080/actuator/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                status = data.get("status", "UNKNOWN")
                print(f"✅ Kotlin API responding (status: {status})")
                self.results["kotlin_health"] = True
                return True
            else:
                print(f"❌ Kotlin API returned {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Kotlin API not accessible: {e}")
            return False

    def test_api_endpoints(self):
        """Test: Key API endpoints"""
        print("\n=== TEST 6: API Endpoint Tests ===")
        
        tests = [
            {
                "name": "Python: GET /docs (Swagger UI)",
                "url": "http://localhost:8000/docs",
                "method": "GET"
            },
            {
                "name": "Python: GET /openapi.json",
                "url": "http://localhost:8000/openapi.json",
                "method": "GET"
            },
            {
                "name": "Kotlin: GET /actuator",
                "url": "http://localhost:8080/actuator",
                "method": "GET"
            },
            {
                "name": "Kotlin: GET /api/v1/jobs/health",
                "url": "http://localhost:8080/api/v1/jobs/health",
                "method": "GET"
            }
        ]
        
        for test in tests:
            try:
                if test["method"] == "GET":
                    response = requests.get(test["url"], timeout=5)
                    if 200 <= response.status_code < 400:
                        print(f"✅ {test['name']}")
                        self.results["api_tests"].append({"name": test["name"], "status": "PASS"})
                    else:
                        print(f"⚠️ {test['name']} (Status: {response.status_code})")
                        self.results["api_tests"].append({"name": test["name"], "status": f"WARN-{response.status_code}"})
            except Exception as e:
                print(f"❌ {test['name']}: {str(e)[:50]}")
                self.results["api_tests"].append({"name": test["name"], "status": "FAIL"})

    def test_scrape_and_dashboard(self):
        """Scrape zwei Personio-URLs und eine Strauss-URL mit JS-Rendering, prüfe Felder und Dashboard-Metriken"""
        print("\n=== TEST 7: Scrape & Dashboard (Web Job Listings) ===")
        urls = [
            {"url": "https://escape.jobs.personio.com/job/742758?language=de&display=de", "name": "Personio #742758"},
            {"url": "https://escape.jobs.personio.com/job/1118877?language=de&display=de", "name": "Personio #1118877"},
            {"url": "https://www.strauss.com/de/de/Unternehmen/Karriere/Jobangebote/Developer_mwd", "name": "Strauss Developer"},
        ]

        # Vorherige Metriken
        try:
            before = requests.get("http://localhost:8000/reports/dashboard-metrics", timeout=5).json()
            before_jobs = before.get("total_jobs", 0)
            before_skills = before.get("total_skills", 0)
        except Exception as e:
            print(f"⚠️ Konnte Metriken vorher nicht laden: {e}")
            before_jobs = 0
            before_skills = 0

        success_count = 0
        for item in urls:
            u = item["url"]
            name = item["name"]
            try:
                print(f"  ↳ {name}...")
                payload = {"url": u, "render_js": True}
                r = requests.post("http://localhost:8000/analyse/scrape-url", json=payload, timeout=90)
                if r.status_code == 200:
                    data = r.json()
                    title = data.get('title', 'N/A')[:50]
                    role = data.get('job_role', 'N/A')
                    industry = data.get('industry', 'N/A')
                    region = data.get('region', 'N/A')
                    skills_count = len(data.get('competences', []))
                    print(f"    ✅ {title}... | role={role} | region={region} | skills={skills_count}")
                    success_count += 1
                else:
                    print(f"    ⚠️ HTTP {r.status_code}")
            except Exception as e:
                print(f"    ❌ {str(e)[:60]}")

        # Nachherige Metriken
        try:
            after = requests.get("http://localhost:8000/reports/dashboard-metrics", timeout=5).json()
            after_jobs = after.get("total_jobs", 0)
            after_skills = after.get("total_skills", 0)
            top_skills = after.get("top_skills", [])
            print(f"\n  Dashboard Update:")
            print(f"    Jobs: {before_jobs} → {after_jobs} (+{success_count})")
            print(f"    Skills: {before_skills} → {after_skills}")
            if top_skills:
                top_labels = ', '.join([s['skill'][:20] for s in top_skills[:3]])
                print(f"    Top Skills: {top_labels}...")
            
            if after_jobs >= before_jobs + success_count and after_jobs > 0:
                print("\n  ✅ Dashboard-Metriken aktualisiert und konsistent")
                return True
            else:
                print("\n  ⚠️ Dashboard-Metriken Update fraglich")
                return False
        except Exception as e:
            print(f"  ❌ Konnte Metriken nicht laden: {e}")
            return False

    def cleanup(self):
        """Stop background processes"""
        print("\n=== Cleanup ===")
        
        if hasattr(self, 'python_proc') and self.python_proc:
            self.python_proc.terminate()
            try:
                self.python_proc.wait(timeout=5)
                print("✅ Python API stopped")
            except:
                self.python_proc.kill()
                print("⚠️ Python API force-stopped")
        
        if hasattr(self, 'kotlin_proc') and self.kotlin_proc:
            self.kotlin_proc.terminate()
            try:
                self.kotlin_proc.wait(timeout=5)
                print("✅ Kotlin API stopped")
            except:
                self.kotlin_proc.kill()
                print("⚠️ Kotlin API force-stopped")

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        total_tests = 0
        passed_tests = 0
        
        for key, value in self.results.items():
            if key != "api_tests":
                total_tests += 1
                status = "✅ PASS" if value else "❌ FAIL"
                print(f"{key:.<40} {status}")
                if value:
                    passed_tests += 1
        
        # API tests
        if self.results["api_tests"]:
            print(f"\nAPI Endpoints: {len([t for t in self.results['api_tests'] if t['status'] == 'PASS'])}/{len(self.results['api_tests'])} passed")
            for test in self.results["api_tests"]:
                symbol = "✅" if test["status"] == "PASS" else "⚠️" if "WARN" in test["status"] else "❌"
                print(f"  {symbol} {test['name']}: {test['status']}")
        
        print("\n" + "="*60)
        print(f"OVERALL: {passed_tests}/{total_tests} critical tests passed")
        print("="*60)
        
        return passed_tests == total_tests

    def run(self):
        """Execute full test suite"""
        try:
            print("🧪 Starting Job Mining System Test Suite...")
            print(f"📍 Working directory: {self.base_dir}")
            
            # Phase 1: Static tests
            self.test_python_import()
            self.test_kotlin_compile()
            
            if not self.results["python_import"] or not self.results["kotlin_compile"]:
                print("\n❌ Static tests failed. Aborting dynamic tests.")
                self.print_summary()
                return False
            
            # Phase 2: Start services
            self.start_kotlin_api()
            time.sleep(2)
            self.start_python_api()
            
            # Phase 3: Wait for services
            print("\n⏳ Waiting for services to start (60 seconds max)...")
            kotlin_ready = self.wait_for_service(8080, max_retries=60)
            python_ready = self.wait_for_service(8000, max_retries=60)
            
            if kotlin_ready:
                print("✅ Kotlin API ready")
                self.results["kotlin_start"] = True
            else:
                print("⚠️ Kotlin API startup timeout")
            
            if python_ready:
                print("✅ Python API ready")
                self.results["python_start"] = True
            else:
                print("⚠️ Python API startup timeout")
            
            # Phase 4: Dynamic tests
            if self.results["kotlin_start"]:
                self.test_kotlin_health()
            if self.results["python_start"]:
                self.test_python_health()
            
            # Phase 5: Trigger Knowledge Refresh (new)
            if self.results["python_start"]:
                self.trigger_knowledge_refresh()
            
            # Phase 6: API tests
            if self.results["python_start"] or self.results["kotlin_start"]:
                self.test_api_endpoints()

            # Phase 7: Scrape & Dashboard (Web Job Listings)
            if self.results["python_start"]:
                ok = self.test_scrape_and_dashboard()
                self.results["api_tests"].append({"name": "Scrape+Dashboard (Web Jobs)", "status": "PASS" if ok else "FAIL"})

            # Phase 6: Scrape & Dashboard
            if self.results["python_start"]:
                ok = self.test_scrape_and_dashboard()
                self.results["api_tests"].append({"name": "Scrape+Dashboard", "status": "PASS" if ok else "FAIL"})
            
            # Cleanup and summary
            self.cleanup()
            return self.print_summary()
            
        except KeyboardInterrupt:
            print("\n⚠️ Test interrupted by user")
            self.cleanup()
            return False
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            self.cleanup()
            return False

if __name__ == "__main__":
    tester = SystemTester()
    success = tester.run()
    sys.exit(0 if success else 1)
