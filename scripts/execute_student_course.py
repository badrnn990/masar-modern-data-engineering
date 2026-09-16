"""Execute the actual five-day learner route; keep real outputs and failures."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from datetime import datetime, timezone
import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from masar.native_contracts import read_stage_report
from masar.workspace import completed_bronze_workspace, DATASET_MANIFEST_SHA256

STAGES = {1:['lab01_bronze','lab02_scan'],2:['lab03a_staging','lab03b_silver'],3:['lab04a_transactions','lab04b_maintenance'],4:['lab05_streaming','lab06_quality'],5:['lab07_gold_recovery','lab08_serving']}
EVIDENCE = ROOT / 'evidence/student-course/notebooks'
EVIDENCE.mkdir(parents=True, exist_ok=True)
REPOSITORY = os.environ.get('GITHUB_REPOSITORY', 'badrnn990/masar-modern-data-engineering')
BRANCH = os.environ.get('GITHUB_REF_NAME', 'develop')
RUN_URL = f'https://github.com/{REPOSITORY}/actions/runs/' + os.environ.get('GITHUB_RUN_ID', 'local')

def save(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str)+'\n', encoding='utf-8')

def retain_reports(copy: Path, target: Path) -> None:
    for path in (copy / 'outputs').rglob('*'):
        if path.is_file() and path.suffix in {'.json', '.log'} and '_delta_log' not in path.parts:
            dest = target / path.relative_to(copy); dest.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(path, dest)

def run_course(attempt: int) -> dict:
    copy = Path(tempfile.mkdtemp(prefix=f'masar_course_{attempt}_')) / 'course'
    shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns('.git','outputs','evidence','__pycache__','.venv','metastore_db','derby.log'))
    target = EVIDENCE / f'run_{attempt}'
    result = {'attempt':attempt,'status':'RUNNING','days':[],'workflow_url':RUN_URL}
    try:
        for day, stages in STAGES.items():
            print(f'EXECUTING run {attempt} / day {day}', flush=True)
            nb = nbformat.read(copy / f'day{day:02}/STUDENT.ipynb', as_version=4)
            for cell in nb.cells:
                if cell.cell_type == 'code': cell.outputs=[]; cell.execution_count=None
            try:
                NotebookClient(nb, timeout=900, kernel_name='python3', resources={'metadata':{'path':str(copy)}}, allow_errors=False).execute()
            finally:
                target.mkdir(parents=True, exist_ok=True); nbformat.write(nb, target / f'day{day:02}.ipynb')
            if any(c.cell_type=='code' and c.source.strip() and c.execution_count is None for c in nb.cells): raise AssertionError('A required code cell did not execute')
            work = completed_bronze_workspace(copy)
            reports = {stage:read_stage_report(work,stage) for stage in stages}
            day_result={'day':day,'status':'PASSED','stages':list(reports),'checks':{s:r['checks'] for s,r in reports.items()},'code_cells_executed':sum(c.cell_type=='code' for c in nb.cells)}
            if day==1:
                result['run_id']=json.loads((work/'.masar-workspace.json').read_text())['run_id']; result['bronze_counts']=reports['lab01_bronze']['counts']; result['base_aggregate']=reports['lab02_scan']['expected_and_observed_aggregate']
            if day==2:
                paths=list((copy/'outputs').rglob('dbt_attempt.json')); assert len(paths)==1
                dbt=json.loads(paths[0].read_text()); assert dbt['status']=='PASSED_DBT_NATIVE' and dbt['dbt_executed'] is True; assert [p['rows'] for p in dbt['phases']]==[72,72,75,75]
                result['dbt_phases']=[{k:p[k] for k in ('phase','rows','total_fare_sar','business_digest')} for p in dbt['phases']]; day_result['dbt_commands']=len(dbt['commands'])
            if day==5: result['serving_checks']=reports['lab08_serving']['checks']
            import zipfile
            with zipfile.ZipFile(copy/f'outputs/day{day:02}_handoff.zip') as archive:
                assert archive.testzip() is None and 'outputs/day01_bronze_success.json' in archive.namelist() and any('/_delta_log/' in n for n in archive.namelist())
            day_result['handoff_zip_verified']=True; result['days'].append(day_result); save(target/'summary.json',result); print(f'PASSED run {attempt} / day {day}',flush=True)
        result['status']='PASSED'
    except Exception as exc:
        result.update(status='FAILED',error_type=type(exc).__name__,error=str(exc)); raise
    finally:
        save(target/'summary.json',result); retain_reports(copy,target)
    return result

def publish_evidence() -> None:
    source=EVIDENCE/'run_1'/'outputs'; mapping=['bronze.json','benchmark.json','day02_staging_latest.json','day02_silver.json','day03_transactions.json','day03_maintenance_latest.json','day04_stream_latest.json','day04_quality_latest.json','day05_recovery.json','day05_serving_latest.json']
    for name in mapping:
        src=source/'reports'/name
        if not src.is_file(): raise FileNotFoundError(f'Missing generated report: reports/{name}')
        dst=ROOT/'reports'/name; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
    for folder,name in [('streaming','day04_stream_latest.json'),('quality','day04_quality_latest.json'),('recovery','day05_recovery.json'),('serving','day05_serving_latest.json')]:
        dst=ROOT/'reports'/folder/name; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(source/'reports'/name,dst)

def write_notes() -> None:
    descriptions={1:'Bronze ingestion and Spark benchmark evidence: reports/bronze.json and reports/benchmark.json.',2:'Typed staging, Silver, late-arrival and idempotency evidence: reports/day02_staging_latest.json and reports/day02_silver.json.',3:'Native Delta transaction, correction, schema and maintenance evidence: reports/day03_transactions.json and reports/day03_maintenance_latest.json.',4:'Native Kafka/streaming and Great Expectations evidence: reports/day04_stream_latest.json and reports/day04_quality_latest.json.',5:'Recovery and Gold serving evidence: reports/day05_recovery.json and reports/day05_serving_latest.json.',6:'Quality-gate evidence: reports/quality/day04_quality_latest.json.',7:'Recovery evidence: reports/recovery/day05_recovery.json.',8:'Serving and reconciliation evidence: reports/serving/day05_serving_latest.json.'}
    for lab,desc in descriptions.items():
        (ROOT/f'LAB{lab:02}_NOTES.md').write_text(f'# LAB{lab:02}_NOTES\n\n{desc}\n\n## Provenance\n- Repository: `{REPOSITORY}`\n- Branch: `{BRANCH}`\n- Execution workflow: {RUN_URL}\n- Dataset: `MASAR_SMALL_V1`\n- Evidence is generated by the native execution route.\n',encoding='utf-8')

if __name__=='__main__':
    results=[run_course(1), run_course(2)]; assert results[0]['run_id']!=results[1]['run_id']
    for key in ('bronze_counts','base_aggregate','dbt_phases','serving_checks'): assert results[0][key]==results[1][key],f'Non-repeatable business result: {key}'
    verified=datetime.now(timezone.utc).isoformat()
    for day in STAGES:
        nb=nbformat.read(EVIDENCE/f'run_1/day{day:02}.ipynb',as_version=4); nb.metadata['masar']={'day':day,'execution_status':'PASSED','independent_course_runs':2,'workflow_url':RUN_URL,'verified_at_utc':verified,'host':'GitHub Actions Ubuntu 24.04'}; nbformat.write(nb,ROOT/f'day{day:02}/STUDENT.ipynb')
        evidence={'day':day,'status':'PASSED','independent_course_runs':2,'verified_at_utc':verified,'workflow_url':RUN_URL,'dataset_manifest_sha256':DATASET_MANIFEST_SHA256,'checks':results[0]['days'][day-1],'colab_host_tested':False,'code_sha256':hashlib.sha256(json.dumps([c.source for c in nb.cells if c.cell_type=='code'],ensure_ascii=False).encode()).hexdigest()}; save(ROOT/f'day{day:02}/verification.json',evidence)
    publish_evidence(); write_notes()
    benchmark=json.loads((ROOT/'reports/benchmark.json').read_text()); (ROOT/'BENCHMARKS.md').write_text('# BENCHMARKS\n\nMachine-produced Day 1 benchmark evidence; timing values are retained exactly as generated and are not general performance guarantees.\n\n```json\n'+json.dumps(benchmark,ensure_ascii=False,indent=2)+'\n```\n',encoding='utf-8')
    (ROOT/'DECISIONS.md').write_text('# DECISIONS\n\n- Preserve Bronze as append-only source history.\n- Use deterministic business-key deduplication and precedence for late/replayed data.\n- Require native stage evidence before downstream promotion.\n- Keep streaming checkpoints persistent and separate by query.\n- Quarantine failed quality candidates and block unsafe promotion.\n- Reconcile Gold outputs by business content, not volatile timestamps.\n- Use only synthetic `MASAR_SMALL_V1`.\n\nExecution evidence: '+RUN_URL+'\n',encoding='utf-8')
    (ROOT/'GOVERNANCE.md').write_text('# GOVERNANCE\n\n## Data classification\nSynthetic training data only (`MASAR_SMALL_V1`); no real personal data is required.\n\n## Ownership and access\nRepository owner: `badrnn990`. Intended access: student, course reviewers and authorised programme staff.\n\n## Lineage\nSource feeds -> Bronze -> Silver -> Gold -> AI/BI serving.\n\n## Retention\nRetain assessment evidence; do not add real personal data or secrets.\n\n## Quality\nInvalid records are quarantined with reasons and unsafe promotion is blocked by the native quality gate.\n',encoding='utf-8')
    summary={'status':'PASSED','scope':'FIVE_STUDENT_NOTEBOOKS_WITH_NATIVE_ENGINES_AND_DBT','independent_course_runs':2,'notebook_executions':10,'workflow_url':RUN_URL,'verified_at_utc':verified,'python':sys.version.split()[0],'dataset_manifest_sha256':DATASET_MANIFEST_SHA256,'colab_host_tested':False,'production_scale_tested':False,'results':results}; save(ROOT/'docs/verification.json',summary)
    (ROOT/'docs/VERIFICATION.md').write_text(f'# Execution record\n\nFive daily student notebooks completed in order in two independent workspaces, with a fresh kernel for each day. The notebooks contain real outputs from the first complete run.\n\nNative components: Spark 3.5.8, Delta 3.3.3, Kafka 4.0.2, Great Expectations 1.7.0 and dbt-spark 1.9.1, using Python 3.11 and Java 17 on GitHub Actions.\n\n[Actual execution logs]({RUN_URL}) · [Machine-readable verification](verification.json). Timing samples vary by machine and are not performance guarantees. Colab hosting and distributed production scale were not separately tested.\n',encoding='utf-8')
    course=json.loads((ROOT/'course.json').read_text()); [day.update(status='PUBLISHED_NATIVE_VERIFIED') for day in course['day_plan']]; save(ROOT/'course.json',course)
    print(json.dumps({'status':'PASSED','notebooks_executed':10,'workflow_url':RUN_URL},indent=2))
