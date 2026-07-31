#!/usr/bin/env python3
"""
Twitter (X) Poster Skill for AI Employee

Uses Playwright to post tweets, threads, and media to X.com.
Supports authentication, scheduling, and approval workflow.
"""

import asyncio
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
except ImportError:
    print("Playwright not installed. Run: pip install playwright && playwright install")
    sys.exit(1)


class TwitterPoster:
    """Automated Twitter/X posting using Playwright."""
    
    def __init__(self, vault_path: str, headless: bool = True):
        self.vault_path = Path(vault_path)
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.session_dir = Path("watchers/twitter_session")
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        # Vault directories
        self.plans_dir = self.vault_path / "Plans" / "Social"
        self.approved_dir = self.vault_path / "Approved" / "Social"
        self.pending_dir = self.vault_path / "Pending_Approval" / "Social"
        self.done_dir = self.vault_path / "Done" / "Social"
        self.logs_dir = self.vault_path / "Logs"
        
        for d in [self.plans_dir, self.approved_dir, self.pending_dir, self.done_dir, self.logs_dir]:
            d.mkdir(parents=True, exist_ok=True)
    
    async def start(self):
        """Start browser."""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context(
            storage_state=self.session_dir / "state.json" if (self.session_dir / "state.json").exists() else None
        )
        self.page = await self.context.new_page()
        self._log("Twitter poster started")
    
    async def authenticate(self) -> bool:
        """Authenticate with Twitter/X."""
        self._log("Starting Twitter/X authentication...")
        
        await self.page.goto("https://x.com/i/flow/login")
        await self.page.wait_for_load_state("networkidle")
        
        # Wait for manual login
        print("\n" + "="*60)
        print("MANUAL LOGIN REQUIRED")
        print("="*60)
        print("1. Log in to Twitter/X in the browser window")
        print("2. Complete any 2FA if prompted")
        print("3. Wait for home timeline to load")
        print("4. Press Enter here when done")
        print("="*60 + "\n")
        
        input("Press Enter after logging in...")
        
        # Save session
        await self.context.storage_state(path=self.session_dir / "state.json")
        self._log("Twitter/X authentication saved")
        return True
    
    async def check_auth(self) -> bool:
        """Check if authenticated."""
        try:
            await self.page.goto("https://x.com/home")
            await self.page.wait_for_load_state("networkidle", timeout=10000)
            # Check for home timeline
            await self.page.wait_for_selector('[data-testid="primaryColumn"]', timeout=5000)
            return True
        except:
            return False
    
    async def post_tweet(self, content: str, media_paths: List[str] = None,
                         reply_to: str = None) -> Dict[str, Any]:
        """Post a single tweet."""
        self._log(f"Posting tweet: {content[:50]}...")
        
        try:
            await self.page.goto("https://x.com/compose/tweet")
            await self.page.wait_for_load_state("networkidle")
            await self.page.wait_for_selector('[data-testid="tweetTextarea_0"]', timeout=10000)
            
            # Type content
            await self.page.fill('[data-testid="tweetTextarea_0"]', content)
            await self.page.wait_for_timeout(1000)
            
            # Add media if provided
            if media_paths:
                for media_path in media_paths:
                    if Path(media_path).exists():
                        await self.page.set_input_files(
                            'input[data-testid="fileInput"]', media_path
                        )
                        await self.page.wait_for_timeout(3000)
            
            # Post
            await self.page.click('[data-testid="tweetButton"]', timeout=10000)
            await self.page.wait_for_selector('[data-testid="toast"]', timeout=10000)
            
            # Get tweet URL
            tweet_link = await self.page.query_selector('a[href*="/status/"]')
            tweet_url = ""
            if tweet_link:
                tweet_url = await tweet_link.get_attribute("href")
            
            self._log(f"Tweet posted successfully: {tweet_url}")
            return {"success": True, "url": tweet_url, "content": content}
            
        except Exception as e:
            self._log(f"Tweet error: {e}")
            return {"success": False, "error": str(e)}
    
    async def post_thread(self, tweets: List[str], media_map: Dict[int, List[str]] = None) -> Dict[str, Any]:
        """Post a thread of tweets."""
        self._log(f"Posting thread with {len(tweets)} tweets")
        
        results = []
        previous_tweet_id = None
        
        for i, tweet_content in enumerate(tweets):
            try:
                await self.page.goto("https://x.com/compose/tweet")
                await self.page.wait_for_load_state("networkidle")
                await self.page.wait_for_selector('[data-testid="tweetTextarea_0"]', timeout=10000)
                
                # Type content
                await self.page.fill('[data-testid="tweetTextarea_0"]', tweet_content)
                await self.page.wait_for_timeout(1000)
                
                # Add media for this tweet
                if media_map and i in media_map:
                    for media_path in media_map[i]:
                        if Path(media_path).exists():
                            await self.page.set_input_files(
                                'input[data-testid="fileInput"]', media_path
                            )
                            await self.page.wait_for_timeout(3000)
                
                # Post
                await self.page.click('[data-testid="tweetButton"]', timeout=10000)
                await self.page.wait_for_selector('[data-testid="toast"]', timeout=10000)
                
                # Get tweet URL
                tweet_link = await self.page.query_selector('a[href*="/status/"]')
                tweet_url = ""
                if tweet_link:
                    tweet_url = await tweet_link.get_attribute("href")
                
                results.append({
                    "index": i,
                    "success": True,
                    "url": tweet_url,
                    "content": tweet_content
                })
                
                self._log(f"Thread tweet {i+1}/{len(tweets)} posted: {tweet_url}")
                await self.page.wait_for_timeout(2000)
                
            except Exception as e:
                self._log(f"Thread tweet {i+1} error: {e}")
                results.append({
                    "index": i,
                    "success": False,
                    "error": str(e),
                    "content": tweet_content
                })
                break
        
        return {
            "success": all(r["success"] for r in results),
            "tweets": results,
            "count": len(results)
        }
    
    async def post_with_media(self, content: str, media_path: str) -> Dict[str, Any]:
        """Post tweet with image/video."""
        return await self.post_tweet(content, [media_path])
    
    def create_tweet_plan(self, content: str, media: List[str] = None,
                          thread: List[str] = None, hashtags: str = "",
                          schedule: str = None) -> Path:
        """Create tweet plan for approval workflow."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tweet_plan_{timestamp}.md"
        filepath = self.plans_dir / filename
        
        plan_content = f"""---
