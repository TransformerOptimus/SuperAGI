import json
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session

from models.agent import SalesAgent, AgentExecution, ExecutionLog, Lead
from agent.llm import LLM
from agent.prompts import get_system_prompt
from tools import AVAILABLE_TOOLS


class AgentExecutor:
    """
    Agent Executor - Orchestrates agent workflow execution
    """

    def __init__(self, db: Session):
        self.db = db
        self.llm = None
        self.tools = {}
        self.agent = None
        self.execution = None
        self.conversation_history = []

    def execute(self, execution_id: int) -> Dict[str, Any]:
        """
        Execute an agent run

        Args:
            execution_id: ID of the execution to run

        Returns:
            Execution result dictionary
        """
        # Load execution
        self.execution = self.db.query(AgentExecution).filter(
            AgentExecution.id == execution_id
        ).first()

        if not self.execution:
            return {"error": "Execution not found"}

        # Load agent
        self.agent = self.db.query(SalesAgent).filter(
            SalesAgent.id == self.execution.agent_id
        ).first()

        if not self.agent:
            return {"error": "Agent not found"}

        # Initialize LLM
        self.llm = LLM(model=self.agent.model)

        # Initialize tools
        self._initialize_tools()

        # Update execution status
        self.execution.status = "RUNNING"
        self.execution.started_at = datetime.utcnow()
        self.db.commit()

        try:
            # Execute workflow
            result = self._run_sales_workflow()

            # Update execution status
            self.execution.status = "COMPLETED"
            self.execution.completed_at = datetime.utcnow()
            self.db.commit()

            return result

        except Exception as e:
            # Handle errors
            self.execution.status = "FAILED"
            self.execution.error_message = str(e)
            self.execution.completed_at = datetime.utcnow()
            self.db.commit()

            self._log(
                role="system",
                content=f"Error: {str(e)}",
                metadata={"error": True}
            )

            return {"error": str(e)}

    def _initialize_tools(self):
        """Initialize tools based on agent configuration"""
        for tool_name in self.agent.tools or []:
            if tool_name in AVAILABLE_TOOLS:
                self.tools[tool_name] = AVAILABLE_TOOLS[tool_name]()

    def _run_sales_workflow(self) -> Dict[str, Any]:
        """
        Execute the sales agent workflow

        Workflow:
        1. Find/load leads
        2. For each lead:
           - Research company
           - Generate personalized email
           - Send email
           - Track in database
        3. Check for responses
        4. Send follow-ups
        """
        self._log(role="system", content="Starting sales workflow")

        # Step 1: Get leads
        leads = self._get_or_find_leads()

        if not leads:
            return {"message": "No leads found"}

        self._log(
            role="system",
            content=f"Found {len(leads)} leads to process"
        )

        # Step 2: Process each lead
        for lead in leads:
            try:
                self._process_lead(lead)
                self.execution.leads_processed += 1
                self.db.commit()
            except Exception as e:
                self._log(
                    role="system",
                    content=f"Error processing lead {lead.get('email')}: {str(e)}",
                    metadata={"error": True, "lead": lead}
                )
                continue

        # Step 3: Check for responses
        self._check_responses()

        return {
            "status": "completed",
            "leads_processed": self.execution.leads_processed,
            "emails_sent": self.execution.emails_sent,
            "responses_received": self.execution.responses_received
        }

    def _get_or_find_leads(self) -> List[Dict[str, Any]]:
        """Get leads from database or find new ones using Apollo"""
        # Check if we have existing leads for this execution
        existing_leads = self.db.query(Lead).filter(
            Lead.execution_id == self.execution.id
        ).all()

        if existing_leads:
            return [lead.to_dict() for lead in existing_leads]

        # Use Apollo to find new leads
        if "apollo_search" in self.tools:
            apollo_tool = self.tools["apollo_search"]

            # Extract search criteria from agent goals/instructions
            # For demo, using default criteria
            leads_data = apollo_tool.execute(
                person_titles=["VP of Sales", "Director of Sales", "Sales Manager"],
                per_page=10
            )

            # Save leads to database
            leads = []
            for lead_data in leads_data:
                lead = Lead(
                    execution_id=self.execution.id,
                    first_name=lead_data.get('first_name'),
                    last_name=lead_data.get('last_name'),
                    email=lead_data.get('email'),
                    company=lead_data.get('company'),
                    title=lead_data.get('title'),
                    linkedin_url=lead_data.get('linkedin_url'),
                    company_domain=lead_data.get('company_domain'),
                    company_size=str(lead_data.get('company_size', '')),
                    industry=lead_data.get('industry'),
                    status='NEW'
                )
                self.db.add(lead)
                leads.append(lead_data)

            self.db.commit()
            return leads

        return []

    def _process_lead(self, lead: Dict[str, Any]):
        """Process a single lead"""
        self._log(
            role="system",
            content=f"Processing lead: {lead.get('name')} at {lead.get('company')}"
        )

        # Step 1: Research company
        research_summary = self._research_company(lead)

        # Step 2: Generate personalized email
        email_content = self._generate_email(lead, research_summary)

        # Step 3: Send email
        if "send_email" in self.tools:
            send_result = self._send_email(lead, email_content)

            if send_result.get("success"):
                # Update lead status
                self.db.query(Lead).filter(
                    Lead.email == lead.get('email')
                ).update({
                    "status": "CONTACTED",
                    "email_sent": True,
                    "last_contacted_at": datetime.utcnow(),
                    "research_data": {"summary": research_summary}
                })
                self.execution.emails_sent += 1
                self.db.commit()

    def _research_company(self, lead: Dict[str, Any]) -> str:
        """Research company using Google Search"""
        if "google_search" not in self.tools:
            return "No research data available"

        company = lead.get('company', '')
        search_tool = self.tools["google_search"]

        # Search for company information
        search_results = search_tool.execute(
            query=f"{company} company news achievements",
            num_results=5
        )

        # Summarize research with LLM
        research_text = "\n".join([
            f"- {r.get('title')}: {r.get('snippet')}"
            for r in search_results
        ])

        prompt = f"""Summarize key insights about {company} for sales outreach:

Search Results:
{research_text}

Provide 2-3 sentences highlighting:
1. What the company does
2. Recent news or achievements
3. Potential pain points or opportunities

Summary:"""

        summary = self.llm.generate_text(prompt, temperature=0.7, max_tokens=200)

        self._log(
            role="tool",
            tool_name="google_search",
            content=summary,
            metadata={"company": company}
        )

        return summary

    def _generate_email(self, lead: Dict[str, Any], research: str) -> Dict[str, str]:
        """Generate personalized email using LLM"""
        name = lead.get('first_name', lead.get('name', 'there'))
        title = lead.get('title', '')
        company = lead.get('company', '')

        prompt = f"""Generate a personalized cold outreach email for:

Name: {name}
Title: {title}
Company: {company}

Research Summary:
{research}

Requirements:
1. Engaging subject line (5-8 words)
2. Personalized opening referencing company/research
3. Clear value proposition
4. Call-to-action to book a 15-min call
5. Professional tone, under 150 words

Format:
SUBJECT: [subject]

[email body]"""

        response = self.llm.generate_text(prompt, temperature=0.8, max_tokens=400)

        # Parse subject and body
        parts = response.split('\n', 1)
        subject = parts[0].replace('SUBJECT:', '').strip()
        body = parts[1].strip() if len(parts) > 1 else response

        self._log(
            role="assistant",
            content=f"Generated email for {lead.get('email')}",
            metadata={"subject": subject, "preview": body[:100]}
        )

        return {"subject": subject, "body": body}

    def _send_email(self, lead: Dict[str, Any], email_content: Dict[str, str]) -> Dict[str, Any]:
        """Send email to lead"""
        send_tool = self.tools["send_email"]

        result = send_tool.execute(
            to=lead.get('email'),
            subject=email_content.get('subject'),
            body=email_content.get('body')
        )

        self._log(
            role="tool",
            tool_name="send_email",
            content=json.dumps(result),
            metadata={"recipient": lead.get('email')}
        )

        return result

    def _check_responses(self):
        """Check for email responses"""
        if "read_email" not in self.tools:
            return

        read_tool = self.tools["read_email"]
        emails = read_tool.execute(max_emails=20, unread_only=True)

        self.execution.responses_received = len([e for e in emails if not e.get('error')])
        self.db.commit()

        self._log(
            role="tool",
            tool_name="read_email",
            content=f"Found {len(emails)} new responses",
            metadata={"count": len(emails)}
        )

    def _log(
        self,
        role: str,
        content: str,
        tool_name: str = None,
        metadata: Dict[str, Any] = None
    ):
        """Log execution step"""
        log = ExecutionLog(
            execution_id=self.execution.id,
            step=self.execution.current_step,
            role=role,
            tool_name=tool_name,
            content=content,
            metadata=metadata or {}
        )
        self.db.add(log)
        self.execution.current_step += 1
        self.db.commit()
