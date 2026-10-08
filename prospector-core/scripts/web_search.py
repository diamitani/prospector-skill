#!/usr/bin/env python3
"""Backup web search (DuckDuckGo via the third-party `ddgs` library) for when the harness has
no search tool of its own. Prints JSON: [{title, url, snippet}]. Results are DISCOVERY ONLY:
nothing found here is trusted until verify_list.py re-fetches and checks it.

  pip install ddgs
  python3 web_search.py '"RevOps" "hiring" site:greenhouse.io' --max 10
"""
import argparse
import json
import sys


def main():
    p = argparse.ArgumentParser()
    p.add_argument('query')
    p.add_argument('--max', type=int, default=10)
    a = p.parse_args()
    try:
        from ddgs import DDGS
    except ImportError:
        sys.exit('The backup search needs the `ddgs` package (pip install ddgs). '
                 'Or use the harness web search tool instead.')
    rows = DDGS().text(a.query, backend='duckduckgo', max_results=min(a.max, 25))
    print(json.dumps([{'title': r.get('title', ''), 'url': r.get('href', ''), 'snippet': r.get('body', '')}
                      for r in rows or []], indent=2))


if __name__ == '__main__':
    main()
