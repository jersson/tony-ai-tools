#!/usr/bin/env python3
"""
Quality gate tool for tony-ai-tools.

Checks quality metrics for converted documents and knowledge base.
Supports load-documents and build-knowledge quality gates.

Usage:
    python quality_gate.py load <md_dir> [threshold]     # Check load quality
    python quality_gate.py build <kb_dir> [threshold]    # Check build quality
"""

import sys
import json
from pathlib import Path


DEFAULT_THRESHOLD = 75.0


def check_load_quality(md_dir: str, threshold: float = DEFAULT_THRESHOLD) -> dict:
    """
    Check quality of converted documents.
    
    Returns:
        quality report dict
    """
    md_dir = Path(md_dir)
    
    report = {
        'stage': 'load',
        'total_files': 0,
        'valid_files': 0,
        'invalid_files': 0,
        'success_rate': 0.0,
        'threshold': threshold,
        'passed': False,
        'issues': []
    }
    
    # Find all markdown files
    md_files = list(md_dir.glob('*.md'))
    report['total_files'] = len(md_files)
    
    if report['total_files'] == 0:
        report['issues'].append('No markdown files found')
        return report
    
    for md_file in md_files:
        # Skip manifest and report files
        if md_file.name in ['manifest.json', 'load-report.md', 'build-report.md']:
            report['total_files'] -= 1
            continue
        
        try:
            content = md_file.read_text(encoding='utf-8')
            
            # Check if file has content
            if len(content.strip()) < 10:
                report['invalid_files'] += 1
                report['issues'].append(f'{md_file.name}: File too short')
                continue
            
            # Check if file has frontmatter
            if not content.startswith('---'):
                report['invalid_files'] += 1
                report['issues'].append(f'{md_file.name}: Missing YAML frontmatter')
                continue
            
            # Check if frontmatter is valid
            end_idx = content.find('---', 3)
            if end_idx == -1:
                report['invalid_files'] += 1
                report['issues'].append(f'{md_file.name}: Invalid YAML frontmatter')
                continue
            
            report['valid_files'] += 1
            
        except Exception as e:
            report['invalid_files'] += 1
            report['issues'].append(f'{md_file.name}: {str(e)}')
    
    # Calculate success rate (exclude manifest/report from count)
    actual_files = report['total_files']
    if actual_files > 0:
        report['success_rate'] = (report['valid_files'] / actual_files) * 100
    else:
        report['success_rate'] = 0.0
    
    report['passed'] = report['success_rate'] >= threshold
    
    return report


def check_build_quality(kb_dir: str, threshold: float = DEFAULT_THRESHOLD) -> dict:
    """
    Check quality of knowledge base.
    
    Returns:
        quality report dict
    """
    kb_dir = Path(kb_dir)
    wiki_dir = kb_dir / 'wiki'
    
    report = {
        'stage': 'build',
        'total_pages': 0,
        'valid_pages': 0,
        'invalid_pages': 0,
        'success_rate': 0.0,
        'threshold': threshold,
        'passed': False,
        'issues': []
    }
    
    # Check if wiki directory exists
    if not wiki_dir.exists():
        report['issues'].append('Wiki directory not found')
        return report
    
    # Find all wiki pages
    wiki_files = list(wiki_dir.glob('*.md'))
    report['total_pages'] = len(wiki_files)
    
    if report['total_pages'] == 0:
        report['issues'].append('No wiki pages found')
        return report
    
    for wiki_file in wiki_files:
        try:
            content = wiki_file.read_text(encoding='utf-8')
            
            # Check if page has content
            if len(content.strip()) < 10:
                report['invalid_pages'] += 1
                report['issues'].append(f'{wiki_file.name}: Page too short')
                continue
            
            # Check if page has frontmatter
            if not content.startswith('---'):
                report['invalid_pages'] += 1
                report['issues'].append(f'{wiki_file.name}: Missing YAML frontmatter')
                continue
            
            # Check if frontmatter has required fields
            end_idx = content.find('---', 3)
            if end_idx == -1:
                report['invalid_pages'] += 1
                report['issues'].append(f'{wiki_file.name}: Invalid YAML frontmatter')
                continue
            
            frontmatter = content[3:end_idx]
            
            # Check for tags
            if 'tags:' not in frontmatter:
                report['invalid_pages'] += 1
                report['issues'].append(f'{wiki_file.name}: Missing tags in frontmatter')
                continue
            
            # Check for wiki links
            if wiki_file.name != 'index.md' and '[[' not in content:
                report['issues'].append(f'{wiki_file.name}: No wiki links found (warning)')
            
            report['valid_pages'] += 1
            
        except Exception as e:
            report['invalid_pages'] += 1
            report['issues'].append(f'{wiki_file.name}: {str(e)}')
    
    # Calculate success rate
    report['success_rate'] = (report['valid_pages'] / report['total_pages']) * 100
    report['passed'] = report['success_rate'] >= threshold
    
    return report


def main():
    if len(sys.argv) < 3:
        print("Usage: python quality_gate.py <stage> <dir> [threshold]")
        print("Stages:")
        print("  load <md_dir> [threshold]   - Check load quality")
        print("  build <kb_dir> [threshold]  - Check build quality")
        sys.exit(1)
    
    stage = sys.argv[1]
    dir_path = sys.argv[2]
    threshold = float(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_THRESHOLD
    
    if stage == 'load':
        report = check_load_quality(dir_path, threshold)
    elif stage == 'build':
        report = check_build_quality(dir_path, threshold)
    else:
        print(f"Error: Unknown stage '{stage}'", file=sys.stderr)
        sys.exit(1)
    
    print(json.dumps(report, indent=2))
    
    if not report['passed']:
        sys.exit(1)


if __name__ == '__main__':
    main()
