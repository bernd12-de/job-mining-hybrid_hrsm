import os
import json
import shutil
from app.infrastructure.repositories.hybrid_competence_repository import HybridCompetenceRepository
from app.domain.models import Competence


def setup_test_domains(tmp_dir):
    d = os.path.join(tmp_dir, 'data', 'job_domains')
    os.makedirs(d, exist_ok=True)
    academia = {
        "domain": "test_academia",
        "level": 5,
        "competences": [{"name": "Quantentheorie", "level": 5}]
    }
    fachbuch = {
        "domain": "test_fachbuch",
        "level": 4,
        "competences": [{"name": "Microservices", "level": 4}]
    }
    with open(os.path.join(d, 'test_academia.json'), 'w', encoding='utf-8') as f:
        json.dump(academia, f, ensure_ascii=False)
    with open(os.path.join(d, 'test_fachbuch.json'), 'w', encoding='utf-8') as f:
        json.dump(fachbuch, f, ensure_ascii=False)
    return d


def test_get_level_priority(tmp_path, monkeypatch):
    root = tmp_path
    # copy an empty data tree
    (root / 'data').mkdir()
    # create job_domains
    jd = setup_test_domains(str(root))

    # monkeypatch cwd path resolution inside repository by setting CWD
    monkeypatch.chdir(str(root))

    repo = HybridCompetenceRepository(rule_client=None)

    # reload local domains and sync sets
    repo._load_local_domains_v2()
    repo._sync_legacy_sets()

    assert repo.get_level('Quantentheorie') == 5
    assert repo.get_level('Microservices') == 4


def test_is_digital_skill_and_esco_index(tmp_path, monkeypatch):
    # Prepare repo with one Competence in _all_competences
    repo = HybridCompetenceRepository(rule_client=None)
    comp = Competence(preferred_label='Jira', esco_uri='http://example/1')
    # attach metadata on object (simulated source)
    setattr(comp, 'is_digital', True)
    setattr(comp, 'level', 2)

    repo._all_competences.append(comp)
    repo._build_esco_index()

    assert repo.is_known('Jira') is True
    assert repo.is_digital_skill('Jira') is True
    assert repo.get_level('Jira') == 2
