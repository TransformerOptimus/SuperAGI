"""
Prompts for Sales Agent
"""


SALES_AGENT_SYSTEM_PROMPT = """You are Alisha, an expert AI Sales Development Representative (SDR) specialized in B2B outreach and lead generation.

Your primary objectives are:
1. Find qualified leads that match the ideal customer profile
2. Research companies thoroughly to understand their needs and pain points
3. Craft highly personalized outreach emails with strong relevance
4. Track responses and send intelligent follow-ups
5. Book meetings with interested prospects

Key principles:
- Always research before reaching out
- Personalize every message with company-specific insights
- Focus on providing value, not just selling
- Be professional, concise, and respectful
- Track all interactions and learn from responses

Available tools:
{tools_description}

Current goals:
{goals}

Constraints:
{constraints}

Instructions:
{instructions}
"""


LEAD_RESEARCH_PROMPT = """Research the following company and prospect to gather personalized outreach information:

Company: {company}
Prospect: {name}
Title: {title}
Company Domain: {domain}

Find and summarize:
1. Recent company news, achievements, or funding
2. Company's main products/services and value proposition
3. Potential pain points or challenges they might face
4. Any relevant industry trends or competitive landscape
5. Specific angles for personalized outreach

Provide a concise summary (2-3 paragraphs) focusing on actionable insights for email personalization.
"""


EMAIL_GENERATION_PROMPT = """Based on the research findings, craft a personalized cold outreach email:

Prospect Information:
- Name: {name}
- Title: {title}
- Company: {company}

Research Summary:
{research_summary}

Our Value Proposition:
{value_proposition}

Email Requirements:
1. Personalized subject line (5-8 words)
2. Brief introduction mentioning specific company insight
3. Clear value proposition relevant to their role
4. Specific call-to-action (book a call)
5. Professional and conversational tone
6. Keep under 150 words

Generate the email in this format:
SUBJECT: [subject line]

BODY:
[email body]
"""


FOLLOW_UP_EMAIL_PROMPT = """Create a follow-up email for a prospect who hasn't responded:

Previous Email:
{previous_email}

Days Since Last Email: {days_elapsed}

Generate a brief follow-up that:
1. References the previous email
2. Adds new value or insight
3. Makes it easy to respond
4. Stays professional and not pushy
5. Keep under 100 words

Format:
SUBJECT: [subject line]

BODY:
[email body]
"""


RESPONSE_ANALYSIS_PROMPT = """Analyze this email response from a prospect:

From: {from_email}
Subject: {subject}
Body:
{body}

Determine:
1. Sentiment: POSITIVE / NEUTRAL / NEGATIVE
2. Intent: INTERESTED / NOT_INTERESTED / NEEDS_MORE_INFO / OUT_OF_OFFICE
3. Next Action: BOOK_MEETING / SEND_INFO / FOLLOW_UP_LATER / DISQUALIFY
4. Suggested Response: [Brief suggestion]

Provide analysis in JSON format.
"""


LEAD_SCORING_PROMPT = """Score this lead based on fit criteria:

Lead Information:
- Company: {company}
- Title: {title}
- Company Size: {company_size}
- Industry: {industry}
- Location: {location}

Ideal Customer Profile:
{ideal_customer_profile}

Score from 0-100 based on:
1. Title match (0-25 points)
2. Company size fit (0-25 points)
3. Industry relevance (0-25 points)
4. Geographic fit (0-15 points)
5. Additional signals (0-10 points)

Provide score and brief reasoning.
"""


def get_system_prompt(goals: list, constraints: list, instructions: str, tools_description: str) -> str:
    """Generate system prompt with agent configuration"""
    return SALES_AGENT_SYSTEM_PROMPT.format(
        goals="\n".join([f"- {goal}" for goal in goals]),
        constraints="\n".join([f"- {constraint}" for constraint in constraints]),
        instructions=instructions,
        tools_description=tools_description
    )
