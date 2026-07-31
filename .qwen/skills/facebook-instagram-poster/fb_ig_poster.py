#!/usr/bin/env python3
"""
Facebook & Instagram Poster Skill

Automates posting to Facebook Pages and Instagram using Playwright.
Supports text, images, scheduling, and approval workflow integration.
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from playwright.async_api import async_playwright, Browser, BrowserContext, Page


class SocialPoster:
    """Handles Facebook and Instagram posting via Playwright."""
    
    def __init__(self, vault_path: str = "AI_Employee_Vault", headless: bool = True):
        self.vault_path = Path(vault_path)
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        # Session directories
        self.fb_session_dir = Path("watchers/facebook_session")
        self.ig_session_dir = Path("watchers/instagram_session")
        
        # Vault directories
        self.social_dir = self.vault_path / "Social"
        self.fb_dir = self.social_dir / "Facebook"
        self.ig_dir = self.social_dir / "Instagram"
        self.plans_dir = self.vault_path / "Plans"
        self.pending_dir = self.vault_path / "Pending_Approval"
        self.approved_dir = self.vault_path / "Approved"
        self.logs_dir = self.vault_path / "Logs"
        
        # Create directories
        for d in [self.fb_session_dir, self.ig_session_dir, self.fb_dir, self.ig_dir, 
                  self.plans_dir, self.pending_dir, self.approved_dir, self.logs_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        self.log_file = self.logs_dir / "social_poster.log"
    
    def _log(self, message: str):
        """Log message to file and console."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
    
    async def _get_browser(self) -> Browser:
        """Get or create browser instance."""
        if self.browser is None:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(headless=self.headless)
        return self.browser
    
    async def _get_context(self, session_dir: Path) -> BrowserContext:
        """Get or create browser context with saved session."""
        browser = await self._get_browser()
        
        if self.context is None:
            self.context = await browser.new_context(
                storage_state=session_dir / "state.json" if (session_dir / "state.json").exists() else None,
                viewport={"width": 1280, "height": 720}
            )
        return self.context
    
    async def _get_page(self, context: BrowserContext) -> Page:
        """Get or create page."""
        if self.page is None:
            self.page = await context.new_page()
        return self.page
    
    async def save_session(self, context: BrowserContext, session_dir: Path):
        """Save browser session state."""
        await context.storage_state(path=session_dir / "state.json")
        self._log(f"Session saved to {session_dir}")
    
    async def authenticate_facebook(self):
        """Interactive Facebook authentication."""
        self._log("Starting Facebook authentication...")
        
        browser = await self._get_browser()
        context = await browser.new_context()
        page = await context.new_page()
        
        await page.goto("https://www.facebook.com/login")
        self._log("Please log in to Facebook in the browser window...")
        self._log("After login, navigate to your Meta Business Suite or Pages.")
        self._log("Press Enter here when done...")
        
        input()
        
        await self.save_session(context, self.fb_session_dir)
        await context.close()
        self._log("Facebook authentication complete!")
    
    async def authenticate_instagram(self):
        """Interactive Instagram authentication."""
        self._log("Starting Instagram authentication...")
        
        browser = await self._get_browser()
        context = await browser.new_context()
        page = await context.new_page()
        
        await page.goto("https://www.instagram.com/accounts/login/")
        self._log("Please log in to Instagram in the browser window...")
        self._log("Press Enter here when done...")
        
        input()
        
        await self.save_session(context, self.ig_session_dir)
        await context.close()
        self._log("Instagram authentication complete!")
    
    async def post_to_facebook(self, page_name: str, content: str, 
                               image_path: Optional[str] = None,
                               schedule_time: Optional[str] = None) -> Dict[str, Any]:
        """Post to a Facebook Page."""
        self._log(f"Posting to Facebook page: {page_name}")
        
        context = await self._get_context(self.fb_session_dir)
        page = await self._get_page(context)
        
        try:
            # Go to Meta Business Suite
            await page.goto("https://business.facebook.com/latest/home")
            await page.wait_for_load_state("networkidle", timeout=30000)
            
            # Navigate to the specific page
            await page.click(f'text="{page_name}"', timeout=10000)
            await page.wait_for_load_state("networkidle")
            
            # Click Create Post
            await page.click('text="Create post"', timeout=10000)
            await page.wait_for_selector('textarea[placeholder*="What"]', timeout=10000)
            
            # Fill content
            await page.fill('textarea[placeholder*="What"]', content)
            
            # Add image if provided
            if image_path and Path(image_path).exists():
                await page.set_input_files('input[type="file"]', image_path)
                await page.wait_for_timeout(3000)
            
            # Schedule or publish
            if schedule_time:
                await page.click('text="Schedule"', timeout=5000)
                await page.fill('input[placeholder*="Date"]', schedule_time.split()[0])
                await page.fill('input[placeholder*="Time"]', schedule_time.split()[1])
                await page.click('text="Schedule"', timeout=5000)
                self._log(f"Post scheduled for {schedule_time}")
            else:
                await page.click('text="Post"', timeout=5000)
                await page.wait_for_selector('text="Published"', timeout=10000)
                self._log("Post published successfully!")
            
            return {"success": True, "platform": "facebook", "page": page_name}
            
        except Exception as e:
            self._log(f"Facebook post error: {e}")
            return {"success": False, "error": str(e)}
    
    async def post_to_instagram(self, content: str, 
                                image_path: Optional[str] = None,
                                hashtags: str = "",
                                schedule_time: Optional[str] = None) -> Dict[str, Any]:
        """Post to Instagram."""
        self._log("Posting to Instagram...")
        
        context = await self._get_context(self.ig_session_dir)
        page = await self._get_page(context)
        
        try:
            # Go to Instagram
            await page.goto("https://www.instagram.com/")
            await page.wait_for_load_state("networkidle")
            
            # Click Create button
            await page.click('svg[aria-label="New post"]', timeout=10000)
            await page.wait_for_selector('button:has-text("Post")', timeout=10000)
            
            # Select post type
            await page.click('button:has-text("Post")', timeout=5000)
            
            # Upload image
            if image_path and Path(image_path).exists():
                await page.set_input_files('input[type="file"]', image_path)
                await page.wait_for_timeout(3000)
                await page.click('text="Next"', timeout=5000)
                await page.wait_for_timeout(2000)
            
            # Add caption
            full_content = content
            if hashtags:
                full_content += f"\n\n{hashtags}"
            
            await page.fill('textarea[placeholder*="caption"]', full_content)
            
            # Share
            await page.click('text="Share"', timeout=10000)
            await page.wait_for_selector('text="Post shared"', timeout=15000)
            
            self._log("Instagram post published successfully!")
            return {"success": True, "platform": "instagram"}
            
        except Exception as e:
            self._log(f"Instagram post error: {e}")
            return {"success": False, "error": str(e)}
    
    def create_post_plan(self, platform: str, page: str, content: str,
                         image: Optional[str] = None, hashtags: str = "",
                         schedule: Optional[str] = None) -> Path:
        """Create a post plan file for approval workflow."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"social_post_{platform}_{timestamp}.md"
        filepath = self.plans_dir / filename
        
        plan_content = f"""---
