"""Validate crawl output and preview ingestion. Sending requires explicit --send.

No target requests are performed. The destination must be a loopback ARGUS API.
Evidence pairs carry stable keys; original observations are preserved in metadata.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from urllib.parse import urlsplit
import requests
from public_transport import public_url


def evidence_rationale(conn):
    parts = ['candidate only; identity unverified', f"basis: {conn.get('basis', '')}"]
    for ev in conn.get('evidence', []):
        parts.append(f"[{ev.get('document')}] {ev.get('quote', '')} ({public_url(ev['url'])})")
    return '\n'.join(parts)


def document_payload(rec):
    url = public_url(rec['url'])
    text = rec.get('full_text') or rec.get('text_excerpt') or ''
    if not isinstance(text, str):raise ValueError('Document text must be a string')
    metadata = {k:v for k,v in rec.items() if k not in ('full_text', 'text_excerpt')}
    metadata['url'] = url
    return {'sourceType':'web','identifier':url,'url':url,
            'documentType':'pdf' if rec.get('mime_type')=='application/pdf' or urlsplit(url).path.lower().endswith(('.pdf','/pdf')) else 'html',
            'metadata':json.dumps(metadata,ensure_ascii=False,allow_nan=False), 'extractedText':text}


def connection_payload(conn):
    a,b=sorted([conn['document_a'],conn['document_b']])
    if not a or not b or a==b:raise ValueError('Distinct source documents required')
    evidence=conn.get('evidence') or []
    if {e.get('document') for e in evidence}!={a,b}:raise ValueError('Both document evidence references required')
    for e in evidence:
        public_url(e['url'])
        if not e.get('quote') or not e.get('matched_text'):raise ValueError('Evidence quotation and matched text required')
        if e['matched_text'].casefold() not in e['quote'].casefold():raise ValueError('Matched text absent from quotation')
    score=float(conn['confidence'])
    if not math.isfinite(score) or not 0 <= score <= 1:raise ValueError('Invalid score')
    key=hashlib.sha256(json.dumps([a,b,conn['entity_type'],conn['entity'].casefold()],ensure_ascii=False).encode()).hexdigest()
    return {'entityA':a,'entityB':b,'confidence':score,'rationale':evidence_rationale(conn),
            'sourceUrl':public_url(evidence[0]['url']),'linkType':'document_co-occurrence',
            'evidenceKey':key,'metadataEvidence':json.dumps({**conn,'identity_verified':False},ensure_ascii=False,allow_nan=False)}


def ingest(crawl,api='http://localhost:8080',timeout=30,*,session=None,dry_run=True):
    parsed=urlsplit(api)
    if parsed.scheme not in ('http','https') or parsed.hostname not in ('localhost','127.0.0.1','::1') or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in ('','/'):
        raise ValueError('Ingestion destination must be a loopback ARGUS API origin')
    stats={'documents':0,'document_errors':[],'links':0,'link_errors':[],'dry_run':dry_run,'payloads':[]}
    own=session is None;session=session or requests.Session()
    successful=set();seen_documents=set();seen_links=set()
    def send(path,payload):
        if dry_run:
            stats['payloads'].append({'path':path,'payload':payload});return
        response=session.post(api.rstrip('/')+path,json=payload,timeout=timeout,allow_redirects=False)
        if not 200 <= response.status_code < 300:raise ValueError(f'HTTP {response.status_code}')
    try:
        for index,rec in enumerate(crawl.get('records',[])):
            try:
                payload=document_payload(rec)
                doc_id=rec['doc_id']
                identity=(doc_id,payload['identifier'])
                if identity in seen_documents:continue
                send('/api/documents',payload);seen_documents.add(identity);successful.add(doc_id);stats['documents']+=1
            except (KeyError,TypeError,ValueError,requests.RequestException) as exc:
                stats['document_errors'].append({'index':index,'error_type':type(exc).__name__})
        for index,conn in enumerate(crawl.get('connections',[])):
            try:
                if conn.get('document_a') not in successful or conn.get('document_b') not in successful:
                    raise ValueError('Source document ingestion incomplete')
                payload=connection_payload(conn)
                if payload['evidenceKey'] in seen_links:continue
                send('/api/links',payload);seen_links.add(payload['evidenceKey']);stats['links']+=1
            except (KeyError,TypeError,ValueError,requests.RequestException) as exc:
                stats['link_errors'].append({'index':index,'error_type':type(exc).__name__})
    finally:
        if own:session.close()
    return stats


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('crawl_json');ap.add_argument('--api',default='http://localhost:8080')
    ap.add_argument('--send',action='store_true',help='Send to local API after reviewing dry-run output')
    args=ap.parse_args()
    with open(args.crawl_json,encoding='utf-8') as f:crawl=json.load(f)
    stats=ingest(crawl,args.api,dry_run=not args.send)
    print(json.dumps(stats,indent=2,ensure_ascii=False))
    return int(bool(stats['document_errors'] or stats['link_errors']))

if __name__=='__main__':raise SystemExit(main())
