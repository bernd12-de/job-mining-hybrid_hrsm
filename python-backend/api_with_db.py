"""
FastAPI with PostgreSQL Integration
Extended version of main.py with real database queries
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from typing import List, Dict, Optional
from pydantic import BaseModel
from datetime import datetime
import logging

# Database
from database.db_config import db_config, init_db, close_db

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI App
app = FastAPI(
    title="Job Mining API with PostgreSQL",
    description="Geo-Dashboard mit echten Daten aus PostgreSQL",
    version="2.0"
)

# Mount static files
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except RuntimeError:
    logger.warning("⚠️ Static directory not found")
    os.makedirs("static", exist_ok=True)
    app.mount("/static", StaticFiles(directory="static"), name="static")


# =====================================================
# PYDANTIC MODELS
# =====================================================

class JobInput(BaseModel):
    """Input model for creating jobs"""
    title: str
    role: str
    description: Optional[str] = None
    city: str
    country: str = "DE"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    posted_at: datetime
    skills: List[str] = []
    source: str = "api"


class LocationResponse(BaseModel):
    """Response model for location data"""
    location: str
    lat: Optional[float]
    lon: Optional[float]
    country: str
    count: int
    color: str


class SkillResponse(BaseModel):
    """Response model for skill data"""
    skill: str
    count: int


class GeoHeatmapResponse(BaseModel):
    """Response model for geo-heatmap endpoint"""
    locations: List[LocationResponse]
    competences: List[SkillResponse]


# =====================================================
# STARTUP/SHUTDOWN
# =====================================================

@app.on_event("startup")
async def startup_event():
    """Initialize database connection pool"""
    logger.info("🚀 Starting FastAPI with PostgreSQL...")
    try:
        init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        logger.warning("⚠️ Running without database (fallback to hardcoded data)")


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection pool"""
    logger.info("🛑 Shutting down...")
    close_db()


# =====================================================
# ROUTES
# =====================================================

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Job Mining API with PostgreSQL",
        "version": "2.0",
        "database": "connected" if db_config._pool else "disconnected",
        "endpoints": {
            "dashboard_map": "/dashboard/map",
            "geo_heatmap": "/api/dashboard/geo-heatmap",
            "ingest_data": "/api/data/ingest",
            "docs": "/docs"
        }
    }


