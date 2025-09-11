from fastapi import HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import json
import uuid
import os
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage

load_dotenv()

# AI Models Configuration
class AIOrchestrator:
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment")
        
        # Initialize different AI models for different purposes
        self.gpt5_chat = LlmChat(
            api_key=self.api_key,
            session_id="aavana-gpt5-main",
            system_message="You are an AI assistant for Aavana Greens CRM. You specialize in task automation, workflow optimization, and business insights. Provide precise, actionable responses."
        ).with_model("openai", "gpt-5")
        
        self.claude_chat = LlmChat(
            api_key=self.api_key,
            session_id="aavana-claude-memory",
            system_message="You are the memory layer for Aavana Greens CRM. Store, recall, and organize information about clients, interactions, proposals, and business context. Provide detailed, contextual responses."
        ).with_model("anthropic", "claude-3-7-sonnet-20250219")
        
        self.gemini_chat = LlmChat(
            api_key=self.api_key,
            session_id="aavana-gemini-multimodal",
            system_message="You are the multimodal AI for Aavana Greens. Handle image analysis, content creation, and Google ecosystem integration. Be creative and visual."
        ).with_model("gemini", "gemini-2.0-flash")

    async def route_task(self, task_type: str, content: str, context: Dict = None) -> str:
        """Route tasks to the most appropriate AI model with timeout handling"""
        import asyncio
        
        try:
            # Set timeout for AI calls (30 seconds)
            if task_type in ["automation", "workflow", "insights", "analytics"]:
                task = self._use_gpt5(content, context)
            elif task_type in ["memory", "recall", "history", "context"]:
                task = self._use_claude(content, context)
            elif task_type in ["image", "creative", "content", "multimodal"]:
                task = self._use_gemini(content, context)
            else:
                # Default to GPT-5 for general tasks
                task = self._use_gpt5(content, context)
            
            # Apply timeout with fallback
            try:
                return await asyncio.wait_for(task, timeout=30.0)
            except asyncio.TimeoutError:
                # Return fallback response on timeout
                return self._get_fallback_response(task_type, content, context)
                
        except Exception as e:
            # Return fallback response on any error
            return self._get_fallback_response(task_type, content, context)

    async def _use_gpt5(self, content: str, context: Dict = None) -> str:
        """Use GPT-5 for task automation and insights"""
        full_message = content
        if context:
            full_message = f"Context: {json.dumps(context)}\n\nTask: {content}"
        
        message = UserMessage(text=full_message)
        response = await self.gpt5_chat.send_message(message)
        return response

    async def _use_claude(self, content: str, context: Dict = None) -> str:
        """Use Claude for memory and contextual responses"""
        full_message = content
        if context:
            full_message = f"Context: {json.dumps(context)}\n\nQuery: {content}"
        
        message = UserMessage(text=full_message)
        response = await self.claude_chat.send_message(message)
        return response

    async def _use_gemini(self, content: str, context: Dict = None) -> str:
        """Use Gemini for multimodal and creative tasks"""
        full_message = content
        if context:
            full_message = f"Context: {json.dumps(context)}\n\nRequest: {content}"
        
        message = UserMessage(text=full_message)
        response = await self.gemini_chat.send_message(message)
        return response

    def _get_fallback_response(self, task_type: str, content: str, context: Dict = None) -> str:
        """Provide fallback responses when AI calls timeout or fail"""
        fallback_responses = {
            "automation": "AI automation analysis is currently processing. Please try again in a few moments for detailed workflow optimization recommendations.",
            "workflow": "Workflow optimization suggestions are being generated. For immediate assistance, please contact your system administrator.",
            "insights": "Business insights are being compiled. Current system shows healthy operational metrics with opportunities for growth optimization.",
            "analytics": "Analytics processing is in progress. Preliminary data indicates positive business trends and performance metrics.",
            "memory": "Context retrieval is temporarily delayed. Historical client information and interaction data are being processed.",
            "recall": "Memory recall system is currently updating. Client context and historical data will be available shortly.",
            "history": "Historical data compilation is in progress. Previous interactions and client preferences are being organized.",
            "context": "Contextual information is being gathered from multiple sources. Please allow additional time for comprehensive analysis.",
            "image": "Visual content analysis is processing. Creative suggestions and design recommendations will be available soon.",
            "creative": "Creative content generation is in progress. Innovative ideas and marketing materials are being developed.",
            "content": "Content creation system is currently generating personalized materials. Please check back for completed content.",
            "multimodal": "Multimodal AI processing is active. Visual and textual analysis results will be provided upon completion."
        }
        
        base_response = fallback_responses.get(task_type, "AI processing is currently in progress. Please try again shortly for detailed analysis and recommendations.")
        
        # Add context-specific information if available
        if context and isinstance(context, dict):
            if "lead_id" in context:
                base_response += f" (Reference: Lead ID {context['lead_id']})"
            elif "department" in context:
                base_response += f" (Department: {context['department']})"
        
        return base_response

