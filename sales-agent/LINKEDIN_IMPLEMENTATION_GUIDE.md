# LinkedIn Tool - Implementation Guide

## 🚀 Quick Start

This guide will help you set up LinkedIn automation for your sales agent in 30 minutes.

---

## 📋 Prerequisites

1. **LinkedIn Account**
   - Premium recommended (higher limits)
   - Complete profile (100%)
   - Verified email and phone
   - Good standing (no previous violations)

2. **PhantomBuster Account** (Recommended)
   - Sign up at https://phantombuster.com
   - Start with $56/month plan
   - Get API key from settings

3. **Alternative**: Browser Automation
   - Advanced users only
   - Requires Selenium/Playwright knowledge
   - Higher risk of suspension

---

## ⚙️ Setup (5 minutes)

### Step 1: Get PhantomBuster API Key

```bash
# 1. Sign up at https://phantombuster.com
# 2. Go to Settings → API
# 3. Copy your API key
```

### Step 2: Configure Phantoms

Create these Phantoms in your PhantomBuster dashboard:

**1. LinkedIn Network Booster** (for connection requests)
   - Go to Phantoms → Create → Search "LinkedIn Network Booster"
   - Copy the Phantom ID from URL

**2. LinkedIn Message Sender** (for messages)
   - Create → Search "LinkedIn Message Sender"
   - Copy Phantom ID

**3. LinkedIn Profile Visitor** (for profile visits)
   - Create → Search "LinkedIn Profile Scraper"
   - Copy Phantom ID

**4. LinkedIn Search Export** (for lead search)
   - Create → Search "LinkedIn Search Export"
   - Copy Phantom ID

### Step 3: Update Configuration

Edit `.env` file:

```bash
# PhantomBuster Configuration
PHANTOMBUSTER_API_KEY=your_api_key_here

# Phantom IDs (copy from PhantomBuster dashboard)
PHANTOMBUSTER_LINKEDIN_NETWORK_BOOSTER_ID=phantom_id_1
PHANTOMBUSTER_LINKEDIN_MESSAGE_SENDER_ID=phantom_id_2
PHANTOMBUSTER_LINKEDIN_PROFILE_VISITOR_ID=phantom_id_3
PHANTOMBUSTER_LINKEDIN_SEARCH_EXPORT_ID=phantom_id_4

# LinkedIn Credentials (for browser automation - optional)
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password
```

### Step 4: Install Dependencies

```bash
cd sales-agent
pip install phantombuster requests
```

---

## 💻 Usage Examples

### Example 1: Send Connection Request

```python
from tools.linkedin.connection_tool import LinkedInConnectionTool

# Initialize tool
linkedin = LinkedInConnectionTool(provider="phantombuster")

# Send connection request
result = linkedin.execute(
    profile_url="https://linkedin.com/in/johnsmith",
    message="Hi John, I noticed we both work in SaaS sales. Would love to connect!",
    include_note=True
)

print(result)
# Output:
# {
#     "success": True,
#     "message": "Connection request sent successfully",
#     "profile_url": "https://linkedin.com/in/johnsmith",
#     "note_included": True
# }
```

### Example 2: Send Message to Connection

```python
from tools.linkedin.message_tool import LinkedInMessageTool

linkedin_msg = LinkedInMessageTool(provider="phantombuster")

result = linkedin_msg.execute(
    profile_url="https://linkedin.com/in/johnsmith",
    message="""Hi John,

I saw your recent post about sales automation. We're helping companies like yours increase outbound efficiency by 5x.

Would you be open to a quick 15-min chat this week?

Best,
Sarah""",
    is_inmail=False  # Set to True for InMail
)
```

### Example 3: Visit Profile

```python
from tools.linkedin.visit_tool import LinkedInProfileVisitTool

visit_tool = LinkedInProfileVisitTool(provider="phantombuster")

result = visit_tool.execute(
    profile_url="https://linkedin.com/in/johnsmith"
)

# This creates a "who viewed your profile" notification
```

### Example 4: Search for Prospects

```python
from tools.linkedin.search_tool import LinkedInSearchTool

search_tool = LinkedInSearchTool(provider="phantombuster")

profiles = search_tool.execute(
    title="VP of Sales",
    location="San Francisco Bay Area",
    industry="Computer Software",
    limit=25
)

for profile in profiles:
    print(f"{profile['name']} - {profile['title']} at {profile['company']}")
```

### Example 5: Check Responses

```python
from tools.linkedin.response_tool import LinkedInResponseTool

response_tool = LinkedInResponseTool(provider="phantombuster")

responses = response_tool.execute(since_hours=24)

print(f"New connections: {responses['total_new_connections']}")
print(f"New messages: {responses['total_new_messages']}")
print(f"Pending requests: {responses['total_pending']}")
```

---

## 🔄 Multi-Channel Workflow Integration

### Update Agent Configuration