@app.get("/dashboard/map")
async def dashboard_map():
    """Serve dashboard map HTML"""
    try:
        with open("static/dashboard_map.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(404, "Dashboard map not found")


@app.get("/api/dashboard/geo-heatmap", response_model=GeoHeatmapResponse)
def get_geo_heatmap(year: Optional[int] = None, role: Optional[str] = None):
    """
    Get geo-heatmap data with filters.

    PRODUCTION VERSION: Loads data from PostgreSQL using stored function.
    FALLBACK: Returns hardcoded data if DB not available.
    """
    try:
        # Try database query
        locations_query = "SELECT * FROM get_geo_heatmap(%s, %s)"
        locations_data = db_config.execute_query(locations_query, (year, role))

        # Convert to response model
        locations = [
            LocationResponse(
                location=row['location'],
                lat=float(row['lat']) if row['lat'] else None,
                lon=float(row['lon']) if row['lon'] else None,
                country=row['country'],
                count=row['count'],
                color=row['color']
            )
            for row in locations_data
        ]

        # Get competences if role is specified
        competences = []
        if role:
            skills_query = "SELECT * FROM get_top_skills(%s, %s, 10)"
            skills_data = db_config.execute_query(skills_query, (role, year))
            competences = [
                SkillResponse(skill=row['skill'], count=row['count'])
                for row in skills_data
            ]

        logger.info(f"✅ Loaded {len(locations)} locations, {len(competences)} skills from DB")

        return GeoHeatmapResponse(locations=locations, competences=competences)

    except Exception as e:
        logger.warning(f"⚠️ Database query failed: {e}. Using fallback data.")
        # Fallback to hardcoded data (from original main.py)
        return get_hardcoded_heatmap(year, role)


def get_hardcoded_heatmap(year: Optional[int] = None, role: Optional[str] = None):
    """Fallback: Hardcoded data (original implementation)"""
    base_locations = [
        {"location": "Remote", "lat": None, "lon": None, "country": "REMOTE", "count": 3200, "color": "#3498db"},
        {"location": "Berlin", "lat": 52.5200, "lon": 13.4050, "country": "DE", "count": 2100, "color": "#e74c3c"},
        {"location": "München", "lat": 48.1351, "lon": 11.5820, "country": "DE", "count": 1850, "color": "#e67e22"},
        {"location": "Hamburg", "lat": 53.5511, "lon": 9.9937, "country": "DE", "count": 980, "color": "#f39c12"},
    ]

    # Apply filters (simplified)
    year_factor = 1.0 if not year else (0.4 + (year - 2020) * 0.12)
    role_factor = 1.0 if not role else 0.6

    locations = [
        LocationResponse(**{**loc, "count": int(loc["count"] * year_factor * role_factor)})
        for loc in base_locations
    ]

    competences = [
        SkillResponse(skill="Python", count=int(1850 * year_factor)),
        SkillResponse(skill="Docker", count=int(1320 * year_factor)),
    ] if role else []

    return GeoHeatmapResponse(locations=locations, competences=competences)


@app.post("/api/data/ingest")
def ingest_job_data(jobs: List[JobInput]):
    """
    Ingest job data from external sources (Python, Kotlin, etc.)

    Example:
        POST /api/data/ingest
        Body: [{"title": "...", "role": "...", "city": "...", ...}]
    """
    try:
        ingested_count = 0

        for job in jobs:
            # 1. Upsert Location
            location_query = """
                INSERT INTO locations (city, country, latitude, longitude)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (city, country) DO UPDATE SET
                    latitude = COALESCE(EXCLUDED.latitude, locations.latitude),
                    longitude = COALESCE(EXCLUDED.longitude, locations.longitude)
                RETURNING id
            """
            location_result = db_config.execute_insert(
                location_query,
                (job.city, job.country, job.latitude, job.longitude)
            )
            location_id = location_result['id'] if location_result else None

            # 2. Insert Job
            job_query = """
                INSERT INTO jobs (title, role, description, location_id, posted_at, source)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """
            job_result = db_config.execute_insert(
                job_query,
                (job.title, job.role, job.description, location_id, job.posted_at, job.source)
            )
            job_id = job_result['id'] if job_result else None

            # 3. Insert Skills
            if job_id and job.skills:
                for skill_name in job.skills:
                    # Upsert Skill
                    skill_query = """
                        INSERT INTO skills (name, is_digital)
                        VALUES (%s, TRUE)
                        ON CONFLICT (name) DO NOTHING
                        RETURNING id
                    """
                    skill_result = db_config.execute_insert(skill_query, (skill_name,))

                    # If skill already exists, get its ID
                    if not skill_result:
                        skill_id_query = "SELECT id FROM skills WHERE name = %s"
                        skill_id_result = db_config.execute_query(skill_id_query, (skill_name,))
                        skill_id = skill_id_result[0]['id'] if skill_id_result else None
                    else:
                        skill_id = skill_result['id']

                    # Link Job <-> Skill
                    if skill_id:
                        job_skill_query = """
                            INSERT INTO job_skills (job_id, skill_id, confidence)
                            VALUES (%s, %s, 0.95)
                            ON CONFLICT DO NOTHING
                        """
                        db_config.execute_insert(job_skill_query, (job_id, skill_id))

            ingested_count += 1

        logger.info(f"✅ Ingested {ingested_count} jobs from external source")

        return {
            "status": "success",
            "count": ingested_count,
            "message": f"Successfully ingested {ingested_count} jobs"
        }

    except Exception as e:
        logger.error(f"❌ Failed to ingest data: {e}")
        raise HTTPException(500, f"Failed to ingest data: {str(e)}")


@app.get("/api/stats")
def get_stats():
    """Get database statistics"""
    try:
        stats_query = """
            SELECT
                (SELECT COUNT(*) FROM jobs) as total_jobs,
                (SELECT COUNT(*) FROM locations WHERE city != 'Remote') as total_locations,
                (SELECT COUNT(*) FROM skills) as total_skills,
                (SELECT COUNT(DISTINCT role) FROM jobs) as total_roles
        """
        stats = db_config.execute_query(stats_query)[0]

        return {
            "total_jobs": stats['total_jobs'],
            "total_locations": stats['total_locations'],
            "total_skills": stats['total_skills'],
            "total_roles": stats['total_roles'],
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"❌ Failed to get stats: {e}")
        return {
            "total_jobs": 0,
            "total_locations": 0,
            "total_skills": 0,
            "total_roles": 0,
            "database": "disconnected",
            "error": str(e)
        }


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":
    import uvicorn

    # Check database connection
    try:
        init_db()
        logger.info("✅ Database connection successful")
    except Exception as e:
        logger.warning(f"⚠️ Database connection failed: {e}")
        logger.warning("⚠️ Starting in fallback mode (hardcoded data)")

    # Start server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5000,
        log_level="info"
    )
