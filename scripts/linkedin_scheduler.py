import time
import argparse
from pathlib import Path
import schedule
import logging
from datetime import datetime

from importlib.machinery import SourceFileLoader

# Load linkedin_poster dynamically from .qwen/skills/linkedin-poster/linkedin_poster.py
poster_path = Path(__file__).parent.parent / '.qwen' / 'skills' / 'linkedin-poster' / 'linkedin_poster.py'
if poster_path.exists():
    poster_module = SourceFileLoader('linkedin_poster', str(poster_path)).load_module()
    LinkedInPoster = getattr(poster_module, 'LinkedInPoster')
else:
    LinkedInPoster = None

logger = logging.getLogger('LinkedInScheduler')
logging.basicConfig(level=logging.INFO)


def find_approved_posts(vault_path: Path):
    approved = vault_path / 'Approved'
    if not approved.exists():
        return []
    files = list(approved.glob('*.md'))
    posts = []
    for f in files:
        try:
            text = f.read_text(encoding='utf-8')
            if 'type: linkedin_post' in text:
                posts.append(f)
        except Exception:
            continue
    return posts


def post_approved(vault_path: Path, session_path: Path):
    if LinkedInPoster is None:
        logger.error('LinkedInPoster implementation not found; ensure .qwen/skills/linkedin-poster/linkedin_poster.py exists')
        return
    poster = LinkedInPoster(str(session_path))
    posts = find_approved_posts(vault_path)
    for p in posts:
        content = p.read_text(encoding='utf-8')
        # crude extraction: after the second --- take the content section
        try:
            idx = content.split('---')
            body = idx[-1].strip()
        except Exception:
            body = content

        logger.info(f'Posting {p.name} to LinkedIn...')
        ok = poster.create_post(body, headless=True)
        if ok:
            logger.info(f'Posted {p.name}; moving to Done')
            done_dir = vault_path / 'Done'
            done_dir.mkdir(parents=True, exist_ok=True)
            p.rename(done_dir / p.name)
        else:
            logger.warning(f'Failed to post {p.name}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--vault', help='Path to AI_Employee_Vault', default=str(Path(__file__).parent.parent / 'AI_Employee_Vault'))
    parser.add_argument('--session', help='LinkedIn session path', default=str(Path(__file__).parent.parent / 'watchers' / 'linkedin_session'))
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    args = parser.parse_args()

    vault = Path(args.vault)
    session = Path(args.session)

    if args.once:
        post_approved(vault, session)
        return

    # Default: run daily at 09:00
    schedule.every().day.at('09:00').do(post_approved, vault, session)
    logger.info('LinkedIn scheduler started — posting daily at 09:00')
    try:
        while True:
            schedule.run_pending()
            time.sleep(10)
    except KeyboardInterrupt:
        logger.info('LinkedIn scheduler stopped')


if __name__ == '__main__':
    main()
