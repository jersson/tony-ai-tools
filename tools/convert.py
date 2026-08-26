#!/usr/bin/env python3
"""
Document conversion tool for tony-ai-tools.

Converts various document formats to markdown using markitdown.
Supports: PDF, DOCX, DOC, XLSX, XLS, PPTX, TXT, HTML
Supports: local files and HTTP/HTTPS URLs

Usage:
    python convert.py <input> <output>
    python convert.py <url> <output>  # download and convert
    python convert.py <input_dir> <output_dir>  # batch conversion
"""

import sys
import os
import json
import hashlib
import tempfile
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime

try:
    from markitdown import MarkItDown
except ImportError:
    print("Error: markitdown not installed. Run: pip install 'markitdown[all]'", file=sys.stderr)
    sys.exit(1)


SUPPORTED_FORMATS = {
    '.pdf': 'markitdown',
    '.doc': 'markitdown',
    '.docx': 'markitdown',
    '.xlsx': 'markitdown',
    '.xls': 'markitdown',
    '.pptx': 'markitdown',
    '.txt': 'direct',
    '.html': 'markitdown',
    '.htm': 'markitdown',
}


def is_url(path: str) -> bool:
    """Check if path is a URL."""
    return path.startswith('http://') or path.startswith('https://')


def download_url(url: str, output_dir: str = None) -> str:
    """
    Download a URL to a temporary file.
    
    Returns:
        Path to downloaded file
    """
    if output_dir is None:
        output_dir = tempfile.mkdtemp()
    
    # Parse URL to get filename
    parsed = urllib.parse.urlparse(url)
    path = parsed.path
    
    # Get filename from URL
    filename = os.path.basename(path)
    if not filename or '.' not in filename:
        # Try to get content type
        try:
            response = urllib.request.urlopen(url)
            content_type = response.headers.get('Content-Type', '')
            if 'pdf' in content_type:
                filename = 'downloaded.pdf'
            elif 'html' in content_type:
                filename = 'downloaded.html'
            elif 'docx' in content_type or 'msword' in content_type:
                filename = 'downloaded.docx'
            else:
                filename = 'downloaded.bin'
        except Exception:
            filename = 'downloaded.bin'
    
    output_path = os.path.join(output_dir, filename)
    
    # Download file
    urllib.request.urlretrieve(url, output_path)
    
    return output_path


def get_url_extension(url: str) -> str:
    """Get file extension from URL."""
    parsed = urllib.parse.urlparse(url)
    path = parsed.path
    
    # Get extension from path
    _, ext = os.path.splitext(path)
    
    if ext:
        return ext.lower()
    
    # Try to detect from content type
    try:
        response = urllib.request.urlopen(url)
        content_type = response.headers.get('Content-Type', '')
        
        if 'pdf' in content_type:
            return '.pdf'
        elif 'html' in content_type:
            return '.html'
        elif 'docx' in content_type or 'msword' in content_type:
            return '.docx'
        elif 'xlsx' in content_type or 'spreadsheet' in content_type:
            return '.xlsx'
    except Exception:
        pass
    
    return ''


def calculate_checksum(file_path: str) -> str:
    """Calculate MD5 checksum of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return f"md5:{hash_md5.hexdigest()}"


def convert_file(input_path: str, output_path: str) -> dict:
    """
    Convert a single file to markdown.
    
    Returns:
        dict with conversion result
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    
    # If output is a directory, generate filename
    if output_path.is_dir() or (not output_path.suffix and not str(output_path).endswith('/')):
        output_path = output_path / f"{input_path.stem}.md"
    
    result = {
        'source_file': input_path.name,
        'output_file': output_path.name,
        'original_format': input_path.suffix.lower(),
        'status': 'success',
        'checksum': calculate_checksum(str(input_path)),
        'date_loaded': datetime.now().strftime('%Y-%m-%d'),
    }
    
    try:
        suffix = input_path.suffix.lower()
        
        if suffix not in SUPPORTED_FORMATS:
            result['status'] = 'skipped'
            result['reason'] = f'Unsupported format: {suffix}'
            return result
        
        if suffix == '.txt':
            # Direct read for TXT files
            content = input_path.read_text(encoding='utf-8')
            result['content'] = content
        else:
            # Use markitdown for other formats
            md = MarkItDown()
            conversion_result = md.convert(str(input_path))
            result['content'] = conversion_result.text_content
        
        # Add YAML frontmatter
        frontmatter = f"""---
source_file: {input_path.name}
original_format: {suffix}
date_loaded: {result['date_loaded']}
checksum: {result['checksum']}
---

"""
        result['content'] = frontmatter + result['content']
        
        # Write output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(result['content'], encoding='utf-8')
        
    except Exception as e:
        result['status'] = 'error'
        result['error'] = str(e)
    
    return result


