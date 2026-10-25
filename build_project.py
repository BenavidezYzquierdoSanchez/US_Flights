"""Regenera y empaqueta una entrega coherente, sin ZIP anidados.
python build_project.py [--browser RUTA_CHROMIUM] [--schemas]
"""
import argparse,hashlib,json,subprocess,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--browser')
parser.add_argument('--schemas',action='store_true')
args=parser.parse_args()
def run(script,*arguments):
    subprocess.run([sys.executable,str(ROOT/script),*arguments],cwd=ROOT,check=True)
run('build_assets.py')
run('build_powerbi.py')
run('tests/verify_project.py',*(['--browser',args.browser] if args.browser else []))
run('tests/audit_powerbi_sync.py')
if args.schemas:run('tests/validate_pbir.py')

excluded_dirs={'__pycache__','.venv','.git','.pbi'}
def deliverable(path):
    return path.is_file() and not (set(path.relative_to(ROOT).parts)&excluded_dirs) and path.suffix.lower() not in ['.zip','.png','.pyc']
files=sorted(f for f in ROOT.rglob('*') if deliverable(f))
manifest={'version':'dashboard_final_2021_2026','paginas':['Panorama','Estacionalidad','Geografía','Aerolíneas','Marco del proyecto','Metodología','Conclusiones'],'source_json_sha256':hashlib.sha256((ROOT/'data/source.json').read_bytes()).hexdigest(),'html_sha256':hashlib.sha256((ROOT/'dashboard_US_Flights.html').read_bytes()).hexdigest(),'resultados':json.loads((ROOT/'docs/test_results.json').read_text(encoding='utf-8')),'powerbi':json.loads((ROOT/'powerbi/revision_dashboard.json').read_text(encoding='utf-8')),'archivos':{str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files if f.name!='release_manifest.json'}}
(ROOT/'release_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))

for folder,target,prefix in [(ROOT,ROOT.parent/'US_Flights_Proyecto_Completo.zip','US_Flights'),(ROOT/'powerbi',ROOT.parent/'US_Flights_PowerBI_Actualizado.zip','PowerBI_US_Flights')]:
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for file in sorted(folder.rglob('*')):
            if deliverable(file):archive.write(file,Path(prefix)/file.relative_to(folder))
    with zipfile.ZipFile(target) as archive:
        if archive.testzip() is not None:raise RuntimeError('Archivo ZIP dañado')
        if any(name.lower().endswith('.zip') for name in archive.namelist()):raise RuntimeError('Se detectó un ZIP anidado')
    print('Entrega verificada:',target.name,target.stat().st_size,'bytes')
