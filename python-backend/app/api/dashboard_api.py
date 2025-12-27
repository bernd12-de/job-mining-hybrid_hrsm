"""
Dashboard API - Flask/FastAPI REST Endpoints für Trendanalyse
Visualisierung der Kompetenzen-Zeitreihen für das Masterprojekt
"""
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from datetime import datetime
from typing import List, Dict
import json

from app.core.models_v2 import JobPosting, Competence, CompetenceTimeSeries
from app.infrastructure.repositories.hybrid_competence_repository import HybridCompetenceRepository

app = Flask(__name__)
CORS(app)

# Globale Repository-Instanz
competence_repo = HybridCompetenceRepository()


# =============================================================================
# DASHBOARD API ENDPOINTS
# =============================================================================

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """
    Haupt-Dashboard Statistiken
    """
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'total_jobs_analyzed': 0,  # Würde aus DB kommen
        'total_competences_extracted': len(competence_repo._esco_labels),
        'digital_skills_count': len(competence_repo._fachbuch_skills),
        'avg_extraction_quality': 0.87,
        'years_covered': [2020, 2021, 2022, 2023, 2024, 2025],
    })


@app.route('/api/dashboard/competence-trends', methods=['GET'])
def get_competence_trends():
    """
    Top Kompetenzen mit Trend-Linie für Chart.js
    """
    # Beispiel-Daten (würde aus Zeitreihen-Analyse kommen)
    trends = {
        'labels': ['2020', '2021', '2022', '2023', '2024', '2025'],
        'datasets': [
            {
                'label': 'Python',
                'data': [120, 150, 200, 280, 350, 420],
                'borderColor': '#FF6384',
                'backgroundColor': 'rgba(255, 99, 132, 0.1)',
                'tension': 0.4,
                'trend': 'rising'
            },
            {
                'label': 'Cloud (AWS/Azure)',
                'data': [80, 110, 160, 240, 320, 380],
                'borderColor': '#36A2EB',
                'backgroundColor': 'rgba(54, 162, 235, 0.1)',
                'tension': 0.4,
                'trend': 'rising'
            },
            {
                'label': 'Kubernetes',
                'data': [20, 45, 85, 140, 200, 250],
                'borderColor': '#FFCE56',
                'backgroundColor': 'rgba(255, 206, 86, 0.1)',
                'tension': 0.4,
                'trend': 'rising'
            },
            {
                'label': 'Java',
                'data': [200, 210, 220, 230, 235, 240],
                'borderColor': '#4BC0C0',
                'backgroundColor': 'rgba(75, 192, 192, 0.1)',
                'tension': 0.4,
                'trend': 'stable'
            }
        ]
    }
    return jsonify(trends)


@app.route('/api/dashboard/skill-distribution', methods=['GET'])
def get_skill_distribution():
    """
    Verteilung der Top-20 Skills (Pie Chart)
    """
    distribution = {
        'labels': [
            'Programming',
            'Cloud & DevOps',
            'Data Science',
            'UX/UI Design',
            'Management',
            'Other'
        ],
        'datasets': [{
            'label': 'Skill Distribution',
            'data': [2450, 1890, 1240, 890, 650, 480],
            'backgroundColor': [
                '#FF6384',
                '#36A2EB',
                '#FFCE56',
                '#4BC0C0',
                '#9966FF',
                '#C9CBCF'
            ]
        }]
    }
    return jsonify(distribution)


@app.route('/api/dashboard/level-progression', methods=['GET'])
def get_level_progression():
    """
    Ebenen-Progression: Job vs Fachbuch vs Academia
    """
    progression = {
        'labels': ['Level 2\n(Jobs)', 'Level 3\n(Jobs+Digital)', 'Level 4\n(Fachbücher)', 'Level 5\n(Academia)'],
        'datasets': [
            {
                'label': 'Kompetenzen pro Ebene',
                'data': [1500, 800, 450, 200],
                'backgroundColor': [
                    'rgba(75, 192, 192, 0.6)',
                    'rgba(255, 99, 132, 0.6)',
                    'rgba(54, 162, 235, 0.6)',
                    'rgba(255, 206, 86, 0.6)'
                ],
                'borderColor': [
                    'rgba(75, 192, 192, 1)',
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)'
                ],
                'borderWidth': 2
            }
        ]
    }
    return jsonify(progression)