```python
# Update agent to include LinkedIn tools
agent_data = {
    "name": "Multi-Channel Sales Agent",
    "tools": [
        "apollo_search",
        "google_search",
        "send_email",
        "read_email",
        "linkedin_send_connection",  # NEW
        "linkedin_send_message",      # NEW
        "linkedin_visit_profile",     # NEW
        "linkedin_search"             # NEW
    ],
    "goals": [
        "Find qualified leads via Apollo and LinkedIn",
        "Research prospects thoroughly",
        "Execute multi-channel outreach (Email + LinkedIn)",
        "Track engagement across all channels",
        "Book discovery calls"
    ]
}
```

### Multi-Channel Sequence Example

```python
from agent.multi_channel_executor import MultiChannelExecutor
from models import Lead

# Create lead
lead = Lead(
    email="john@company.com",
    linkedin_url="https://linkedin.com/in/johnsmith",
    first_name="John",
    company="Acme Corp"
)

# Execute sequence
executor = MultiChannelExecutor(lead, sequence="linkedin_first")

# Day 1: LinkedIn visit
executor.linkedin_visit(lead.linkedin_url)

# Day 2: LinkedIn connection
executor.linkedin_connect(
    profile_url=lead.linkedin_url,
    message=f"Hi {lead.first_name}, noticed we're both in SaaS. Let's connect!"
)

# Day 5: Email outreach (if not connected)
if not executor.is_connected():
    executor.send_email(
        to=lead.email,
        subject=f"Quick question, {lead.first_name}",
        body=executor.generate_email()
    )

# Day 8: LinkedIn message (if connected)
if executor.is_connected():
    executor.linkedin_message(
        profile_url=lead.linkedin_url,
        message=executor.generate_linkedin_message()
    )
```

---

## 📊 Rate Limits & Safety

### Built-in Rate Limiting

The LinkedIn tools have built-in rate limiting:

```python
from tools.linkedin.rate_limiter import LinkedInRateLimiter

limiter = LinkedInRateLimiter()

# Check if action is allowed
can_perform, reason = limiter.can_perform_action("connection_request")

if can_perform:
    # Send connection request
    pass
else:
    print(f"Cannot perform action: {reason}")

# Get current usage stats
stats = limiter.get_stats("connection_request")
print(f"Used today: {stats['connection_request']['last_day']}/20")
```

### Default Limits (Conservative)

```python
LIMITS = {
    "connection_request": {
        "per_day": 20,
        "per_week": 100,
        "min_delay": 120  # 2 minutes
    },
    "message": {
        "per_day": 50,
        "per_hour": 20,
        "min_delay": 60  # 1 minute
    },
    "profile_visit": {
        "per_day": 80,
        "per_hour": 40,
        "min_delay": 30  # 30 seconds
    }
}
```

### Warmup Schedule

For new accounts, start slow:

```python
from tools.linkedin.rate_limiter import WarmupScheduler

warmup = WarmupScheduler(start_date=datetime.utcnow())

limits = warmup.get_current_limits()
print(limits)
# Week 1: {"connections": 5, "messages": 10, "visits": 20}
# Week 2: {"connections": 10, "messages": 20, "visits": 40}
# Week 3: {"connections": 15, "messages": 35, "visits": 60}
# Week 4+: {"connections": 20, "messages": 50, "visits": 80}
```

---

## 🎯 Best Practices

### 1. Connection Requests

**DO:**
✅ Personalize every note
✅ Mention common connections or interests
✅ Keep it under 300 characters
✅ Send during business hours
✅ Target relevant prospects only

**DON'T:**
❌ Send generic "I'd like to connect" requests
❌ Spam everyone in your search results
❌ Send more than 20/day
❌ Use templates with [NAME] placeholders
❌ Send requests late at night

**Example Good Note:**
```
Hi Sarah, I saw your post about sales automation at Enterprise SaaS Summit.
We're helping companies like Acme Corp increase pipeline by 3x. Let's connect!
```

**Example Bad Note:**
```
Hi, I'd like to add you to my professional network on LinkedIn.
```

### 2. Messages

**DO:**
✅ Wait 2-3 days after connection acceptance
✅ Reference their profile/posts
✅ Provide value upfront
✅ Keep it conversational
✅ Include clear CTA

**DON'T:**
❌ Pitch immediately after connecting
❌ Send generic copy-paste messages
❌ Write long essays
❌ Be pushy or aggressive
❌ Use hard sales language

**Example Good Message:**
```
Hey John,

Thanks for connecting! I noticed you're focused on scaling sales ops at Acme.

We just helped a similar company (TechCo) reduce their SDR ramp time by 60% using
AI-powered automation.

Would you be open to a quick 15-min chat to see if there's a fit?

Cheers,
Sarah
```

### 3. Profile Visits

**Strategy:**
- Visit profiles 1-2 days before connection request
- Creates awareness ("who viewed your profile")
- Warms up cold prospects
- Don't overdo it (max 80/day)

### 4. Search Quality

