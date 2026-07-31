"""
File System Watcher - Monitors a drop folder for new files.

This is a simple watcher that requires no API setup. Users can drag files
into a drop folder, and the watcher will create action files for Claude
to process.

Usage:
    python filesystem_watcher.py
"""

import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

from base_watcher import BaseWatcher


class FileDropHandler(BaseWatcher):
    """
    File System Watcher - Monitors a drop folder for new files.
    
    Features:
    - Watches Inbox folder for new files
    - Creates markdown action files with file metadata
    - Copies files to vault for safekeeping
    - Tracks processed files by hash to avoid duplicates
    """
    
    def __init__(self, vault_path: str, check_interval: int = 30):
        """
        Initialize File System Watcher.
        
        Args:
            vault_path: Path to Obsidian vault
            check_interval: Seconds between checks (default: 30)
        """
        super().__init__(vault_path, check_interval)
        
        # Drop folder (where users put files)
        self.drop_folder = self.vault_path / 'Inbox'
        self.files_folder = self.vault_path / 'Files'
        
        # Ensure directories exist
        self.drop_folder.mkdir(parents=True, exist_ok=True)
        self.files_folder.mkdir(parents=True, exist_ok=True)
        
        # Load processed file hashes
        self.load_processed_from_disk()
    
    def check_for_updates(self) -> List[Path]:
        """
        Check for new files in the drop folder.
        
        Returns:
            List of new file paths
        """
        new_files = []
        
        try:
            for filepath in self.drop_folder.iterdir():
                if filepath.is_file() and not filepath.name.startswith('.'):
                    # Calculate hash to check if already processed
                    file_hash = self._calculate_hash(filepath)
                    
                    if not self.is_processed(file_hash):
                        new_files.append(filepath)
            
            return new_files
            
        except Exception as e:
            self.logger.error(f'Error checking drop folder: {e}')
            return []
    
    def create_action_file(self, filepath: Path) -> Optional[Path]:
        """
        Create markdown action file for dropped file.
        
        Args:
            filepath: Path to the dropped file
            
        Returns:
            Path to created action file
        """
        try:
            # Calculate file hash
            file_hash = self._calculate_hash(filepath)
            
            # Get file metadata
            stat = filepath.stat()
            file_size = stat.st_size
            created_time = datetime.fromtimestamp(stat.st_ctime)
            modified_time = datetime.fromtimestamp(stat.st_mtime)
            
            # Copy file to Files folder for safekeeping
            dest_path = self.files_folder / filepath.name
            if not dest_path.exists():
                shutil.copy2(filepath, dest_path)
                self.logger.info(f'Copied file to Files: {filepath.name}')
            
            # Create filename
            safe_name = self._sanitize_filename(filepath.stem)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            action_filename = f'FILE_{timestamp}_{safe_name}.md'
            
            # Determine file type hints
            file_type_hints = self._get_file_type_hints(filepath.suffix)
            
            # Create content
            content = f'''---
type: file_drop
original_name: {filepath.name}
file_hash: {file_hash}
size_bytes: {file_size}
size_human: {self._format_size(file_size)}
received: {datetime.now().isoformat()}
priority: normal
status: pending
---

# File Drop: {filepath.name}

## File Information

- **Original Path:** {filepath}
- **Size:** {self._format_size(file_size)}
- **Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **File Type:** {filepath.suffix} {file_type_hints}

---

## File Content

<!-- If this is a text file, you can paste content below -->

---

## Suggested Actions

- [ ] Review the file content
- [ ] Process according to file type
- [ ] Take necessary action
- [ ] Archive after processing

## Notes

<!-- Add your notes here -->

---
*Created by File System Watcher at {datetime.now().isoformat()}*
'''
            
            # Write action file
            action_filepath = self.needs_action / action_filename
            action_filepath.write_text(content, encoding='utf-8')
            
            # Mark as processed
            self.mark_processed(file_hash)
            self.save_processed_to_disk()
            
            return action_filepath
            
        except Exception as e:
            self.logger.error(f'Error creating action file: {e}')
            return None
    
    def _calculate_hash(self, filepath: Path) -> str:
        """
        Calculate SHA256 hash of file.
        
        Args:
            filepath: Path to file
            
        Returns:
            SHA256 hash string
        """
        hash_md5 = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _format_size(self, size_bytes: int) -> str:
        """
        Format file size in human-readable format.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Human-readable size string
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    def _sanitize_filename(self, text: str) -> str:
        """
        Sanitize text for use in filename.
        
        Args:
            text: Text to sanitize
            
        Returns:
            Sanitized filename-safe string
        """
        invalid_chars = '<>:"/\\|？*'
        for char in invalid_chars:
            text = text.replace(char, '_')
        return text.strip()[:50]
    
    def _get_file_type_hints(self, extension: str) -> str:
        """
        Get hints about file type based on extension.
        
        Args:
            extension: File extension (e.g., '.pdf')
            
        Returns:
            Description of file type
        """
        hints = {
            '.pdf': '(PDF Document)',
            '.doc': '(Word Document)',
            '.docx': '(Word Document)',
            '.txt': '(Text File)',
            '.md': '(Markdown)',
            '.xls': '(Excel Spreadsheet)',
            '.xlsx': '(Excel Spreadsheet)',
            '.csv': '(CSV Data)',
            '.jpg': '(Image)',
            '.jpeg': '(Image)',
            '.png': '(Image)',
            '.gif': '(Image)',
            '.zip': '(Compressed Archive)',
            '.rar': '(Compressed Archive)',
        }
        return hints.get(extension.lower(), '(Unknown Type)')


def main():
    """Main entry point."""
    import sys
    
    # Get vault path from argument or use default
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        # Default: sibling directory
        vault_path = Path(__file__).parent.parent / 'AI_Employee_Vault'
    
    # Create and run watcher
    watcher = FileDropHandler(
        vault_path=str(vault_path),
        check_interval=30  # Check every 30 seconds
    )
    
    print(f"File System Watcher starting...")
    print(f"Drop folder: {watcher.drop_folder}")
    print(f"Vault: {vault_path}")
    print("Drop files into the Inbox folder to trigger processing")
    print("Press Ctrl+C to stop")
    print()
    
    watcher.run()


if __name__ == '__main__':
    main()
