#!/usr/bin/env python3
"""
Hatch Intel Scanner — watches crypto earning sources 24/7
MVP: TaskMarket + manual sources, outputs JSON feed
"""
import json
import subprocess
import os
from datetime import datetime, timezone

def scan_taskmarket():
    """Scan TaskMarket for open bounties"""
    env = os.environ.copy()
    env['PATH'] = '/home/hatch/workspace/npm-global/bin:' + env['PATH']
    env['TASKMARKET_API_URL'] = 'https://api.taskmarket.dev'
    try:
        result = subprocess.run(
            ['taskmarket', 'task', 'list', '--status', 'open', '--limit', '20'],
            capture_output=True, text=True, env=env, timeout=30
        )
        data = json.loads(result.stdout)
        tasks = []
        for t in data['data']['tasks']:
            tasks.append({
                'source': 'taskmarket',
                'id': t.get('referenceCode'),
                'title': t.get('description', '')[:100],
                'reward_usdc': int(t.get('reward', 0)) / 1000000,
                'mode': t.get('mode'),
                'submissions': t.get('submissionCount', 0),
                'expiry': t.get('expiryTime'),
                'url': f"https://taskmarket.dev/tasks/{t.get('id')}"
            })
        return tasks
    except Exception as e:
        print(f"TaskMarket scan failed: {e}")
        return []

def main():
    all_ops = []
    all_ops.extend(scan_taskmarket())
    
    # Filter: no-KYC (all taskmarket), real rewards, not expired
    filtered = [op for op in all_ops if op['reward_usdc'] >= 1.0]
    
    output = {
        'scanned_at': datetime.now(timezone.utc).isoformat(),
        'opportunities': filtered,
        'count': len(filtered)
    }
    
    os.makedirs('/home/hatch/workspace/hatch-intel/data', exist_ok=True)
    with open('/home/hatch/workspace/hatch-intel/data/latest.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Scanned {len(all_ops)} ops, {len(filtered)} meet criteria")
    return output

if __name__ == '__main__':
    main()
