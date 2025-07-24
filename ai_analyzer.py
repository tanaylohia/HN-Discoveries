import json
from typing import Dict, Optional, List
from openai import AzureOpenAI
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
import config

# AIDEV-NOTE: AI analyzer using Azure OpenAI and DeepSeek for startup analysis
# Follows the configuration from CLAUDE.md

class AIAnalyzer:
    def __init__(self, use_deepseek: bool = False):
        self.use_deepseek = use_deepseek
        
        if use_deepseek:
            # Initialize DeepSeek client
            self.client = ChatCompletionsClient(
                endpoint=config.AZURE_DEEPSEEK_ENDPOINT,
                credential=AzureKeyCredential(config.AZURE_DEEPSEEK_API_KEY),
                api_version="2024-05-01-preview"
            )
            self.model_name = config.DEEPSEEK_MODEL
        else:
            # Initialize Azure OpenAI client
            self.client = AzureOpenAI(
                api_version=config.API_VERSION,
                azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
                api_key=config.AZURE_OPENAI_API_KEY,
            )
            self.deployment = config.GPT_4_1_DEPLOYMENT  # Using GPT-4.1 for better analysis
    
    def analyze_startup(self, post: Dict) -> Optional[Dict]:
        """
        Analyze a HN post to extract startup information
        
        Returns:
            Dict with analysis results or None if error
        """
        prompt = self._create_analysis_prompt(post)
        
        try:
            if self.use_deepseek:
                response = self._call_deepseek(prompt)
            else:
                response = self._call_openai(prompt)
            
            # Parse JSON response
            return self._parse_response(response)
            
        except Exception as e:
            print(f"Error analyzing post {post.get('id')}: {e}")
            return None
    
    def _create_analysis_prompt(self, post: Dict) -> str:
        """Create a structured prompt for startup analysis"""
        title = post.get('title', '')
        url = post.get('url', '')
        score = post.get('score', 0)
        comments = post.get('descendants', 0)
        
        prompt = f"""Analyze this Hacker News post to determine if it's about:
1. A NEW STARTUP ANNOUNCEMENT - MUST be founders/creators announcing their own new startup/company
2. A cool technical innovation (open source project, research, algorithm, tool, etc.)
3. Neither

Post Title: {title}
URL: {url}
Score: {score} points
Comments: {comments}

IMPORTANT STARTUP CRITERIA:
- MUST be a NEW startup announcement (not news about existing companies)
- MUST be posted by founders/team members (Show HN, Launch HN, or clear founder language like "we built", "we're launching")
- NOT general news, updates, or discussions about existing companies
- NOT job postings, funding news, or company pivots
- Examples of valid startups: "Show HN: We built X", "Launch HN: Company (YC S24)", "Introducing our new startup"
- Examples to REJECT: "Company X raises funding", "Company Y's new feature", "Why Company Z failed"

Please analyze and return a JSON response with the following structure:
{{
    "type": "startup" | "innovation" | "other",
    "confidence": 0.0-1.0,
    "name": "project/startup/innovation name",
    "category": "e.g., AI/ML, SaaS, Developer Tools, Programming Language, Algorithm, etc.",
    "stage": "e.g., idea, MVP, launched, funded, research, experimental",
    "summary": "1-2 sentence description",
    "key_features": ["feature1", "feature2"],
    "target_audience": "who this is for",
    "technical_details": "for innovations: what makes it technically interesting",
    "business_model": "for startups: if mentioned",
    "founder_info": "any creator/founder details",
    "funding_stage": "if mentioned",
    "why_interesting": "why this is noteworthy",
    "innovation_score": 0.0-10.0,
    "coolness_factor": "what makes this cool or innovative"
}}

Rate based on:
For startups: Innovation, market potential, team quality, traction, technical merit
For innovations: Technical novelty, usefulness, elegance, performance gains, community impact

Set type="startup" ONLY for genuine new startup announcements by founders.
Set type="other" if it's just news about existing companies or not a technical innovation."""

        return prompt
    
    def _call_openai(self, prompt: str) -> str:
        """Call Azure OpenAI API"""
        response = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert startup analyst. Analyze Hacker News posts to identify promising startups. Always respond with valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_completion_tokens=800,
            temperature=0.7,  # Balanced temperature for GPT-4.1
            model=self.deployment,
            response_format={"type": "json_object"}  # Force JSON response
        )
        
        return response.choices[0].message.content
    
    def _call_deepseek(self, prompt: str) -> str:
        """Call DeepSeek API"""
        response = self.client.complete(
            messages=[
                SystemMessage(content="You are an expert startup analyst. Analyze Hacker News posts to identify promising startups. Always respond with valid JSON."),
                UserMessage(content=prompt),
            ],
            max_tokens=800,
            model=self.model_name,
            temperature=0.3
        )
        
        return response.choices[0].message.content
    
    def _parse_response(self, response: str) -> Dict:
        """Parse and validate AI response"""
        try:
            data = json.loads(response)
            
            # Ensure required fields exist with defaults
            return {
                'type': data.get('type', 'other'),
                'is_startup': data.get('type') == 'startup',  # Backward compatibility
                'is_innovation': data.get('type') == 'innovation',
                'confidence': float(data.get('confidence', 0.0)),
                'name': data.get('name', data.get('startup_name', 'Unknown')),
                'startup_name': data.get('name', data.get('startup_name', 'Unknown')),  # Backward compatibility
                'category': data.get('category', 'Uncategorized'),
                'stage': data.get('stage', 'Unknown'),
                'summary': data.get('summary', ''),
                'key_features': data.get('key_features', []),
                'target_audience': data.get('target_audience', ''),
                'technical_details': data.get('technical_details', ''),
                'business_model': data.get('business_model', ''),
                'founder_info': data.get('founder_info', ''),
                'funding_stage': data.get('funding_stage', ''),
                'why_interesting': data.get('why_interesting', ''),
                'innovation_score': float(data.get('innovation_score', 0.0)),
                'ai_score': float(data.get('innovation_score', 0.0)),  # Backward compatibility
                'coolness_factor': data.get('coolness_factor', '')
            }
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing AI response: {e}")
            return None
    
    def batch_analyze(self, posts: List[Dict], max_batch: int = 10) -> List[Dict]:
        """
        Analyze multiple posts in batch
        
        Args:
            posts: List of posts to analyze
            max_batch: Maximum posts to analyze at once
        """
        results = []
        
        for i, post in enumerate(posts[:max_batch]):
            print(f"Analyzing post {i+1}/{min(len(posts), max_batch)}: {post.get('title', 'Unknown')}")
            
            analysis = self.analyze_startup(post)
            if analysis and analysis['type'] in ['startup', 'innovation']:
                results.append({
                    'post': post,
                    'analysis': analysis
                })
        
        return results

# AIDEV-TODO: Implement caching to avoid re-analyzing the same posts
# AIDEV-TODO: Add retry logic for API failures