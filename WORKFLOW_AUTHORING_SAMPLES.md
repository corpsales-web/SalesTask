# Workflow Authoring Samples & Examples

## Overview
This document provides comprehensive examples of how to create and use AI-powered workflows in the Aavana Greens CRM system.

## How to Create Workflows

### Step 1: Access Workflow Builder
1. Navigate to **Admin** → **Workflow Authoring**
2. Click the **"New Workflow"** button (purple button in top-right)
3. This automatically switches you to the **Workflow Builder** tab

### Step 2: Fill Basic Information
- **Workflow Name**: Give your workflow a descriptive name
- **Category**: Choose from Lead Nurturing, Customer Onboarding, Follow-up Automation, etc.
- **Description**: Explain what this workflow does

### Step 3: Add Workflow Steps
Click the step type buttons to add them to your workflow:
- **AI Response**: Generate AI-powered responses using GPT-5/Claude/Gemini
- **Send Message**: Send automated WhatsApp/Email messages
- **Wait for Response**: Pause workflow until user responds
- **Conditional Logic**: Branch workflow based on conditions
- **Assign Agent**: Assign lead to specific agent or team
- **Schedule Follow-up**: Schedule future actions
- **Update Lead**: Modify lead information
- **Send Notification**: Notify agents or managers

### Step 4: Configure Settings
- **Auto-assign leads**: Automatically assign leads to agents
- **Send notifications**: Notify team members of workflow actions
- **Retry on failure**: Retry failed steps automatically
- **Max execution time**: Set timeout for workflow execution

### Step 5: Save & Test
1. Click **"Save Workflow"** to save your workflow
2. Use **"Test Workflow"** to test with sample data
3. **Publish** when ready for production use

---

## Sample Workflow 1: WhatsApp Lead Nurturing

### Workflow Configuration
```json
{
  "name": "WhatsApp Lead Nurturing - Residential Gardens",
  "description": "Automated lead nurturing sequence for residential garden projects via WhatsApp",
  "category": "lead_nurturing",
  "steps": [
    {
      "type": "ai_response",
      "name": "Generate Personalized Welcome Message",
      "config": {
        "prompt_template": "Create a personalized welcome message for {lead_name} who is interested in {project_type} with budget {budget} in {location}. Keep it warm and professional.",
        "ai_model": "gpt-5",
        "temperature": 0.7
      }
    },
    {
      "type": "send_message",
      "name": "Send Welcome WhatsApp",
      "config": {
        "channel": "whatsapp",
        "message": "{{ai_response_output}}",
        "delay_minutes": 0
      }
    },
    {
      "type": "wait_for_response",
      "name": "Wait for Initial Response",
      "config": {
        "timeout_hours": 24,
        "reminder_after_hours": 12
      }
    },
    {
      "type": "conditional",
      "name": "Check Response Interest Level",
      "config": {
        "conditions": [
          {
            "if": "response_contains(['interested', 'yes', 'tell me more'])",
            "then": "continue_workflow"
          },
          {
            "if": "response_contains(['not interested', 'no', 'remove'])",
            "then": "end_workflow"
          }
        ],
        "default": "schedule_followup"
      }
    },
    {
      "type": "ai_response",
      "name": "Generate Detailed Information",
      "config": {
        "prompt_template": "Create a detailed response about our {project_type} services for {lead_name}. Include pricing info for budget {budget}, timeline, and next steps. Make it compelling and informative.",
        "ai_model": "gpt-5"
      }
    },
    {
      "type": "schedule_followup",
      "name": "Schedule Site Visit",
      "config": {
        "delay_days": 3,
        "action": "site_visit_reminder",
        "assign_to": "senior_consultant"
      }
    }
  ],
  "settings": {
    "auto_assign": true,
    "send_notifications": true,
    "max_execution_time": 3600,
    "retry_on_failure": true
  }
}
```

### Expected Flow:
1. **Day 1**: Lead receives personalized welcome message via WhatsApp
2. **Day 1-2**: System waits for response, sends reminder after 12 hours
3. **Day 2**: Based on response, either continues nurturing or ends workflow
4. **Day 2**: Interested leads receive detailed project information
5. **Day 5**: Site visit is scheduled with senior consultant