**Target Precisely:**
```python
# Good: Specific targeting
search_tool.execute(
    title="VP of Sales",
    location="San Francisco Bay Area",
    company="Series B SaaS",
    limit=25
)

# Bad: Too broad
search_tool.execute(
    keywords="sales",
    limit=1000  # Too many
)
```

---

## ⚠️ Safety & Compliance

### LinkedIn's Perspective

❗ **Important**: LinkedIn automation technically violates their Terms of Service

**Risks:**
- Account warning
- Temporary restriction
- Permanent suspension

**Mitigation Strategies:**

1. **Use Premium Account**
   - Higher limits
   - More credibility
   - Better support

2. **Stay Conservative**
   - Don't max out daily limits
   - Use lower-than-allowed numbers
   - Random delays between actions

3. **Be Human-like**
   - Mix activity types
   - Don't automate 24/7
   - Take weekends off
   - Vary messaging times

4. **Monitor Metrics**
   - Connection acceptance rate > 30%
   - Message response rate > 10%
   - Report rate < 1%

5. **Quality Over Quantity**
   - Target precisely
   - Personalize thoroughly
   - Provide value

### Warning Signs

🚨 **Stop immediately if you see:**
- "Unusual activity" warning
- CAPTCHA on login
- Email about policy violation
- Restricted account features

**Recovery Steps:**
1. Stop all automation
2. Use LinkedIn manually for 1-2 weeks
3. Complete profile verification
4. Contact LinkedIn support if needed

---

## 🐛 Troubleshooting

### Issue: PhantomBuster Not Working

**Solution:**
```bash
# Check API key
echo $PHANTOMBUSTER_API_KEY

# Test connection
python examples/test_linkedin.py

# Check Phantom status
# Go to PhantomBuster dashboard → Phantoms → Check logs
```

### Issue: Rate Limit Errors

**Solution:**
```python
# Check current usage
from tools.linkedin.rate_limiter import LinkedInRateLimiter

limiter = LinkedInRateLimiter()
stats = limiter.get_stats()
print(stats)

# Reset if needed (testing only)
limiter.reset_action_type("connection_request")
```

### Issue: Connection Requests Not Sending

**Possible Causes:**
1. Phantom not configured correctly
2. LinkedIn session expired
3. Profile URL invalid
4. Already connected

**Debug:**
```python
result = linkedin.execute(
    profile_url="https://linkedin.com/in/test",
    message="Test",
    include_note=True
)

print(result)  # Check error message
```

### Issue: Low Acceptance Rate

**Solutions:**
- Improve connection note personalization
- Target more relevant prospects
- Visit profiles first
- Check if profile is complete and professional

---

## 📈 Performance Monitoring

### Track Key Metrics

```python
from models import Lead
from sqlalchemy import func

# Connection acceptance rate
total_sent = db.query(Lead).filter(
    Lead.linkedin_connection_sent_at != None
).count()

total_accepted = db.query(Lead).filter(
    Lead.linkedin_connected == True
).count()

acceptance_rate = (total_accepted / total_sent) * 100
print(f"Acceptance rate: {acceptance_rate}%")

# Message response rate
total_messages = db.query(Lead).filter(
    Lead.linkedin_last_message_at != None
).count()

total_replies = db.query(Lead).filter(
    Lead.linkedin_message_replied == True
).count()

response_rate = (total_replies / total_messages) * 100
print(f"Response rate: {response_rate}%")
```

### Optimize Based on Data

**If acceptance rate < 20%:**
- Improve personalization
- Target more precisely
- Add mutual connections

**If response rate < 10%:**
- Improve message quality
- Add more value upfront
- Reference their content
- Softer CTA

---

## 🎓 Next Steps

1. **Start Small**
   - 5 connections/day for week 1
   - Test different messaging
   - Monitor acceptance rates

2. **Scale Gradually**
   - Increase to 10/day week 2
   - Add profile visits
   - Start messaging connections

3. **Optimize**
   - A/B test connection notes
   - Track which messages get responses
   - Refine targeting

4. **Integrate with Email**
   - Build multi-channel sequences
   - Coordinate touchpoints
   - Track cross-channel attribution

5. **Advanced Features**
   - Build custom workflows
   - Add CRM integration
   - Implement scoring

---

## 📚 Additional Resources

- [PhantomBuster Documentation](https://docs.phantombuster.com/)
- [LinkedIn Automation Best Practices](https://www.linkedin.com/help/linkedin)
- [Sales Agent Architecture](./ARCHITECTURE.md)
- [LinkedIn Integration Plan](./LINKEDIN_INTEGRATION_PLAN.md)

---

## 🤝 Support

Issues? Check:
1. PhantomBuster Phantom logs
2. Sales agent execution logs
3. Rate limiter stats
4. LinkedIn account health

Still stuck? Review the troubleshooting section or check GitHub issues.

---

**Happy automating! Remember: Quality > Quantity** 🚀