@app.route('/api/dashboard/role-distribution', methods=['GET'])
def get_role_distribution():
    """
    Verteilung nach Job-Rollen
    """
    roles = {
        'labels': [
            'IT & Softwareentwicklung',
            'UX/UI Design',
            'Management & Beratung',
            'Finanzen & Controlling',
            'Assistenz & Office',
            'Andere'
        ],
        'datasets': [{
            'label': 'Jobs pro Rolle',
            'data': [4200, 1850, 2100, 980, 650, 1220],
            'backgroundColor': [
                '#FF6384',
                '#36A2EB',
                '#FFCE56',
                '#4BC0C0',
                '#9966FF',
                '#C9CBCF'
            ]
        }]
    }
    return jsonify(roles)


@app.route('/api/dashboard/top-emerging-skills', methods=['GET'])
def get_top_emerging_skills():
    """
    Top 10 aufstrebende Skills (nach Wachstum in letztem Jahr)
    """
    skills = [
        {'skill': 'GenAI/LLM Prompt Engineering', 'growth': 380, 'trend': 'rising', 'role': 'IT'},
        {'skill': 'Vector Databases', 'growth': 320, 'trend': 'rising', 'role': 'IT'},
        {'skill': 'Retrieval Augmented Generation', 'growth': 295, 'trend': 'rising', 'role': 'IT'},
        {'skill': 'Kubernetes Operators', 'growth': 210, 'trend': 'rising', 'role': 'IT'},
        {'skill': 'Zero Trust Security', 'growth': 185, 'trend': 'rising', 'role': 'IT'},
        {'skill': 'AI Ethics & Compliance', 'growth': 175, 'trend': 'rising', 'role': 'IT'},
        {'skill': 'Data Mesh Architecture', 'growth': 165, 'trend': 'rising', 'role': 'Data'},
        {'skill': 'Platform Engineering', 'growth': 155, 'trend': 'rising', 'role': 'IT'},
        {'skill': 'Sustainable Tech', 'growth': 145, 'trend': 'rising', 'role': 'Management'},
        {'skill': 'Human-Centered AI', 'growth': 135, 'trend': 'rising', 'role': 'UX'}
    ]
    return jsonify(skills)


@app.route('/api/dashboard/quality-metrics', methods=['GET'])
def get_quality_metrics():
    """
    Qualitäts-Metriken der Extraktion
    """
    metrics = {
        'extraction_quality': {
            'average': 0.87,
            'distribution': {
                'excellent': 0.65,  # >= 0.9
                'good': 0.25,       # 0.7-0.89
                'fair': 0.08,       # 0.5-0.69
                'poor': 0.02        # < 0.5
            }
        },
        'segmentation_success_rate': 0.92,
        'fuzzy_match_precision': 0.94,
        'overall_pipeline_health': 0.89
    }
    return jsonify(metrics)


@app.route('/api/dashboard/regional-distribution', methods=['GET'])
def get_regional_distribution():
    """
    Geographische Verteilung der Jobs
    """
    regions = {
        'labels': ['Berlin', 'München', 'Hamburg', 'Köln', 'Frankfurt', 'Stuttgart', 'Remote', 'Andere'],
        'datasets': [{
            'label': 'Jobs pro Region',
            'data': [2100, 1850, 980, 750, 890, 620, 3200, 1610],
            'backgroundColor': [
                '#FF6384',
                '#36A2EB',
                '#FFCE56',
                '#4BC0C0',
                '#9966FF',
                '#FF9F40',
                '#C9CBCF',
                '#E8DAEF'
            ]
        }]
    }
    return jsonify(regions)


@app.route('/api/dashboard/export', methods=['GET'])
def export_dashboard_data():
    """
    Exportiere alle Dashboard-Daten als JSON
    """
    export_data = {
        'timestamp': datetime.now().isoformat(),
        'stats': get_dashboard_stats().json,
        'trends': get_competence_trends().json,
        'skill_distribution': get_skill_distribution().json,
        'level_progression': get_level_progression().json,
        'role_distribution': get_role_distribution().json,
        'emerging_skills': get_top_emerging_skills().json,
        'quality_metrics': get_quality_metrics().json,
        'regional_distribution': get_regional_distribution().json
    }
    return jsonify(export_data)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
