"""
Pipeline Utility für Batch-Verarbeitung
Basiert auf: Best_Practice Code Lib/pipeline.py

Features:
- Records flatten (Batch-Struktur auflösen)
- JSONL-Export (zeilenweise JSON für Streaming)
- ESCO-Alias optional enrichment
- Statistik & Reporting
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Iterator
from dataclasses import dataclass, asdict


@dataclass
class ExportStats:
    """Statistik für Export-Run"""
    total_records: int
    exported: int
    with_competences: int
    with_esco: int
    output_path: str


def _flatten_records(obj: Any) -> Iterator[Dict]:
    """
    Rekursiv flattened Batch-Strukturen.
    
    Falls obj = {"_batch": True, "records": [...]}, yield each record.
    Sonst yield obj direkt.
    """
    if isinstance(obj, dict) and obj.get("_batch"):
        for r in obj.get("records", []):
            yield from _flatten_records(r)
    else:
        yield obj


def flatten_batch_records(records: List[Dict]) -> List[Dict]:
    """
    Konvertiert eine Liste von möglicherweise verschachtelten Records
    in eine flache Liste von Job-Records.
    
    Args:
        records: Liste von Records (können Batch-Struktur enthalten)
    
    Returns:
        Flattened Liste von Job-Records
    """
    result = []
    for rec in records:
        result.extend(_flatten_records(rec))
    return result


def save_to_jsonl(
    records: List[Dict],
    output_path: str,
    mode: str = "w",
    include_stats: bool = True
) -> ExportStats:
    """
    Exportiert Records als JSONL (zeilenweise JSON).
    
    Args:
        records: Liste von Records
        output_path: Zieldatei (.jsonl)
        mode: "w" (überschreiben) oder "a" (anhängen)
        include_stats: Statistik-Zeile am Ende
    
    Returns:
        ExportStats mit Metadaten
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    exported = 0
    with_competences = 0
    with_esco = 0
    
    with open(output_path, mode, encoding="utf-8") as f:
        for rec in records:
            # Sicherheitshalber: vermeide Zeilenumbrüche in JSON
            clean_rec = _clean_for_jsonl(rec)
            f.write(json.dumps(clean_rec, ensure_ascii=False) + "\n")
            
            exported += 1
            if rec.get("competences"):
                with_competences += 1
                with_esco += sum(1 for c in rec["competences"] if c.get("esco_uri"))
    
    stats = ExportStats(
        total_records=len(records),
        exported=exported,
        with_competences=with_competences,
        with_esco=with_esco,
        output_path=str(output_path)
    )
    
    return stats


def _clean_for_jsonl(obj: Any) -> Any:
    """
    Bereinigt Objekt für JSONL-Export (entfernt Newlines, begrenzt Größe).
    """
    if isinstance(obj, dict):
        return {k: _clean_for_jsonl(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_clean_for_jsonl(v) for v in obj]
    elif isinstance(obj, str):
        # Ersetze Newlines durch Spaces
        return obj.replace("\n", " ").replace("\r", " ")
    else:
        return obj


def load_esco_alias(path: str = "data/esco_alias.json") -> Dict[str, str]:
    """
    Lädt ESCO-Alias-Map aus JSON.
    Format: {"skill_name_de": "ESCO_URI"}
    
    Args:
        path: Pfad zur esco_alias.json
    
    Returns:
        Dict[str, str] oder {} bei Fehler
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ ESCO-Alias nicht geladen: {e}")
        return {}


def enrich_with_esco(
    records: List[Dict],
    esco_map: Dict[str, str]
) -> List[Dict]:
    """
    Reichert Records mit ESCO-Skills an (optional, best-effort).
    
    Für jedes Record: Durchsuche competences nach Matches in esco_map,
    speichere ESCO-URIs.
    
    Args:
        records: Liste von Job-Records
        esco_map: Dict mit Skill→ESCO-URI Mappings
    
    Returns:
        Angereicherte Records
    """
    if not esco_map:
        return records
    
    # Prepare keyset (lowercase für Case-insensitive Suche)
    esco_lower = {k.lower(): v for k, v in esco_map.items()}
    
    for rec in records:
        competences = rec.get("competences", [])
        for comp in competences:
            # Versuche Original-Name zu matchen
            comp_name = (comp.get("original_term") or comp.get("name") or "").lower()
            if comp_name in esco_lower and not comp.get("esco_uri"):
                comp["esco_uri"] = esco_lower[comp_name]
        
        # Speichere angereicherte competences zurück
        rec["competences"] = competences
    
    return records


def process_and_export_batch(
    records: List[Dict],
    output_jsonl: str,
    esco_map: Optional[Dict[str, str]] = None,
    verbose: bool = True
) -> ExportStats:
    """
    Komplette Pipeline: Flatten → optional ESCO-Enrichment → JSONL-Export
    
    Args:
        records: Input-Records (können Batch-Struktur enthalten)
        output_jsonl: Output-Pfad (.jsonl)
        esco_map: Optional ESCO-Map für Enrichment
        verbose: Drucke Progress
    
    Returns:
        ExportStats
    """
    if verbose:
        print(f"📂 Starten Batch-Export: {len(records)} Records")
    
    # Schritt 1: Flatten
    flat = flatten_batch_records(records)
    if verbose:
        print(f"   ✅ Flattened: {len(flat)} unique records")
    
    # Schritt 2: Optional ESCO-Enrichment
    if esco_map:
        enrich_with_esco(flat, esco_map)
        if verbose:
            print(f"   ✅ ESCO-Enrichment angewendet")
    
    # Schritt 3: JSONL-Export
    stats = save_to_jsonl(flat, output_jsonl)
    
    if verbose:
        print(f"""
╔══════════════════════════════════════════╗
║ ✅ EXPORT ABGESCHLOSSEN                 ║
╠══════════════════════════════════════════╣
║ Output:        {stats.output_path:34} ║
║ Records:       {stats.exported:34} ║
║ Mit Skills:    {stats.with_competences:34} ║
║ Mit ESCO:      {stats.with_esco:34} ║
╚══════════════════════════════════════════╝
        """)
    
    return stats
