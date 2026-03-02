"""
Base Watcher - Abstract base class for all watcher scripts.

Watchers are lightweight Python scripts that run continuously and monitor
various inputs (Gmail, WhatsApp, filesystems) and create actionable .md files
in the Needs_Action folder for Claude Code to process.
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Any, Optional


class BaseWatcher(ABC):
    """
    Abstract base class for all watcher implementations.
    
    All watchers follow this pattern:
    1. Check for new items periodically
    2. Create .md action files in Needs_Action folder
    3. Track processed items to avoid duplicates
    """
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 60)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.inbox = self.vault_path / 'Inbox'
        self.check_interval = check_interval
        self.processed_ids: set = set()
        self.running = False
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.inbox.mkdir(parents=True, exist_ok=True)
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging to file and console."""
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.INFO)
        
        # Create logs directory
        logs_dir = self.vault_path / 'Logs'
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        # File handler
        log_file = logs_dir / f'{self.__class__.__name__}.log'
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    @abstractmethod
    def check_for_updates(self) -> List[Any]:
        """
        Check for new items to process.
        
        Returns:
            List of new items (emails, messages, files, etc.)
        """
        pass
    
    @abstractmethod
    def create_action_file(self, item: Any) -> Optional[Path]:
        """
        Create a .md action file in Needs_Action folder.
        
        Args:
            item: The item to create an action file for
            
        Returns:
            Path to created file, or None if failed
        """
        pass
    
    def process_item(self, item: Any) -> Optional[Path]:
        """
        Process a single item and create action file.
        
        Args:
            item: The item to process
            
        Returns:
            Path to created file, or None if skipped
        """
        try:
            filepath = self.create_action_file(item)
            if filepath:
                self.logger.info(f'Created action file: {filepath.name}')
            return filepath
        except Exception as e:
            self.logger.error(f'Error processing item: {e}')
            return None
    
    def run(self):
        """
        Main run loop. Continuously checks for updates and processes them.
        """
        self.running = True
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        
        try:
            while self.running:
                try:
                    items = self.check_for_updates()
                    if items:
                        self.logger.info(f'Found {len(items)} new item(s)')
                        for item in items:
                            self.process_item(item)
                    else:
                        self.logger.debug('No new items')
                except Exception as e:
                    self.logger.error(f'Error checking for updates: {e}')
                
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            self.logger.info('Watcher stopped by user')
        finally:
            self.running = False
            self.logger.info(f'{self.__class__.__name__} stopped')
    
    def stop(self):
        """Stop the watcher."""
        self.running = False
    
    def get_item_id(self, item: Any) -> str:
        """
        Extract unique ID from item. Override in subclass.
        
        Args:
            item: The item to extract ID from
            
        Returns:
            Unique identifier string
        """
        return str(hash(str(item)))
    
    def is_processed(self, item_id: str) -> bool:
        """Check if item has already been processed."""
        return item_id in self.processed_ids
    
    def mark_processed(self, item_id: str):
        """Mark item as processed."""
        self.processed_ids.add(item_id)
    
    def load_processed_from_disk(self) -> int:
        """
        Load processed item IDs from disk (for recovery after restart).
        
        Returns:
            Number of items loaded
        """
        processed_file = self.vault_path / '.processed_ids.txt'
        if processed_file.exists():
            try:
                content = processed_file.read_text()
                self.processed_ids = set(content.strip().split('\n'))
                self.processed_ids.discard('')  # Remove empty string
                self.logger.info(f'Loaded {len(self.processed_ids)} processed IDs from disk')
                return len(self.processed_ids)
            except Exception as e:
                self.logger.error(f'Error loading processed IDs: {e}')
        return 0
    
    def save_processed_to_disk(self):
        """Save processed item IDs to disk for recovery."""
        processed_file = self.vault_path / '.processed_ids.txt'
        try:
            processed_file.write_text('\n'.join(self.processed_ids))
        except Exception as e:
            self.logger.error(f'Error saving processed IDs: {e}')
    
    def cleanup_old_action_files(self, days: int = 7):
        """
        Clean up old action files that have been processed.
        
        Args:
            days: Remove files older than this many days
        """
        try:
            cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
            for filepath in self.needs_action.glob('*.md'):
                if filepath.stat().st_mtime < cutoff:
                    # Move to Done instead of deleting
                    done_dir = self.vault_path / 'Done'
                    done_dir.mkdir(parents=True, exist_ok=True)
                    filepath.rename(done_dir / filepath.name)
                    self.logger.info(f'Moved old file to Done: {filepath.name}')
        except Exception as e:
            self.logger.error(f'Error cleaning up old files: {e}')
