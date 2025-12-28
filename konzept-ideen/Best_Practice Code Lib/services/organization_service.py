from __future__ import annotations
from datetime import datetime
from models.job_ad import JobAd, Organization
from services.organization_extractor import (
    extract_company_name, extract_location, extract_posting_date, extract_branch
)

class OrganizationEnrichmentService:
    def enrich(self, job: JobAd) -> JobAd:
        text = job.cleaned_text or job.raw_text or ""
        company = extract_company_name(text)
        if company:
            job.organization = job.organization or Organization(name=company, branch="Unknown")
            job.organization.name = company
            job.organization.branch = extract_branch(company)

        loc = extract_location(text)
        if loc:
            job.location = loc

        dt = extract_posting_date(text)
        if dt:
            job.posting_date = datetime(dt.year, dt.month, dt.day)

        return job
