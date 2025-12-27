"""
Package Checker und Auto-Installer für Job Mining V2.0
Verhindert Abstürze durch fehlende Pakete im Produktivbetrieb
"""
import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PackageChecker")

# Kritische Pakete, die das System benötigt
REQUIRED_PACKAGES = {
    'fastapi': 'fastapi',
    'uvicorn': 'uvicorn',
    'spacy': 'spacy',
    'pydantic': 'pydantic',
    'requests': 'requests',
    'python-multipart': 'python-multipart',
    'pandas': 'pandas',
    'numpy': 'numpy',
    'streamlit': 'streamlit',
    'plotly': 'plotly',
}

OPTIONAL_PACKAGES = {
    'PyPDF2': 'PyPDF2',
    'python-docx': 'python-docx',
    'beautifulsoup4': 'beautifulsoup4',
    'lxml': 'lxml',
    'reportlab': 'reportlab',
}

def check_package(package_name):
    """Prüft ob ein Paket importierbar ist"""
    try:
        __import__(package_name.replace('-', '_'))
        return True
    except ImportError:
        return False

def install_package(package_name, pip_name=None):
    """Installiert ein fehlendes Paket"""
    pip_name = pip_name or package_name
    try:
        logger.info(f"📦 Installiere {pip_name}...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-q", pip_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        logger.info(f"✅ {pip_name} erfolgreich installiert")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Fehler beim Installieren von {pip_name}: {e}")
        return False

def check_and_install_packages(required=True):
    """Prüft und installiert fehlende Pakete"""
    packages = REQUIRED_PACKAGES if required else OPTIONAL_PACKAGES
    missing = []
    
    logger.info(f"🔍 Prüfe {'kritische' if required else 'optionale'} Pakete...")
    
    for import_name, pip_name in packages.items():
        if not check_package(import_name):
            missing.append((import_name, pip_name))
    
    if missing:
        logger.warning(f"⚠️  {len(missing)} Paket(e) fehlen: {[p[0] for p in missing]}")
        
        for import_name, pip_name in missing:
            if required:
                logger.info(f"   Installiere kritisches Paket: {pip_name}")
                if not install_package(import_name, pip_name):
                    if required:
                        logger.error(f"❌ Kritisches Paket {pip_name} konnte nicht installiert werden!")
                        return False
            else:
                logger.info(f"   Versuche optionales Paket zu installieren: {pip_name}")
                install_package(import_name, pip_name)
    else:
        logger.info(f"✅ Alle {'kritischen' if required else 'optionalen'} Pakete vorhanden")
    
    return True

def verify_system():
    """Verifiziert die komplette System-Installation"""
    logger.info("🚀 Starte System-Verifikation...")
    
    # Kritische Pakete MÜSSEN vorhanden sein
    if not check_and_install_packages(required=True):
        logger.error("❌ System kann nicht gestartet werden - kritische Pakete fehlen!")
        sys.exit(1)
    
    # Optionale Pakete werden best-effort installiert
    check_and_install_packages(required=False)
    
    # Spezielle spaCy-Modell-Prüfung
    try:
        import spacy
        try:
            spacy.load('de_core_news_md')
            logger.info("✅ spaCy Modell 'de_core_news_md' verfügbar")
        except OSError:
            logger.warning("⚠️  spaCy Modell 'de_core_news_md' nicht gefunden")
            try:
                spacy.load('de_core_news_sm')
                logger.info("✅ Fallback auf 'de_core_news_sm'")
            except OSError:
                logger.warning("⚠️  Kein deutsches spaCy-Modell gefunden")
                logger.info("   NLP-Funktionen könnten eingeschränkt sein")
    except Exception as e:
        logger.warning(f"⚠️  Konnte spaCy-Modell nicht prüfen: {e}")
    
    logger.info("✅ System-Verifikation abgeschlossen")
    return True

if __name__ == "__main__":
    verify_system()
