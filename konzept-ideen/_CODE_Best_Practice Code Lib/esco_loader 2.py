import zipfile, csv, io

def load_esco(zip_path):
    skills = []
    with zipfile.ZipFile(zip_path, 'r') as z:
        for name in z.namelist():
            if 'skill' in name and name.endswith('.csv'):
                with z.open(name) as f:
                    text = io.TextIOWrapper(f, encoding='utf-8')
                    reader = csv.DictReader(text)
                    for row in reader:
                        skills.append({'label': row.get('preferredLabel',''), 'uri': row.get('uri','')})
    return skills