def convert_url(url: str, output_path: str) -> dict:
    """
    Download and convert a URL to markdown.
    
    Returns:
        dict with conversion result
    """
    # If output_path is a directory, generate filename from URL
    output_path_obj = Path(output_path)
    if output_path_obj.is_dir() or output_path.endswith('/'):
        # Generate filename from URL
        parsed = urllib.parse.urlparse(url)
        filename = os.path.basename(parsed.path)
        if not filename or '.' not in filename:
            filename = 'downloaded.md'
        elif not filename.endswith('.md'):
            filename = os.path.splitext(filename)[0] + '.md'
        output_path = str(output_path_obj / filename)
    
    result = {
        'source_file': url,
        'output_file': output_path,
        'original_format': get_url_extension(url),
        'status': 'success',
        'checksum': '',
        'date_loaded': datetime.now().strftime('%Y-%m-%d'),
    }
    
    try:
        # Download URL
        temp_dir = tempfile.mkdtemp()
        downloaded_file = download_url(url, temp_dir)
        
        # Get extension from downloaded file
        downloaded_path = Path(downloaded_file)
        suffix = downloaded_path.suffix.lower()
        
        if suffix not in SUPPORTED_FORMATS:
            result['status'] = 'skipped'
            result['reason'] = f'Unsupported format: {suffix}'
            return result
        
        # Convert file
        result['checksum'] = calculate_checksum(downloaded_file)
        result['original_format'] = suffix
        
        if suffix == '.txt':
            content = downloaded_path.read_text(encoding='utf-8')
            result['content'] = content
        else:
            md = MarkItDown()
            conversion_result = md.convert(downloaded_file)
            result['content'] = conversion_result.text_content
        
        # Add YAML frontmatter
        frontmatter = f"""---
source_file: {url}
original_format: {suffix}
date_loaded: {result['date_loaded']}
checksum: {result['checksum']}
source_url: {url}
---

"""
        result['content'] = frontmatter + result['content']
        
        # Write output
        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)
        output_path_obj.write_text(result['content'], encoding='utf-8')
        
        # Cleanup
        os.remove(downloaded_file)
        os.rmdir(temp_dir)
        
    except Exception as e:
        result['status'] = 'error'
        result['error'] = str(e)
    
    return result


def get_file_checksum(file_path: str) -> str:
    """Calculate MD5 checksum of a file."""
    return calculate_checksum(file_path)


def load_manifest(manifest_path: str) -> dict:
    """Load manifest.json if it exists."""
    manifest_file = Path(manifest_path)
    if manifest_file.exists():
        with open(manifest_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_manifest(manifest_path: str, manifest: dict):
    """Save manifest.json."""
    manifest_file = Path(manifest_path)
    manifest_file.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)


def get_new_files(input_dir: Path, output_dir: Path) -> list:
    """
    Get files that are new or changed since last conversion.
    
    Returns:
        list of Path objects for files to convert
    """
    manifest_path = output_dir / 'manifest.json'
    manifest = load_manifest(str(manifest_path))
    
    new_files = []
    
    # Find all supported files
    for file in input_dir.iterdir():
        if file.is_file() and file.suffix.lower() in SUPPORTED_FORMATS:
            # Check if file is new or changed (manifest is keyed by filename)
            if file.name not in manifest:
                # New file
                new_files.append(file)
            else:
                # Check if file has changed
                current_checksum = get_file_checksum(str(file))
                stored_checksum = manifest[file.name].get('checksum', '')

                if current_checksum != stored_checksum:
                    new_files.append(file)
    
    return new_files


def batch_convert(input_dir: str, output_dir: str, incremental: bool = False) -> dict:
    """
    Convert all supported files in a directory.
    
    Args:
        input_dir: Input directory path
        output_dir: Output directory path
        incremental: If True, only convert new/changed files
    
    Returns:
        dict with batch conversion results
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    
    results = {
        'files': [],
        'total': 0,
        'success': 0,
        'failed': 0,
        'skipped': 0,
        'incremental': incremental,
    }
    
    # Get files to convert
    if incremental:
        files = get_new_files(input_dir, output_dir)
        results['mode'] = 'incremental'
    else:
        files = [f for f in input_dir.iterdir() 
                 if f.is_file() and f.suffix.lower() in SUPPORTED_FORMATS]
        results['mode'] = 'full'
    
    results['total'] = len(files)
    
    for file in files:
        output_file = output_dir / f"{file.stem}.md"
        result = convert_file(str(file), str(output_file))
        results['files'].append(result)
        
        if result['status'] == 'success':
            results['success'] += 1
        elif result['status'] == 'error':
            results['failed'] += 1
        else:
            results['skipped'] += 1
    
    # Calculate success rate
    results['success_rate'] = (results['success'] / results['total'] * 100) if results['total'] > 0 else 0
    
    return results


def main():
    if len(sys.argv) < 3:
        print("Usage: python convert.py <input> <output> [--incremental]")
        print("  <input>  - file, directory, or URL")
        print("  <output> - file or directory")
        print("  --incremental - only convert new/changed files (for directories)")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    incremental = '--incremental' in sys.argv
    
    # Check if input is a URL
    if is_url(input_path):
        result = convert_url(input_path, output_path)
        print(json.dumps(result, indent=2))
        
        if result['status'] != 'success':
            sys.exit(1)
        return
    
    input_path_obj = Path(input_path)
    output_path_obj = Path(output_path)
    
    if input_path_obj.is_file():
        # Single file conversion
        result = convert_file(input_path, output_path)
        print(json.dumps(result, indent=2))
        
        if result['status'] != 'success':
            sys.exit(1)
    
    elif input_path_obj.is_dir():
        # Batch conversion
        results = batch_convert(input_path, output_path, incremental)
        
        # Write manifest
        manifest_path = output_path_obj / 'manifest.json'
        
        # Update manifest with new files
        existing_manifest = load_manifest(str(manifest_path))
        for file_result in results['files']:
            if file_result['status'] == 'success':
                # Store file info in manifest
                source_file = file_result['source_file']
                # Find the full path - for now just store the filename
                existing_manifest[source_file] = {
                    'checksum': file_result['checksum'],
                    'date_loaded': file_result['date_loaded']
                }
        
        save_manifest(str(manifest_path), existing_manifest)
        
        print(json.dumps(results, indent=2))
        
        if results['success_rate'] < 75 and results['total'] > 0:
            print(f"\nWarning: Success rate {results['success_rate']:.1f}% is below 75% threshold", file=sys.stderr)
            sys.exit(1)
    
    else:
        print(f"Error: {input_path} does not exist", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