type: tweet
content: |
{content}
media: {json.dumps(media or [])}
thread: {json.dumps(thread or [])}
hashtags: "{hashtags}"
schedule: "{schedule or ''}"
status: draft
created: "{datetime.now().isoformat()}"
---

# Tweet Plan

## Content
{content}
**Hashtags:** {hashtags or 'None'}
**Media:** {len(media) if media else 0} file(s)
**Thread:** {len(thread)} additional tweets
**Schedule:** {schedule or 'Immediate'}

## Approval Required
Move this file to `/Approved/Social/` to publish.
"""
        
        filepath.write_text(plan_content, encoding="utf-8")
        self._log(f"Created tweet plan: {filepath}")
        return filepath
    
    async def check_approved_tweets(self) -> List[Path]:
        """Check for approved tweets."""
        return list(self.approved_dir.glob("tweet_plan_*.md"))
    
    async def process_approved_tweets(self) -> List[Dict[str, Any]]:
        """Process all approved tweets."""
        results = []
        approved = await self.check_approved_tweets()
        
        for tweet_file in approved:
            try:
                content = tweet_file.read_text(encoding="utf-8")
                details = self._parse_plan_file(content)
                
                if details.get("thread"):
                    result = await self.post_thread(
                        [details.get("content", "")] + details["thread"],
                        {}  # media_map not implemented in simple version
                    )
                else:
                    result = await self.post_tweet(
                        details.get("content", ""),
                        details.get("media", [])
                    )
                
                # Move to done
                done_dir = self.vault_path / "Done" / "Social"
                done_dir.mkdir(parents=True, exist_ok=True)
                tweet_file.rename(done_dir / tweet_file.name)
                
                results.append({
                    "file": tweet_file.name,
                    "result": result
                })
                
            except Exception as e:
                self._log(f"Error processing {tweet_file}: {e}")
                results.append({"file": tweet_file.name, "result": {"success": False, "error": str(e)}})
        
        return results
    
    def _parse_plan_file(self, content: str) -> Dict[str, Any]:
        """Parse plan file frontmatter."""
        details = {}
        lines = content.split("\n")
        in_frontmatter = False
        
        for line in lines:
            if line.strip() == "---":
                in_frontmatter = not in_frontmatter
                continue
            if in_frontmatter and ":" in line:
                key, value = line.split(":", 1)
                details[key.strip()] = value.strip().strip('"')
        
        # Parse JSON fields
        for field in ["media", "thread"]:
            if field in details:
                try:
                    details[field] = json.loads(details[field])
                except:
                    details[field] = []
        
        return details
    
    def _log(self, message: str):
        """Log to file."""
        log_file = self.logs_dir / "twitter_poster.log"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_file, "a") as f:
            f.write(f"[{timestamp}] {message}\n")
        print(f"[{timestamp}] {message}")
    
    async def close(self):
        """Close browser."""
        if self.browser:
            await self.browser.close()
            self._log("Twitter poster closed")


async def main():
    parser = argparse.ArgumentParser(description="Twitter/X Poster")
    parser.add_argument("--vault", default="AI_Employee_Vault", help="Vault path")
    parser.add_argument("--headless", action="store_true", default=True, help="Run headless")
    parser.add_argument("--auth", action="store_true", help="Authenticate with Twitter")
    parser.add_argument("--content", help="Tweet content")
    parser.add_argument("--media", nargs="*", help="Media file paths")
    parser.add_argument("--thread", nargs="*", help="Additional thread tweets")
    parser.add_argument("--hashtags", help="Hashtags")
    parser.add_argument("--schedule", help="Schedule time (not implemented)")
    parser.add_argument("--create-plan", action="store_true", help="Create approval plan")
    parser.add_argument("--process-approved", action="store_true", help="Process approved tweets")
    
    args = parser.parse_args()
    
    poster = TwitterPoster(args.vault, args.headless)
    
    try:
        await poster.start()
        
        if args.auth:
            await poster.authenticate()
        
        elif args.create_plan:
            if not args.content:
                print("Error: --content required for creating plan")
                sys.exit(1)
            
            poster.create_tweet_plan(
                args.content, args.media, args.thread, args.hashtags, args.schedule
            )
        
        elif args.content:
            if not await poster.check_auth():
                print("Not authenticated. Run with --auth first.")
                sys.exit(1)
            
            if args.thread:
                result = await poster.post_thread(
                    [args.content] + args.thread
                )
            else:
                result = await poster.post_tweet(args.content, args.media)
            
            print(json.dumps(result, indent=2))
        
        elif args.process_approved:
            if not await poster.check_auth():
                print("Not authenticated. Run with --auth first.")
                sys.exit(1)
            
            results = await poster.process_approved_tweets()
            for r in results:
                print(f"{r['file']}: {r['result']}")
        
        else:
            parser.print_help()
    
    finally:
        await poster.close()


if __name__ == "__main__":
    asyncio.run(main())