# infrastructure/storage/job_repository.py

from typing import List, Dict, Optional
from core.entities.job_posting import JobPosting, Competence
from infrastructure.storage.db_service import DBJob, DBCompetence, Session, joinedload

class JobRepository:
    """
    Repository-Klasse zur Abstraktion des Datenbankzugriffs.
    Sie empfängt die SQLAlchemy Session über Dependency Injection (DI).
    """

    def __init__(self, session: Session):
        self.session = session

    # ✅ KORREKT: In die Klasse eingerückt
    def save_job_posting(self, job: JobPosting):
        """
        Speichert oder aktualisiert ein JobPosting (Idempotenz-Logik).
        """
        # 1. Prüfen, ob der Job bereits existiert (UPSERT-Logik)
        existing_job = self.session.query(DBJob).filter(DBJob.source_id == job.source_id).first()

        if existing_job:
            # Löschen des alten Jobs
            self.session.delete(existing_job)

            # WICHTIG: Commit des Löschvorgangs, damit der nächste INSERT funktioniert!
            self.session.commit()

            print(f"[Repo] Bestehender Job '{job.title}' (ID: {job.source_id}) aktualisiert.")

        # 2. Neuen Job einfügen
        db_job = DBJob(
            source_id=job.source_id,
            title=job.title,
            company=job.company,
            region=job.region,
            year=job.year,
            source_path=job.source_path,
            raw_text=job.raw_text
        )

        for comp in job.competences:
            db_competence = DBCompetence(
                original_skill=comp.original_skill, esco_match=comp.esco_match,
                score=comp.score, category=comp.category, context_section=comp.context_section
            )
            db_job.competences.append(db_competence)

        self.session.add(db_job)
        self.session.commit() # Finaler Commit für den neuen Job
        print(f"[Repo] Erfolgreich Job '{job.title}' (ID: {job.source_id}) gespeichert.")

    # ✅ KORREKT: In die Klasse eingerückt
    def fetch_all_job_postings(self) -> List[Dict]:
        """Ruft alle Jobs mit zugehörigen Kompetenzen aus der Datenbank ab."""

        jobs = (
            self.session.query(DBJob)
            .options(joinedload(DBJob.competences))
            .all()
        )

        result_list = []

        for db_job in jobs:
            # Serialisierung der Job-Felder
            job_dict = {
                "source_id": db_job.source_id,
                "title": db_job.title,
                "company": db_job.company,
                "region": db_job.region,
                "year": db_job.year,
                "source_path": db_job.source_path,
                "raw_text": db_job.raw_text,
                "competences": []
            }

            for db_comp in db_job.competences:
                job_dict["competences"].append({
                    "original_skill": db_comp.original_skill,
                    "esco_match": db_comp.esco_match,
                    "score": db_comp.score,
                    "category": db_comp.category,
                    "context_section": db_comp.context_section,
                })

            result_list.append(job_dict)

        return result_list
