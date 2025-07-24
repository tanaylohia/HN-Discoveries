import os
import json
from datetime import datetime
from typing import List, Dict
from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown
import config

# AIDEV-NOTE: Reporter module for generating startup discovery reports
# Supports multiple output formats: console, markdown, JSON

class Reporter:
    def __init__(self):
        self.console = Console()
        self.report_dir = config.REPORT_DIR
        
        # Create report directory if it doesn't exist
        os.makedirs(self.report_dir, exist_ok=True)
    
    def generate_report(self, startups: List[Dict], format: str = "all") -> str:
        """
        Generate a report of discovered startups
        
        Args:
            startups: List of startup data with analysis
            format: Output format - "console", "markdown", "json", or "all"
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report_date = datetime.now().strftime("%B %d, %Y at %I:%M %p IST")
        
        # Sort by AI score
        startups.sort(key=lambda x: x['analysis']['ai_score'], reverse=True)
        
        if format in ["console", "all"]:
            self._console_report(startups, report_date)
        
        if format in ["markdown", "all"]:
            md_path = self._markdown_report(startups, timestamp, report_date)
            if format == "markdown":
                return md_path
        
        if format in ["json", "all"]:
            json_path = self._json_report(startups, timestamp)
            if format == "json":
                return json_path
        
        return os.path.join(self.report_dir, f"report_{timestamp}")
    
    def _console_report(self, startups: List[Dict], report_date: str):
        """Display report in console using rich"""
        self.console.print(f"\n[bold blue]Hacker News Startup & Innovation Discovery Report[/bold blue]")
        self.console.print(f"[dim]{report_date}[/dim]\n")
        
        if not startups:
            self.console.print("[yellow]No new startups found in this run.[/yellow]")
            return
        
        # Separate startups and innovations
        startups_list = [s for s in startups if s['analysis']['type'] == 'startup']
        innovations_list = [s for s in startups if s['analysis']['type'] == 'innovation']
        
        # Summary table
        table = Table(title=f"Top {len(startups)} Discoveries ({len(startups_list)} Startups, {len(innovations_list)} Innovations)")
        table.add_column("Rank", style="cyan", width=6)
        table.add_column("Name", style="green", width=25)
        table.add_column("Type", style="white", width=12)
        table.add_column("Category", style="yellow", width=20)
        table.add_column("Score", style="magenta", width=8)
        table.add_column("HN Score", style="blue", width=10)
        
        for i, startup_data in enumerate(startups[:10]):  # Top 10 for console
            post = startup_data['post']
            analysis = startup_data['analysis']
            
            table.add_row(
                str(i + 1),
                analysis['name'][:25],
                analysis['type'].capitalize(),
                analysis['category'][:20],
                f"{analysis['innovation_score']:.1f}/10",
                str(post.get('score', 0))
            )
        
        self.console.print(table)
        
        # Detailed view of top 3
        self.console.print("\n[bold]Top 3 Discoveries - Detailed View:[/bold]\n")
        
        for i, startup_data in enumerate(startups[:3]):
            post = startup_data['post']
            analysis = startup_data['analysis']
            
            self.console.print(f"[bold cyan]#{i+1} {analysis['name']} ({analysis['type']})[/bold cyan]")
            self.console.print(f"[link={config.HN_WEB_BASE}/item?id={post['id']}]View on HN[/link]")
            self.console.print(f"[bold]Category:[/bold] {analysis['category']}")
            self.console.print(f"[bold]Stage:[/bold] {analysis['stage']}")
            self.console.print(f"[bold]AI Score:[/bold] {analysis['ai_score']}/10")
            self.console.print(f"[bold]Summary:[/bold] {analysis['summary']}")
            self.console.print(f"[bold]Why Interesting:[/bold] {analysis['why_interesting']}")
            self.console.print("-" * 60 + "\n")
    
    def _markdown_report(self, startups: List[Dict], timestamp: str, report_date: str) -> str:
        """Generate markdown report"""
        filename = f"startup_report_{timestamp}.md"
        filepath = os.path.join(self.report_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# Hacker News Startup & Innovation Discovery Report\n\n")
            f.write(f"*Generated on {report_date}*\n\n")
            
            if not startups:
                f.write("No new startups found in this run.\n")
                return filepath
            
            # Separate types
            startups_list = [s for s in startups if s['analysis']['type'] == 'startup']
            innovations_list = [s for s in startups if s['analysis']['type'] == 'innovation']
            
            f.write(f"## Summary\n\n")
            f.write(f"- **Total Discoveries:** {len(startups)}\n")
            f.write(f"- **Startups:** {len(startups_list)}\n")
            f.write(f"- **Technical Innovations:** {len(innovations_list)}\n")
            f.write(f"- **Average Score:** {sum(s['analysis']['innovation_score'] for s in startups) / len(startups):.1f}/10\n")
            
            # Category distribution
            categories = {}
            for s in startups:
                cat = s['analysis']['category']
                categories[cat] = categories.get(cat, 0) + 1
            
            f.write(f"- **Top Categories:** {', '.join(f'{k} ({v})' for k, v in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5])}\n\n")
            
            f.write("## Top Discoveries\n\n")
            
            for i, startup_data in enumerate(startups):
                post = startup_data['post']
                analysis = startup_data['analysis']
                
                f.write(f"### {i+1}. {analysis['name']} ({analysis['type']})\n\n")
                f.write(f"- **HN Post:** [{post['title']}](https://news.ycombinator.com/item?id={post['id']})\n")
                if post.get('url'):
                    f.write(f"- **URL:** {post['url']}\n")
                f.write(f"- **Category:** {analysis['category']}\n")
                f.write(f"- **Stage:** {analysis['stage']}\n")
                f.write(f"- **AI Score:** {analysis['ai_score']}/10\n")
                f.write(f"- **HN Score:** {post.get('score', 0)} points, {post.get('descendants', 0)} comments\n\n")
                
                f.write(f"**Summary:** {analysis['summary']}\n\n")
                
                if analysis['key_features']:
                    f.write("**Key Features:**\n")
                    for feature in analysis['key_features']:
                        f.write(f"- {feature}\n")
                    f.write("\n")
                
                if analysis['target_audience']:
                    f.write(f"**Target Audience:** {analysis['target_audience']}\n\n")
                
                if analysis['why_interesting']:
                    f.write(f"**Why It's Interesting:** {analysis['why_interesting']}\n\n")
                
                f.write("---\n\n")
        
        return filepath
    
    def _json_report(self, startups: List[Dict], timestamp: str) -> str:
        """Generate JSON report"""
        filename = f"startup_report_{timestamp}.json"
        filepath = os.path.join(self.report_dir, filename)
        
        # Also save as latest.json for easy access
        latest_path = os.path.join(self.report_dir, "latest.json")
        
        # Separate startups and innovations
        startups_list = [s for s in startups if s['analysis']['type'] == 'startup']
        innovations_list = [s for s in startups if s['analysis']['type'] == 'innovation']
        
        report_data = {
            'metadata': {
                'timestamp': timestamp,
                'generated_at': datetime.now().isoformat(),
                'generated_at_ist': datetime.now(config.TIMEZONE).strftime("%B %d, %Y at %I:%M %p IST"),
                'total_discoveries': len(startups),
                'total_startups': len(startups_list),
                'total_innovations': len(innovations_list)
            },
            'discoveries': []
        }
        
        for startup_data in startups:
            post = startup_data['post']
            analysis = startup_data['analysis']
            
            report_data['discoveries'].append({
                'id': post['id'],
                'type': analysis['type'],
                'title': post['title'],
                'name': analysis['name'],
                'url': post.get('url'),
                'hn_url': f"https://news.ycombinator.com/item?id={post['id']}",
                'hn_score': post.get('score', 0),
                'hn_comments': post.get('descendants', 0),
                'posted_at': datetime.fromtimestamp(post['time']).isoformat(),
                'category': analysis['category'],
                'stage': analysis['stage'],
                'innovation_score': analysis['innovation_score'],
                'summary': analysis['summary'],
                'why_interesting': analysis['why_interesting'],
                'coolness_factor': analysis.get('coolness_factor', ''),
                'key_features': analysis.get('key_features', []),
                'target_audience': analysis.get('target_audience', ''),
                'technical_details': analysis.get('technical_details', ''),
                'business_model': analysis.get('business_model', ''),
                'founder_info': analysis.get('founder_info', '')
            })
        
        # Sort by innovation score
        report_data['discoveries'].sort(key=lambda x: x['innovation_score'], reverse=True)
        
        # Save both files
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        with open(latest_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def quick_summary(self, new_startups: int, total_processed: int):
        """Print a quick summary after a run"""
        self.console.print(f"\n[green][Success] Run completed successfully[/green]")
        self.console.print(f"  - Processed {total_processed} posts")
        self.console.print(f"  - Found {new_startups} new startups")

# AIDEV-TODO: Add email report functionality
# AIDEV-TODO: Add HTML report format with better styling