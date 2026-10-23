import json
import sqlite3
from hashlib import sha256
import pytest
import rfc8785
from api import research_capture as source, research_records as exports
from api.research_record_verify import verify_package


def test_review_keeps_exact_bundle_draft_text_and_declares_missing_context(tmp_path,monkeypatch):
    monkeypatch.setenv('DATABASE_PATH',str(tmp_path/'briefing.db'))
    monkeypatch.setenv('SUMMARY_BUILDER_DATA_ROOT',str(tmp_path/'synopsis'))
    bundle={'bundle_id':'ssb-one','sources':[{'application_slug':'gom','context_id':'context-one'}], 'fact_ledger':[{'kp':7.3}], 'runtime':{'mode':'replay'}}
    bundle['integrity']={'sha256':sha256(rfc8785.dumps({k:bundle[k] for k in ('fact_ledger','sources')})).hexdigest()}
    root=tmp_path/'synopsis';(root/'source-bundles').mkdir(parents=True);(root/'drafts').mkdir()
    path=root/'source-bundles/ssb-one.json';path.write_text(json.dumps(bundle),encoding='utf-8')
    (root/'drafts/swd-one.json').write_text(json.dumps({'source_bundle':{'bundle_id':'ssb-one'}}),encoding='utf-8')
    text='Retained Synopsis\nKp 7.3\n'
    review={'review_id':'review-one','source_bundle_id':'ssb-one','source_draft_id':'swd-one','product_text':text,'sha256':sha256(text.encode()).hexdigest(),'runtime':{'mode':'replay'},'evidence_refs':[{'kind':'synopsis_source_bundle','record_id':'ssb-one','sha256':bundle['integrity']['sha256']}]}
    with sqlite3.connect(source.database()) as db:
        db.execute('CREATE TABLE synopsis_reviews(id TEXT,scope TEXT,version INTEGER,payload TEXT)')
        db.execute('INSERT INTO synopsis_reviews VALUES(?,?,?,?)',('review-one','replay',2,json.dumps(review)))
    before=source.database().read_bytes()
    item=next(source.records('reviews'));manifest,files=exports.build(source.APPLICATION,item)
    assert manifest['runtime']=={'mode':'replay'} and files['files/synopsis.txt']==text.encode()
    assert json.loads(files['files/source-bundle.json'])==bundle
    assert any(e['availability']=='unavailable' for e in manifest['assets'])
    archive=tmp_path/'selected.zip';archive.write_bytes(exports.package(manifest,files));verify_package(archive)
    assert source.database().read_bytes()==before
    bundle['fact_ledger'][0]['kp']=0;path.write_text(json.dumps(bundle),encoding='utf-8')
    with pytest.raises(ValueError,match='checksum'):exports.build(source.APPLICATION,item)


def test_missing_storage_does_not_create_it_and_receipts_do_not_generate_reviews(tmp_path,monkeypatch):
    monkeypatch.setenv('DATABASE_PATH',str(tmp_path/'missing/new.db'))
    assert list(source.records('email-documents'))==[] and not source.database().parent.exists()
    with sqlite3.connect(tmp_path/'existing.db') as db:
        db.execute('CREATE TABLE synopsis_receipts(review_id TEXT,payload TEXT)')
        db.execute('INSERT INTO synopsis_receipts VALUES(?,?)',('missing-review',json.dumps({'candidate_id':'candidate'})))
    monkeypatch.setenv('DATABASE_PATH',str(tmp_path/'existing.db'))
    manifest,_=exports.build(source.APPLICATION,next(source.records('receipts')))
    assert manifest['assets'][1]['availability']=='unavailable'
