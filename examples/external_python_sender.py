"""
External Python Program - Job Data Sender
Sendet Job-Daten an das Job Mining API

Use Cases:
- Scraping von Job-Websites
- Import von CSV/Excel
- Integration mit anderen Systemen
- Batch-Import von historischen Daten
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict
import random
import json


class JobDataSender:
    """Client zum Senden von Job-Daten an das API"""

    def __init__(self, api_url: str = "http://localhost:5000"):
        self.api_url = api_url
        self.ingest_endpoint = f"{api_url}/api/data/ingest"

    def send_jobs(self, jobs: List[Dict]) -> Dict:
        """
        Sendet Job-Daten an das API

        Args:
            jobs: Liste von Job-Dictionaries

        Returns:
            Response vom API
        """
        try:
            response = requests.post(
                self.ingest_endpoint,
                json=jobs,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()

            result = response.json()
            print(f"✅ Successfully sent {result['count']} jobs")
            return result

        except requests.exceptions.RequestException as e:
            print(f"❌ Error sending data: {e}")
            if hasattr(e.response, 'text'):
                print(f"   Response: {e.response.text}")
            raise

    def generate_sample_jobs(self, count: int = 10) -> List[Dict]:
        """
        Generiert Sample-Jobs für Testing

        Args:
            count: Anzahl der zu generierenden Jobs

        Returns:
            Liste von Job-Dictionaries
        """
        roles = ["Software Developer", "Data Scientist", "DevOps Engineer", "Project Manager", "UI/UX Designer"]
        cities = [
            {"city": "Berlin", "lat": 52.5200, "lon": 13.4050},
            {"city": "München", "lat": 48.1351, "lon": 11.5820},
            {"city": "Hamburg", "lat": 53.5511, "lon": 9.9937},
            {"city": "Köln", "lat": 50.9375, "lon": 6.9603},
            {"city": "Frankfurt", "lat": 50.1109, "lon": 8.6821},
        ]

        skills_by_role = {
            "Software Developer": ["Python", "Java", "JavaScript", "Docker", "Kubernetes", "Git", "SQL"],
            "Data Scientist": ["Python", "R", "Machine Learning", "TensorFlow", "Pandas", "SQL"],
            "DevOps Engineer": ["Docker", "Kubernetes", "AWS", "Terraform", "Jenkins", "Linux", "CI/CD"],
            "Project Manager": ["Agile", "Scrum", "Jira", "MS Project"],
            "UI/UX Designer": ["Figma", "Adobe XD", "Sketch", "Prototyping"],
        }

        jobs = []
        for i in range(count):
            role = random.choice(roles)
            location = random.choice(cities)
            year = random.randint(2020, 2025)
            month = random.randint(1, 12)
            day = random.randint(1, 28)

            job = {
                "title": f"{role} (m/w/d) - {location['city']}",
                "role": role,
                "description": f"Wir suchen einen {role} für unser Team in {location['city']}.",
                "city": location['city'],
                "country": "DE",
                "latitude": location['lat'],
                "longitude": location['lon'],
                "posted_at": f"{year}-{month:02d}-{day:02d}T10:00:00",
                "skills": random.sample(skills_by_role[role], k=random.randint(3, 6)),
                "source": "external_python_sender"
            }
            jobs.append(job)

        return jobs

    def import_from_csv(self, csv_path: str) -> List[Dict]:
        """
        Importiert Jobs aus CSV-Datei

        CSV Format:
        title,role,city,country,latitude,longitude,posted_at,skills

        Args:
            csv_path: Pfad zur CSV-Datei

        Returns:
            Liste von Job-Dictionaries
        """
        import csv

        jobs = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                job = {
                    "title": row['title'],
                    "role": row['role'],
                    "description": row.get('description', ''),
                    "city": row['city'],
                    "country": row.get('country', 'DE'),
                    "latitude": float(row['latitude']) if row.get('latitude') else None,
                    "longitude": float(row['longitude']) if row.get('longitude') else None,
                    "posted_at": row['posted_at'],
                    "skills": row.get('skills', '').split(',') if row.get('skills') else [],
                    "source": "csv_import"
                }
                jobs.append(job)

        print(f"📊 Loaded {len(jobs)} jobs from {csv_path}")
        return jobs


def main():
    """Main execution"""
    print("=" * 60)
    print("External Python Job Data Sender")
    print("=" * 60)

    # Initialize sender
    sender = JobDataSender(api_url="http://localhost:5000")

    # Option 1: Generate and send sample data
    print("\n1️⃣ Generating sample jobs...")
    sample_jobs = sender.generate_sample_jobs(count=20)

    print("\n2️⃣ Sending jobs to API...")
    result = sender.send_jobs(sample_jobs)

    print(f"\n✅ Result: {result}")

    # Option 2: Import from CSV (uncomment if you have a CSV file)
    # csv_jobs = sender.import_from_csv("jobs_data.csv")
    # sender.send_jobs(csv_jobs)


if __name__ == "__main__":
    # Example 1: Basic usage
    main()

    # Example 2: Custom jobs
    # sender = JobDataSender()
    # custom_jobs = [
    #     {
    #         "title": "Senior Python Developer",
    #         "role": "Software Developer",
    #         "city": "Berlin",
    #         "country": "DE",
    #         "latitude": 52.52,
    #         "longitude": 13.40,
    #         "posted_at": "2025-12-27T10:00:00",
    #         "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
    #         "source": "custom"
    #     }
    # ]
    # sender.send_jobs(custom_jobs)
