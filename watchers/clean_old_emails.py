"""
Clean up old email action files by re-extracting plain text from Gmail.
This removes HTML/CSS code from existing email files.
"""

import re
from pathlib import Path

def clean_email_files():
    """Remove HTML/CSS from existing email action files."""
    
    needs_action = Path('AI_Employee_Vault/Needs_Action')
    
    for filepath in needs_action.glob('EMAIL_*.md'):
        content = filepath.read_text(encoding='utf-8')
        
        # Check if file has HTML content
        if '<!DOCTYPE' in content or '<html' in content.lower():
            print(f"Cleaning: {filepath.name}")
            
            # Find the Email Content section
            parts = content.split('## Email Content\n')
            if len(parts) >= 2:
                header = parts[0]
                rest = parts[1].split('\n\n---\n\n## Suggested Actions')
                
                if len(rest) >= 2:
                    old_content = rest[0]
                    footer = rest[1]
                    
                    # Strip HTML tags
                    clean_text = re.sub(r'<[^>]+>', '', old_content)
                    clean_text = re.sub(r'\s+', ' ', clean_text)
                    clean_text = clean_text.strip()
                    
                    # Truncate if too long
                    if len(clean_text) > 5000:
                        clean_text = clean_text[:5000] + "\n\n... [truncated]"
                    
                    # Rebuild file
                    new_content = f"{header}## Email Content\n\n{clean_text}\n\n---\n\n## Suggested Actions{footer}"
                    
                    filepath.write_text(new_content, encoding='utf-8')
                    print(f"  ✓ Cleaned: {filepath.name}")
    
    print("\nDone! All email files cleaned.")

if __name__ == '__main__':
    clean_email_files()