---

## Sample Workflow 2: Email Lead Qualification

### Workflow Configuration
```json
{
  "name": "Email Lead Qualification - Commercial Projects",
  "description": "Automated lead qualification sequence for commercial landscaping projects",
  "category": "lead_qualification",
  "steps": [
    {
      "type": "send_message",
      "name": "Send Qualification Questionnaire",
      "config": {
        "channel": "email",
        "subject": "Help us design your perfect commercial landscape - Quick Questions",
        "template": "qualification_questionnaire",
        "variables": {
          "lead_name": "{{lead.name}}",
          "company_name": "{{lead.company}}"
        }
      }
    },
    {
      "type": "wait_for_response",
      "name": "Wait for Questionnaire Response",
      "config": {
        "timeout_hours": 72,
        "reminder_after_hours": 48
      }
    },
    {
      "type": "ai_response",
      "name": "Analyze Qualification Responses",
      "config": {
        "prompt_template": "Analyze this lead qualification response: {response_text}. Rate the lead quality (Hot/Warm/Cold) and suggest next best action. Consider budget, timeline, decision-making authority, and project scope.",
        "ai_model": "claude-sonnet-4"
      }
    },
    {
      "type": "conditional",
      "name": "Route Based on Lead Quality",
      "config": {
        "conditions": [
          {
            "if": "ai_rating == 'Hot'",
            "then": "assign_senior_agent"
          },
          {
            "if": "ai_rating == 'Warm'",
            "then": "assign_regular_agent"
          },
          {
            "if": "ai_rating == 'Cold'",
            "then": "nurture_sequence"
          }
        ]
      }
    },
    {
      "type": "assign_agent",
      "name": "Assign to Appropriate Agent",
      "config": {
        "assignment_rules": {
          "hot_leads": "senior_commercial_consultant",
          "warm_leads": "commercial_consultant",
          "cold_leads": "junior_consultant"
        }
      }
    },
    {
      "type": "trigger_notification",
      "name": "Notify Assigned Agent",
      "config": {
        "notification_type": "high_priority",
        "message": "New qualified lead assigned: {lead_name} from {company_name}. Quality: {ai_rating}. Action required within 2 hours."
      }
    }
  ]
}
```

---

## Sample Workflow 3: Customer Onboarding

### Workflow Configuration
```json
{
  "name": "Customer Onboarding - Project Kickoff",
  "description": "Welcome new customers and guide them through project initiation",
  "category": "customer_onboarding",
  "steps": [
    {
      "type": "send_message",
      "name": "Welcome Email",
      "config": {
        "channel": "email",
        "subject": "Welcome to Aavana Greens! Your garden transformation begins now 🌱",
        "template": "customer_welcome",
        "attachments": ["project_guide.pdf", "care_instructions.pdf"]
      }
    },
    {
      "type": "ai_response",
      "name": "Generate Project Timeline",
      "config": {
        "prompt_template": "Create a detailed project timeline for {project_type} with budget {budget}. Include milestones, estimated completion dates, and key deliverables. Format as a professional timeline.",
        "ai_model": "gpt-5"
      }
    },
    {
      "type": "schedule_followup",
      "name": "Schedule Site Survey",
      "config": {
        "delay_days": 2,
        "action": "site_survey",
        "assign_to": "site_surveyor",
        "calendar_duration": 120
      }
    },
    {
      "type": "send_message",
      "name": "Site Survey Confirmation",
      "config": {
        "channel": "whatsapp",
        "message": "Hi {lead_name}! Your site survey is scheduled for {survey_date}. Our team will arrive at {survey_time}. Please ensure someone is available to provide access. Questions? Reply here!"
      }
    },
    {
      "type": "update_lead",
      "name": "Update Customer Status",
      "config": {
        "fields": {
          "status": "onboarding_in_progress",
          "project_stage": "site_survey_scheduled",
          "last_contact": "{{current_timestamp}}"
        }
      }
    }
  ]
}
```

---

## Sample Workflow 4: Follow-up Automation