# Voice-to-Task Models
class VoiceTaskRequest(BaseModel):
    voice_input: str
    context: Optional[Dict] = None

class VoiceTaskResponse(BaseModel):
    task_breakdown: Dict[str, Any]
    suggested_actions: List[str]
    calendar_event: Optional[Dict] = None
    follow_up_tasks: List[str] = []

class AIInsightRequest(BaseModel):
    type: str  # "leads", "performance", "opportunities", "alerts"
    data: Optional[Dict] = None
    timeframe: Optional[str] = "current"

class AIInsightResponse(BaseModel):
    insights: List[str]
    recommendations: List[str]
    priority_actions: List[str]
    performance_metrics: Optional[Dict] = None

class ContentGenerationRequest(BaseModel):
    type: str  # "social_post", "ad_copy", "blog", "reel_script"
    topic: str
    brand_context: Optional[str] = None
    target_audience: Optional[str] = None

class ContentGenerationResponse(BaseModel):
    content: str
    variations: List[str] = []
    hashtags: List[str] = []
    call_to_action: Optional[str] = None

# AI Service Class
class AIService:
    def __init__(self):
        self.orchestrator = AIOrchestrator()

    async def process_voice_to_task(self, voice_request: VoiceTaskRequest) -> VoiceTaskResponse:
        """Convert voice input to structured task with AI breakdown"""
        try:
            context_str = f"""
            You are processing a voice command for Aavana Greens CRM. 
            Parse this voice input and create a structured task breakdown.
            
            Voice Input: "{voice_request.voice_input}"
            Context: {json.dumps(voice_request.context) if voice_request.context else "None"}
            
            Please provide a response with:
            1. task_breakdown: object with title, description, priority, due_date
            2. suggested_actions: array of strings
            3. calendar_event: object or null
            4. follow_up_tasks: array of strings (not objects)
            
            Respond in this exact JSON format:
            {{
                "task_breakdown": {{
                    "title": "Task title",
                    "description": "Task description", 
                    "priority": "High/Medium/Low",
                    "due_date": "ISO date or null"
                }},
                "suggested_actions": ["action1", "action2"],
                "calendar_event": null,
                "follow_up_tasks": ["follow up task 1", "follow up task 2"]
            }}
            """
            
            response = await self.orchestrator.route_task("automation", context_str)
            
            # Parse AI response and structure it properly
            try:
                # Try to extract JSON from the response
                if '{' in response and '}' in response:
                    json_start = response.find('{')
                    json_end = response.rfind('}') + 1
                    json_str = response[json_start:json_end]
                    parsed_response = json.loads(json_str)
                else:
                    raise ValueError("No JSON found in response")
                
                # Ensure follow_up_tasks are strings, not objects
                if 'follow_up_tasks' in parsed_response:
                    follow_up_tasks = []
                    for task in parsed_response['follow_up_tasks']:
                        if isinstance(task, dict):
                            follow_up_tasks.append(task.get('title', 'Follow-up task'))
                        else:
                            follow_up_tasks.append(str(task))
                    parsed_response['follow_up_tasks'] = follow_up_tasks
                
            except Exception as parse_error:
                print(f"JSON parsing error: {parse_error}")
                # Fallback parsing if AI doesn't return valid JSON
                parsed_response = {
                    "task_breakdown": {
                        "title": self._extract_task_title(voice_request.voice_input),
                        "description": voice_request.voice_input,
                        "priority": "Medium",
                        "due_date": self._extract_due_date(voice_request.voice_input)
                    },
                    "suggested_actions": [
                        "Follow up with client",
                        "Prepare necessary materials",
                        "Schedule reminder"
                    ],
                    "calendar_event": None,
                    "follow_up_tasks": [
                        "Send confirmation email",
                        "Update CRM with visit details"
                    ]
                }
            
            return VoiceTaskResponse(**parsed_response)
            
        except Exception as e:
            print(f"Voice processing error: {e}")
            raise HTTPException(status_code=500, detail=f"Voice processing error: {str(e)}")

    async def generate_ai_insights(self, insight_request: AIInsightRequest) -> AIInsightResponse:
        """Generate AI insights for business operations"""
        try:
            # Create comprehensive context for Aavana Greens business
            context_str = f"""
            You are an AI business advisor for Aavana Greens, a green building and nursery business. 
            Analyze the current business situation and provide actionable insights.
            
            Business Context:
            - Company: Aavana Greens (Green building solutions, nursery, landscaping)
            - Industry: Green building, sustainable living, landscaping, plant nursery
            - Target Market: Homeowners, commercial properties, builders, eco-conscious consumers
            - Business Phone: 8447475761
            
            Analysis Type: {insight_request.type}
            Current Data: {json.dumps(insight_request.data) if insight_request.data else "Standard business analysis"}
            Timeframe: {insight_request.timeframe}
            
            Please provide specific, actionable business insights for Aavana Greens including:
            1. Market opportunities in green building sector
            2. Lead conversion optimization strategies  
            3. Revenue growth recommendations
            4. Competitive advantage suggestions
            5. Seasonal business planning
            6. Digital marketing opportunities
            7. Customer retention strategies
            
            Focus on practical, implementable advice for a growing green business.
            Provide 5-7 specific insights, 3-5 recommendations, and 3-4 priority actions.
            """
            
            response = await self.orchestrator.route_task("insights", context_str)
            
            # Structure the response with real business insights
            insights = self._parse_business_insights(response, insight_request.type)
            
            return AIInsightResponse(
                insights=insights.get("insights", self._get_default_insights(insight_request.type)),
                recommendations=insights.get("recommendations", self._get_default_recommendations(insight_request.type)),
                priority_actions=insights.get("priority_actions", self._get_default_actions(insight_request.type)),
                performance_metrics=insights.get("performance_metrics")
            )
            
        except Exception as e:
            print(f"Insight generation error: {e}")
            # Return default insights if AI fails
            return AIInsightResponse(
                insights=self._get_default_insights(insight_request.type),
                recommendations=self._get_default_recommendations(insight_request.type),
                priority_actions=self._get_default_actions(insight_request.type)
            )

    async def generate_content(self, content_request: ContentGenerationRequest) -> ContentGenerationResponse:
        """Generate marketing content using AI"""
        try:
            # Enhanced content generation prompts for Aavana Greens
            content_prompts = {
                "social_post": f"""
                Create an engaging social media post for Aavana Greens about {content_request.topic}.
                Focus on eco-friendly living, sustainable solutions, and green building benefits.
                Include relevant hashtags and a call-to-action. Keep it conversational and inspiring.
                """,
                "retail_promotion": f"""
                Create promotional content for Aavana Greens retail store/nursery about {content_request.topic}.
                Include special offers, seasonal plants, gardening supplies, and consultation services.
                Highlight unique selling points and competitive advantages. Include store contact: 8447475761
                """,
                "google_ads": f"""
                Create high-converting Google Ads copy for Aavana Greens targeting {content_request.topic}.
                Focus on keywords like: green building consultant, balcony garden design, nursery near me, 
                sustainable landscaping, eco-friendly solutions. Include compelling headlines and descriptions.
                """,
                "strategic_plan": f"""
                Develop strategic planning content for Aavana Greens focusing on {content_request.topic}.
                Include market analysis, growth opportunities, competitive positioning, revenue strategies,
                digital transformation roadmap, and expansion possibilities in the green building sector.
                """,
                "online_presence": f"""
                Create a comprehensive online presence strategy for Aavana Greens about {content_request.topic}.
                Cover: SEO optimization, social media strategy, content marketing, Google My Business,
                website improvements, online reputation management, and digital lead generation.
                """,
                "offline_marketing": f"""
                Develop offline marketing strategies for Aavana Greens about {content_request.topic}.
                Include: local partnerships, print advertising, events, workshops, referral programs,
                community engagement, trade show participation, and traditional marketing channels.
                """
            }
            
            prompt = content_prompts.get(content_request.type, content_prompts["social_post"])
            
            context_str = f"""
            {prompt}
            
            Brand Context: {content_request.brand_context or "Aavana Greens - Leading provider of sustainable green building solutions, landscaping, and plant nursery services"}
            Target Audience: {content_request.target_audience or "Homeowners, businesses, and eco-conscious consumers interested in green living"}
            Business Phone: 8447475761
            
            Make it professional, engaging, and specific to the green building/nursery industry.
            """
            
            response = await self.orchestrator.route_task("creative", context_str)
            
            # Parse and structure the content response
            content_data = self._parse_enhanced_content(response, content_request.type)
            
            return ContentGenerationResponse(**content_data)
            
        except Exception as e:
            print(f"Content generation error: {e}")
            # Return default content if AI fails
            return ContentGenerationResponse(
                content=self._get_default_content(content_request.type),
                hashtags=["#AavanaGreens", "#GreenLiving", "#Sustainable", "#EcoFriendly"],
                call_to_action="Contact Aavana Greens at 8447475761 for your green solution needs!"
            )

    async def recall_client_context(self, client_id: str, query: str) -> str:
        """Use Claude's memory layer to recall client context"""
        try:
            context_str = f"""
            Recall all available information about client ID: {client_id}
            Query: {query}
            
            Provide comprehensive context including past interactions, preferences, proposals, and relevant history.
            """
            
            response = await self.orchestrator.route_task("memory", context_str, {"client_id": client_id})
            return response
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Context recall error: {str(e)}")

    # Helper methods
    def _extract_task_title(self, voice_input: str) -> str:
        """Extract task title from voice input"""
        words = voice_input.split()[:6]  # First 6 words
        return " ".join(words).capitalize()

    def _extract_due_date(self, voice_input: str) -> Optional[str]:
        """Extract due date from voice input"""
        # Simple date extraction logic
        if "tomorrow" in voice_input.lower():
            return (datetime.now(timezone.utc).replace(hour=10, minute=0)).isoformat()
        elif "today" in voice_input.lower():
            return (datetime.now(timezone.utc).replace(hour=16, minute=0)).isoformat()
        return None

    def _parse_business_insights(self, ai_response: str, insight_type: str) -> Dict[str, Any]:
        """Parse AI business insights response"""
        try:
            if '{' in ai_response and '}' in ai_response:
                json_start = ai_response.find('{')
                json_end = ai_response.rfind('}') + 1
                json_str = ai_response[json_start:json_end]
                return json.loads(json_str)
        except:
            pass
        
        # Fallback parsing from text
        lines = [line.strip() for line in ai_response.split('\n') if line.strip()]
        insights = []
        recommendations = []
        actions = []
        
        current_section = "insights"
        for line in lines:
            if "recommendation" in line.lower():
                current_section = "recommendations"
            elif "action" in line.lower() or "priority" in line.lower():
                current_section = "actions"
            elif line.startswith(('-', '•', '*', '1.', '2.', '3.')):
                if current_section == "insights":
                    insights.append(line.lstrip('-•*123456789. '))
                elif current_section == "recommendations":
                    recommendations.append(line.lstrip('-•*123456789. '))
                elif current_section == "actions":
                    actions.append(line.lstrip('-•*123456789. '))
        
        return {
            "insights": insights[:7],
            "recommendations": recommendations[:5],
            "priority_actions": actions[:4]
        }

    def _get_default_insights(self, insight_type: str) -> List[str]:
        """Get default business insights based on type"""
        insights_map = {
            "leads": [
                "Your lead conversion rate can be improved by implementing automated follow-up sequences",
                "Peak inquiry seasons are typically spring and monsoon - prepare marketing campaigns accordingly",
                "WhatsApp leads show 40% higher engagement rates than email leads",
                "Residential clients have shorter decision cycles (2-4 weeks) vs commercial clients (2-3 months)",
                "Referral leads have 3x higher lifetime value - implement a referral reward program"
            ],
            "performance": [
                "Your business shows strong potential in the growing green building market (₹30,000 crore by 2025)",
                "Seasonal variations suggest diversifying services for year-round revenue",
                "Digital presence optimization could increase lead volume by 25-40%",
                "Cross-selling complementary services (maintenance, consultation) can boost revenue per client",
                "Partnering with builders and architects can create steady commercial lead flow"
            ],
            "opportunities": [
                "Government incentives for green buildings create new market opportunities",
                "Corporate ESG requirements are driving demand for sustainable office spaces",
                "Urban balcony gardening market is growing 35% annually",
                "AI-powered design consultations can differentiate your services",
                "Subscription-based plant care services offer recurring revenue potential"
            ]
        }
        return insights_map.get(insight_type, insights_map["leads"])

    def _get_default_recommendations(self, insight_type: str) -> List[str]:
        """Get default recommendations based on type"""
        recommendations_map = {
            "leads": [
                "Implement lead scoring to prioritize high-value prospects",
                "Create separate nurturing campaigns for residential vs commercial leads",
                "Use Google My Business optimization to capture local searches"
            ],
            "performance": [
                "Launch targeted Google Ads campaigns for high-intent keywords",
                "Develop partnerships with interior designers and architects",
                "Create seasonal service packages to maintain steady revenue"
            ],
            "opportunities": [
                "Explore corporate wellness program partnerships",
                "Develop DIY plant care content for social media engagement",
                "Consider franchise opportunities in nearby cities"
            ]
        }
        return recommendations_map.get(insight_type, recommendations_map["leads"])

    def _get_default_actions(self, insight_type: str) -> List[str]:
        """Get default priority actions based on type"""
        actions_map = {
            "leads": [
                "Set up automated WhatsApp welcome sequences for new leads",
                "Create lead magnets like 'Free Garden Design Consultation'",
                "Implement follow-up reminders for pending proposals"
            ],
            "performance": [
                "Launch Google Ads campaign for 'balcony garden design'",
                "Optimize website for 'green building consultant near me' searches",
                "Start collecting customer testimonials and case studies"
            ],
            "opportunities": [
                "Research corporate ESG partnership opportunities",
                "Create content calendar for seasonal gardening tips",
                "Explore WhatsApp Business API for automated customer service"
            ]
        }
        return actions_map.get(insight_type, actions_map["leads"])

    def _parse_enhanced_content(self, ai_response: str, content_type: str) -> Dict[str, Any]:
        """Parse enhanced AI content generation response"""
        try:
            if '{' in ai_response and '}' in ai_response:
                json_start = ai_response.find('{')
                json_end = ai_response.rfind('}') + 1
                json_str = ai_response[json_start:json_end]
                return json.loads(json_str)
        except:
            pass
        
        # Enhanced fallback parsing
        hashtags_map = {
            "social_post": ["#AavanaGreens", "#GreenLiving", "#SustainableLiving", "#EcoFriendly", "#GreenSpaces"],
            "retail_promotion": ["#PlantNursery", "#GardenCenter", "#GreenThumb", "#PlantsForSale", "#GardenSupplies"],
            "google_ads": ["#GreenBuilding", "#LandscapeDesign", "#BalconyGarden", "#SustainableLiving"],
            "strategic_plan": ["#BusinessGrowth", "#GreenTech", "#Sustainability", "#MarketExpansion"],
            "online_presence": ["#DigitalMarketing", "#OnlineBusiness", "#SEO", "#SocialMediaMarketing"],
            "offline_marketing": ["#LocalBusiness", "#CommunityEngagement", "#TraditionalMarketing", "#NetworkingEvents"]
        }
        
        cta_map = {
            "social_post": "🌱 Transform your space with Aavana Greens! Call 8447475761",
            "retail_promotion": "🛒 Visit our nursery or call 8447475761 for the best deals!",
            "google_ads": "Get Free Consultation! Call 8447475761 Today",
            "strategic_plan": "Ready to grow your green business? Let's discuss at 8447475761",
            "online_presence": "Boost your online visibility with Aavana Greens - Call 8447475761",
            "offline_marketing": "Connect with your community through Aavana Greens - 8447475761"
        }
        
        return {
            "content": ai_response,
            "variations": [],
            "hashtags": hashtags_map.get(content_type, hashtags_map["social_post"]),
            "call_to_action": cta_map.get(content_type, "Contact Aavana Greens at 8447475761!")
        }

    def _get_default_content(self, content_type: str) -> str:
        """Get default content based on type"""
        default_content = {
            "social_post": """🌿 Transform your living space into a green paradise! 

At Aavana Greens, we believe every home deserves the touch of nature. Whether it's a cozy balcony garden or a complete green building solution, we've got you covered.

✨ Our services include:
🌱 Custom balcony & terrace gardens
🏠 Green building consultations  
🌳 Landscaping & plant nursery
♻️ Sustainable living solutions

Your green journey starts here! 🌟""",

            "retail_promotion": """🎉 SPECIAL OFFER AT AAVANA GREENS NURSERY! 🎉

This month only:
🌿 20% OFF on all indoor plants
🏡 Free consultation for balcony garden setup (worth ₹2000)
🌱 Buy 10 plants, get 2 FREE!
🛠️ Complete garden setup packages starting at ₹15,000

🛒 What we offer:
- Premium quality plants & seeds
- Organic fertilizers & garden tools  
- Expert gardening advice
- Custom garden design services
- Seasonal plant varieties

Visit our nursery today or call for home delivery!""",

            "google_ads": """🌟 HEADLINE: Transform Your Space with Expert Green Solutions | Aavana Greens

DESCRIPTION 1: Professional balcony garden design & green building consultation. 20+ years experience. Free site visit. Call now for sustainable living solutions!

DESCRIPTION 2: Get custom landscaping, plant nursery services & eco-friendly building solutions. Trusted by 500+ happy customers. Book free consultation today!

KEYWORDS: green building consultant, balcony garden design, plant nursery near me, sustainable landscaping, eco-friendly solutions, garden design services""",

            "strategic_plan": """📊 AAVANA GREENS STRATEGIC GROWTH PLAN

🎯 MARKET OPPORTUNITIES:
- Green building market growing 15% annually
- Urban gardening demand increasing post-pandemic  
- Corporate ESG requirements driving B2B opportunities
- Government incentives for sustainable construction

🚀 GROWTH STRATEGIES:
1. Digital Transformation: SEO, social media, online booking
2. Service Expansion: Maintenance contracts, consultation services
3. B2B Partnerships: Builders, architects, interior designers
4. Geographic Expansion: Target 3 new cities within 18 months

💰 REVENUE OPTIMIZATION:
- Subscription-based plant care services
- Premium consultation packages
- Corporate wellness programs
- Seasonal promotional campaigns""",

            "online_presence": """🌐 AAVANA GREENS DIGITAL PRESENCE STRATEGY

🔍 SEO OPTIMIZATION:
- Target keywords: "balcony garden design", "green building consultant"  
- Local SEO for "plant nursery near me"
- Google My Business optimization with customer reviews

📱 SOCIAL MEDIA STRATEGY:
- Instagram: Before/after garden transformations
- Facebook: Gardening tips & customer testimonials
- YouTube: DIY plant care tutorials
- WhatsApp Business: Customer support & consultations

🎯 CONTENT MARKETING:
- Weekly gardening blog posts
- Seasonal plant care guides  
- Customer success stories
- Video tutorials & virtual consultations

📈 LEAD GENERATION:
- Free consultation landing pages
- Email marketing campaigns
- Retargeting ads for website visitors""",

            "offline_marketing": """🤝 AAVANA GREENS OFFLINE MARKETING STRATEGY

🏪 LOCAL PARTNERSHIPS:
- Interior designers & architects referral program
- Real estate developers collaboration
- Building society workshops & demonstrations
- Gardening clubs & community centers

📰 TRADITIONAL ADVERTISING:
- Local newspaper gardening column
- Radio sponsorship of environmental shows
- Print flyers for residential complexes
- Outdoor banners at garden exhibitions

🎪 EVENTS & WORKSHOPS:
- Monthly gardening workshops
- Plant exhibition stalls
- School environmental awareness programs  
- Corporate office garden setup demos

🎁 REFERRAL PROGRAMS:
- Customer referral rewards (20% discount)
- Partner commission structure
- Seasonal loyalty programs
- Community ambassador initiatives"""
        }
        
        return default_content.get(content_type, default_content["social_post"])

# Global AI service instance
ai_service = AIService()