type: social_post
platform: {platform}
page: "{page}"
content: |
{content}
image: "{image or ''}"
hashtags: "{hashtags}"
schedule: "{schedule or ''}"
status: draft
created: "{datetime.now().isoformat()}"
---

# Social Media Post Plan

## Platform: {platform.capitalize()}
**Page/Account:** {page}
**Content:** 
{content}
**Image:** {image or 'None'}
**Hashtags:** {hashtags or 'None'}
**Schedule:** {schedule or 'Immediate'}

## Approval Required
Move this file to `/Approved/` to publish.
"""
        
        filepath.write_text(plan_content, encoding="utf-8")
        self._log(f"Created post plan: {filepath}")
        return filepath
    
    async def check_approved_posts(self) -> List[Path]:
        """Check for approved social posts."""
        approved = list(self.approved_dir.glob("social_post_*.md"))
        return approved
    
    async def process_approved_posts(self) -> List[Dict[str, Any]]:
        """Process all approved social posts."""
        results = []
        approved_posts = await self.check_approved_posts()
        
        for post_file in approved_posts:
            try:
                content = post_file.read_text(encoding="utf-8")
                details = self._parse_plan_file(content)
                
                if details.get("platform") == "facebook":
                    result = await self.post_to_facebook(
                        details.get("page", ""),
                        details.get("content", ""),
                        details.get("image"),
                        details.get("schedule")
                    )
                elif details.get("platform") == "instagram":
                    result = await self.post_to_instagram(
                        details.get("content", ""),
                        details.get("image"),
                        details.get("hashtags", ""),
                        details.get("schedule")
                    )
                elif details.get("platform") == "both":
                    fb_result = await self.post_to_facebook(
                        details.get("page", ""),
                        details.get("content", ""),
                        details.get("image"),
                        details.get("schedule")
                    )
                    ig_result = await self.post_to_instagram(
                        details.get("content", ""),
                        details.get("image"),
                        details.get("hashtags", ""),
                        details.get("schedule")
                    )
                    result = {"facebook": fb_result, "instagram": ig_result}
                else:
                    result = {"success": False, "error": f"Unknown platform: {details.get('platform')}"}
                
                # Move to done
                done_dir = self.vault_path / "Done" / "Social"
                done_dir.mkdir(parents=True, exist_ok=True)
                post_file.rename(done_dir / post_file.name)
                
                results.append({
                    "file": post_file.name,
                    "result": result
                })
                
            except Exception as e:
                self._log(f"Error processing {post_file}: {e}")
                results.append({"file": post_file.name, "result": {"success": False, "error": str(e)}})
        
        return results
    
    def _parse_plan_file(self, content: str) -> Dict[str, str]:
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
        
        return details
    
    async def close(self):
        """Close browser."""
        if self.browser:
            await self.browser.close()


async def main():
    parser = argparse.ArgumentParser(description="Facebook & Instagram Poster")
    parser.add_argument("--vault", default="AI_Employee_Vault", help="Vault path")
    parser.add_argument("--headless", action="store_true", default=True, help="Run headless")
    parser.add_argument("--auth", choices=["facebook", "instagram", "both"], help="Authenticate")
    parser.add_argument("--platform", choices=["facebook", "instagram", "both"], help="Platform to post to")
    parser.add_argument("--page", help="Facebook page name")
    parser.add_argument("--content", help="Post content")
    parser.add_argument("--image", help="Image path")
    parser.add_argument("--hashtags", help="Hashtags for Instagram")
    parser.add_argument("--schedule", help="Schedule time (YYYY-MM-DD HH:MM)")
    parser.add_argument("--create-plan", action="store_true", help="Create approval plan only")
    parser.add_argument("--process-approved", action="store_true", help="Process approved posts")
    
    args = parser.parse_args()
    
    poster = SocialPoster(args.vault, args.headless)
    
    try:
        if args.auth:
            if args.auth in ["facebook", "both"]:
                await poster.authenticate_facebook()
            if args.auth in ["instagram", "both"]:
                await poster.authenticate_instagram()
        
        elif args.create_plan:
            if not args.platform or not args.content:
                print("Error: --platform and --content required for creating plan")
                sys.exit(1)
            
            page = args.page or "Default Page"
            poster.create_post_plan(
                args.platform, page, args.content,
                args.image, args.hashtags, args.schedule
            )
        
        elif args.platform and args.content:
            if args.platform in ["facebook", "both"]:
                if not args.page:
                    print("Error: --page required for Facebook")
                    sys.exit(1)
                result = await poster.post_to_facebook(
                    args.page, args.content, args.image, args.schedule
                )
                print(json.dumps(result, indent=2))
            
            if args.platform in ["instagram", "both"]:
                result = await poster.post_to_instagram(
                    args.content, args.image, args.hashtags, args.schedule
                )
                print(json.dumps(result, indent=2))
        
        elif args.process_approved:
            results = await poster.process_approved_posts()
            for r in results:
                print(f"{r['file']}: {r['result']}")
        
        else:
            parser.print_help()
    
    finally:
        await poster.close()


if __name__ == "__main__":
    asyncio.run(main())