### Workflow Configuration
```json
{
  "name": "Post-Project Follow-up & Upsell",
  "description": "Follow up with completed projects for maintenance services and referrals",
  "category": "follow_up_automation",
  "steps": [
    {
      "type": "wait_for_response",
      "name": "Wait for Project Completion",
      "config": {
        "trigger": "project_status_completed",
        "delay_days": 7
      }
    },
    {
      "type": "send_message",
      "name": "Project Satisfaction Survey",
      "config": {
        "channel": "email",
        "subject": "How did we do? Your feedback matters! 🌟",
        "template": "satisfaction_survey",
        "survey_link": "https://forms.aavanagreens.com/satisfaction"
      }
    },
    {
      "type": "ai_response",
      "name": "Generate Maintenance Proposal",
      "config": {
        "prompt_template": "Create a personalized maintenance service proposal for {lead_name} who completed a {project_type}. Include seasonal care, plant health monitoring, and landscaping updates. Make it compelling with seasonal offers.",
        "ai_model": "gpt-5"
      }
    },
    {
      "type": "schedule_followup",
      "name": "Schedule Maintenance Call",
      "config": {
        "delay_days": 14,
        "action": "maintenance_upsell_call"
      }
    },
    {
      "type": "send_message",
      "name": "Referral Request",
      "config": {
        "channel": "whatsapp",
        "message": "Hi {lead_name}! We're thrilled you love your new garden! 🌺 If you know anyone who might benefit from our services, we'd love to help them too. As a thank you, you'll receive a ₹5000 credit for successful referrals! Share our contact: +91-XXXXXXXXX"
      }
    }
  ]
}
```

---

## Testing Your Workflows

### 1. Using the Test Feature
- Click **"Test Workflow"** in the Workflow Builder
- Provide sample data like:
  ```json
  {
    "lead_name": "Rajesh Kumar",
    "project_type": "Residential Garden",
    "budget": "₹2,50,000",
    "location": "Mumbai",
    "phone": "+91 9876543210",
    "email": "rajesh@example.com"
  }
  ```

### 2. Monitor Test Results
- Check the **Testing & Analytics** tab
- Review AI responses, token usage, and execution time
- Verify all steps execute correctly

### 3. Publish When Ready
- Click **"Publish"** to make the workflow live
- Set up triggers (new leads, project completion, etc.)
- Monitor performance in Analytics

---

## Best Practices

### 1. Workflow Design
- Start simple with 3-5 steps
- Add complexity gradually
- Always include conditional logic for different scenarios
- Set appropriate timeouts and reminders

### 2. AI Prompts
- Be specific about desired output format
- Include relevant context variables
- Test with various input scenarios
- Use appropriate AI models (GPT-5 for creativity, Claude for analysis)

### 3. Message Templates
- Keep messages conversational and personal
- Include clear call-to-actions
- Use emojis sparingly but effectively
- Test across different communication channels

### 4. Error Handling
- Always enable "Retry on failure"
- Set reasonable timeout values
- Include fallback paths for failed conditions
- Monitor workflow execution logs

---

## Variables You Can Use

### Lead Information
- `{lead_name}` - Lead's full name
- `{phone}` - Phone number
- `{email}` - Email address
- `{location}` - City/area
- `{budget}` - Project budget
- `{project_type}` - Type of project (Residential, Commercial, etc.)
- `{requirements}` - Specific requirements
- `{status}` - Current lead status

### System Variables
- `{current_date}` - Today's date
- `{current_time}` - Current time
- `{agent_name}` - Assigned agent name
- `{company_name}` - Aavana Greens
- `{contact_number}` - Company contact number

### AI Response Variables
- `{ai_response_output}` - Output from previous AI step
- `{ai_rating}` - Lead quality rating
- `{ai_analysis}` - Detailed AI analysis

---

## Troubleshooting

### Common Issues
1. **Workflow not triggering**: Check trigger conditions and lead status
2. **AI responses empty**: Verify prompt template and variables
3. **Messages not sending**: Check phone/email formats and channel settings
4. **Steps being skipped**: Review conditional logic and prerequisites

### Getting Help
- Use the **Testing & Analytics** tab to debug issues
- Check workflow execution logs
- Test individual steps before full workflow
- Contact admin for complex troubleshooting

---

This documentation should help you create powerful, automated workflows that enhance your lead management and customer engagement processes!