# 🧠 Advanced NLP Features

**Status:** 🔵 KONZEPT

## Idee

Fortgeschrittene NLP-Features für bessere Kompetenz-Extraktion.

## Features

### 1. Named Entity Recognition (NER)
- Automatische Erkennung von Skill-Namen
- Unterscheidung zwischen Tools, Methoden, Soft Skills

### 2. Lemmatisierung & Stemming
- Normalisierung von Begriffen (z.B. "programmieren", "Programmierung" → "programm")
- Verbesserte Matching-Qualität

### 3. Semantic Similarity
- Verwendung von Word Embeddings (Word2Vec, fastText)
- Transformer-basierte Modelle (BERT, GPT)
- Ähnlichkeits-Matching statt nur Keyword-Matching

### 4. Context-Aware Extraction
- Berücksichtigung des Kontext um Keywords
- Unterscheidung zwischen "Java programmieren" vs. "Java Insel besuchen"

## Technologien

- **spaCy** - Industrial-strength NLP
- **Transformers** (Hugging Face) - BERT-Modelle
- **sentence-transformers** - Semantic Search
- **flair** - State-of-the-art NER

## Beispiel-Code

Lege hier deine Experimente ab:
- `ner_extractor.py` - Named Entity Recognition
- `semantic_matcher.py` - Semantic Similarity Matching
- `context_analyzer.py` - Kontext-basierte Extraktion

## Performance-Überlegungen

- Transformer-Modelle sind langsam → Caching nötig
- Vortrainierte deutsche Modelle verwenden
- Hybrid-Ansatz: Keyword-Matching + NLP
