#!/usr/bin/env python3
"""
GSC Data Pull — Brand 9 Signs Search Console API
Part of the PRAGMA Site-Health Operator (Phase 1).

Requires: Google Search Console API enabled for the project + proper OAuth scopes.
Run: python3 pull-gsc.py [--days 28] [--output site-health-gsc.json]

When the API scope is properly granted, this pulls:
  - Performance data (clicks, impressions, CTR, position) for last N days
  - Coverage/index errors
  - Query-level and page-level performance
  - 28-day trend comparison

Current status: API scope not yet granted. See:
  https://console.cloud.google.com/apis/library/searchconsole.googleapis.com
  Service account: hermes-gsc-indexer@empyrean-surge-498212-f6.iam.gserviceaccount.com
"""
import json, sys, time, os
from datetime import datetime, timedelta

# ── Config ────────────────────────────────────────────────────
SITE_URL = "sc-domain:brand9signs.com"  # or "https://brand9signs.com/"
DAYS = 28
OUTPUT = None  # default: print to stdout

# Parse args
for i, a in enumerate(sys.argv[1:]):
    if a == '--days' and i+2 < len(sys.argv):
        DAYS = int(sys.argv[i+2])
    elif a and not a.startswith('--'):
        OUTPUT = a

def main():
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError:
        print("Error: need google-api-python-client + google-auth. Install:")
        print("  pip install google-api-python-client google-auth-httplib2 google-auth")
        sys.exit(1)

    # Try service account first, then fallback to gcloud auth
    creds = None
    sa_path = os.path.expanduser('~/.config/gcloud/application_default_credentials.json')
    
    if os.path.exists(sa_path):
        try:
            creds = service_account.Credentials.from_service_account_file(
                sa_path,
                scopes=['https://www.googleapis.com/auth/webmasters.readonly']
            )
            print("Using service account credentials", file=sys.stderr)
        except Exception as e:
            print(f"SA credentials failed: {e}", file=sys.stderr)

    if not creds:
        import google.auth
        creds, project = google.auth.default(
            scopes=['https://www.googleapis.com/auth/webmasters.readonly']
        )
        print(f"Using default credentials ({project})", file=sys.stderr)

    service = build('searchconsole', 'v1', credentials=creds)
    
    today = datetime.now().strftime('%Y-%m-%d')
    start = (datetime.now() - timedelta(days=DAYS)).strftime('%Y-%m-%d')
    prior_start = (datetime.now() - timedelta(days=DAYS*2)).strftime('%Y-%m-%d')
    
    result = {
        'generated': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'site_url': SITE_URL,
        'period': {'start': start, 'end': today},
        'prior_period': {'start': prior_start, 'end': start},
    }

    # 1. Performance summary
    print(f"Pulling performance: {start} → {today}", file=sys.stderr)
    resp = service.searchanalytics().query(
        siteUrl=SITE_URL,
        body={
            'startDate': start,
            'endDate': today,
            'dimensions': [],
            'rowLimit': 1,
        }
    ).execute()
    
    rows = resp.get('rows', [])
    if rows:
        r = rows[0]
        perf = {'clicks': r.get('clicks', 0), 'impressions': r.get('impressions', 0),
                'ctr': r.get('ctr', 0), 'avg_position': r.get('position', 0)}
    else:
        perf = {'clicks': 0, 'impressions': 0, 'ctr': 0, 'avg_position': 0}
    
    # Prior period for comparison
    resp_prior = service.searchanalytics().query(
        siteUrl=SITE_URL,
        body={
            'startDate': prior_start,
            'endDate': start,
            'dimensions': [],
            'rowLimit': 1,
        }
    ).execute()
    prior_rows = resp_prior.get('rows', [])
    if prior_rows:
        pr = prior_rows[0]
        perf_prior = {'clicks': pr.get('clicks', 0), 'impressions': pr.get('impressions', 0),
                      'ctr': pr.get('ctr', 0), 'avg_position': pr.get('position', 0)}
    else:
        perf_prior = {'clicks': 0, 'impressions': 0, 'ctr': 0, 'avg_position': 0}
    
    result['performance'] = {'current': perf, 'prior_period': perf_prior}
    
    clicks_delta = perf['clicks'] - perf_prior['clicks']
    imps_delta = perf['impressions'] - perf_prior['impressions']
    result['trend'] = {
        'clicks_delta': clicks_delta,
        'clicks_delta_pct': round((clicks_delta / max(perf_prior['clicks'], 1)) * 100, 1),
        'impressions_delta': imps_delta,
        'impressions_delta_pct': round((imps_delta / max(perf_prior['impressions'], 1)) * 100, 1),
    }

    # 2. Top queries
    print("Pulling top queries...", file=sys.stderr)
    qresp = service.searchanalytics().query(
        siteUrl=SITE_URL,
        body={
            'startDate': start,
            'endDate': today,
            'dimensions': ['query'],
            'rowLimit': 50,
            'orderBy': [{'fieldName': 'impressions', 'sortOrder': 'DESCENDING'}],
        }
    ).execute()
    
    result['top_queries'] = [
        {'query': r.get('keys', [''])[0], 'clicks': r.get('clicks', 0),
         'impressions': r.get('impressions', 0), 'ctr': r.get('ctr', 0),
         'position': r.get('position', 0)}
        for r in qresp.get('rows', [])
    ]

    # 3. Top pages
    print("Pulling top pages...", file=sys.stderr)
    presp = service.searchanalytics().query(
        siteUrl=SITE_URL,
        body={
            'startDate': start,
            'endDate': today,
            'dimensions': ['page'],
            'rowLimit': 50,
            'orderBy': [{'fieldName': 'impressions', 'sortOrder': 'DESCENDING'}],
        }
    ).execute()
    
    result['top_pages'] = [
        {'page': r.get('keys', [''])[0], 'clicks': r.get('clicks', 0),
         'impressions': r.get('impressions', 0), 'ctr': r.get('ctr', 0),
         'position': r.get('position', 0)}
        for r in presp.get('rows', [])
    ]

    # 4. Pages dropped from Top 10 (pages that had position < 10 in prior period but not in current)
    print("Checking pages dropped from Top 10...", file=sys.stderr)
    ppresp = service.searchanalytics().query(
        siteUrl=SITE_URL,
        body={
            'startDate': start,
            'endDate': today,
            'dimensions': ['page'],
            'rowLimit': 1000,
            'orderBy': [{'fieldName': 'position', 'sortOrder': 'ASCENDING'}],
        }
    ).execute()

    # Check current top pages
    current_top = [r for r in ppresp.get('rows', []) if r.get('position', 100) < 10]
    
    # For dropped detection, we'd need historical data or comparison periods
    dropped = []
    # Simple heuristic: pages that had impressions last period but zero this period
    # Full dropped detection requires stored history
    result['pages_dropped_top10'] = {
        'count': len(dropped),
        'pages': dropped,
        'note': 'Full dropped-page detection requires stored historical snapshots'
    }

    # 5. Coverage / Index data
    print("Pulling index coverage...", file=sys.stderr)
    try:
        sitemaps = service.sitemaps().list(siteUrl=SITE_URL).execute()
        result['sitemaps'] = {'count': len(sitemaps.get('sitemap', [])),
                              'submitted': sum(s.get('contents', [{}])[0].get('submitted', 0)
                                              for s in sitemaps.get('sitemap', []) if s.get('contents'))}
    except Exception as e:
        result['sitemaps'] = {'error': str(e)[:100]}

    if OUTPUT:
        with open(OUTPUT, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Wrote {OUTPUT}", file=sys.stderr)
    else:
        print(json.dumps(result, indent=2))

    print(f"\n=== SUMMARY ===", file=sys.stderr)
    print(f"Clicks: {perf['clicks']} ({result['trend']['clicks_delta_pct']}% vs prior)", file=sys.stderr)
    print(f"Impressions: {perf['impressions']} ({result['trend']['impressions_delta_pct']}% vs prior)", file=sys.stderr)
    print(f"Avg CTR: {perf['ctr']:.1%}, Avg Position: {perf['avg_position']:.1f}", file=sys.stderr)
    print(f"Top queries: {len(result['top_queries'])}", file=sys.stderr)
    print(f"Top pages: {len(result['top_pages'])}", file=sys.stderr)

if __name__ == '__main__':
    main()