"""Run the packaged DOCX renderer; isolated Linux LO supplies only conversion.
The Windows runtime bundles Poppler/Python, but no native LibreOffice.
"""
import importlib.util,os,subprocess,sys
from pathlib import Path
SKILL=Path('C:/Users/LOQ/.codex/plugins/cache/openai-primary-runtime/documents/26.1105.12137/skills/documents')
spec=importlib.util.spec_from_file_location('packaged_docx_renderer',SKILL/'render_docx.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
docker='C:/Users/LOQ/AppData/Local/Programs/DockerDesktop/resources/bin/docker.exe'
def convert(doc_path,user_profile,convert_tmp_dir,stem,verbose):
    src=Path(doc_path).resolve(); dest=Path(convert_tmp_dir).resolve()
    cmd=[docker,'run','--rm','-v',str(src.parent)+':/input:ro','-v',str(dest)+':/output',
         'mpl-docx-render:local','-env:UserInstallation=file:///tmp/lo-profile','--headless',
         '--convert-to','pdf','--outdir','/output','/input/'+src.name]
    r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=240)
    pdf=dest/(src.stem+'.pdf')
    return (str(pdf) if pdf.exists() else ''),r.stdout+r.stderr
mod.convert_to_pdf=convert
os.environ['PATH']='C:/Users/LOQ/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin'+os.pathsep+os.environ['PATH']
mod.main()
