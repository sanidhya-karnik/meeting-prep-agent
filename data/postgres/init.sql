-- PreCall Briefing CRM Database
-- Mimics Salesforce-like structure

-- ============================================================================
-- SCHEMA
-- ============================================================================

CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    company_size VARCHAR(50),
    headquarters VARCHAR(255),
    website VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE contacts (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id),
    name VARCHAR(255) NOT NULL,
    role VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(50),
    sentiment VARCHAR(50), -- Champion, Supportive, Neutral, Detractor
    notes TEXT,
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE deals (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id),
    name VARCHAR(255) NOT NULL,
    stage VARCHAR(50), -- Prospecting, Qualification, Proposal, Negotiation, Closed Won, Closed Lost
    deal_type VARCHAR(100),
    value DECIMAL(12, 2),
    currency VARCHAR(3) DEFAULT 'USD',
    close_date DATE,
    probability INTEGER,
    owner VARCHAR(255),
    competitor VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE activities (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id),
    deal_id INTEGER REFERENCES deals(id),
    activity_type VARCHAR(50), -- Call, Email, Meeting, Note
    subject VARCHAR(255),
    description TEXT,
    participants TEXT[], -- Array of participant names
    duration_minutes INTEGER,
    activity_date TIMESTAMP,
    next_steps TEXT,
    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE health_metrics (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id),
    engagement_score INTEGER,
    nps_score INTEGER,
    support_tickets_open INTEGER,
    last_login DATE,
    usage_trend VARCHAR(20), -- up, down, stable
    risk_level VARCHAR(20), -- low, medium, high
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- DEMO DATA: ACME CORP
-- ============================================================================

-- Client
INSERT INTO clients (id, name, industry, company_size, headquarters, website)
VALUES (1, 'Acme Corp', 'Manufacturing', '2,500 employees', 'Chicago, IL', 'https://acmecorp.example.com');

-- Contacts
INSERT INTO contacts (client_id, name, role, email, phone, sentiment, notes, is_primary) VALUES
(1, 'John Smith', 'VP Engineering', 'john.smith@acmecorp.com', '+1 312-555-0142', 'Champion', 
 'Primary technical decision maker. Very hands-on, wants to see demos. Previously worked at a company that used our competitor.', TRUE),
(1, 'Lisa Park', 'CFO', 'lisa.park@acmecorp.com', '+1 312-555-0198', 'Neutral',
 'Focused on ROI and total cost of ownership. Has not attended recent calls. May need executive alignment meeting.', FALSE),
(1, 'Mike Chen', 'IT Director', 'mike.chen@acmecorp.com', '+1 312-555-0156', 'Supportive',
 'Concerned about integration with existing ERP. Wants detailed security documentation. Satisfied after technical deep-dive.', FALSE);

-- Deal
INSERT INTO deals (id, client_id, name, stage, deal_type, value, close_date, probability, owner, competitor)
VALUES (1, 1, 'Acme Corp - Enterprise License', 'Negotiation', '3-year Enterprise License', 450000.00, '2026-04-15', 75, 'Sarah Chen', 'TechRival Inc');

-- Activities (reverse chronological)
INSERT INTO activities (client_id, deal_id, activity_type, subject, description, participants, duration_minutes, activity_date, next_steps, created_by) VALUES
(1, 1, 'Call', 'Pricing Discussion', 
 'Discussed pricing concerns. John pushing for 10% discount. Mentioned competitor is offering lower price but fewer features. Need to emphasize ROI.',
 ARRAY['John Smith', 'Sarah Chen'], 45, '2026-03-18 14:00:00', 'Send updated ROI projections', 'Sarah Chen'),

(1, 1, 'Email', 'Revised Proposal Sent',
 'Sent revised proposal v3 with adjusted payment terms. Net 30 instead of Net 15. Added 99.9% SLA guarantee.',
 ARRAY['John Smith', 'Mike Chen', 'Sarah Chen'], NULL, '2026-03-15 16:00:00', NULL, 'Sarah Chen'),

(1, 1, 'Meeting', 'Technical Deep-Dive',
 'Technical deep-dive on integration. Mike satisfied with API documentation. John wants go-live by Q2 end. Discussed SAP ERP integration approach.',
 ARRAY['John Smith', 'Mike Chen', 'Sarah Chen', 'Tom Wilson'], 60, '2026-03-10 10:00:00', 'Confirm implementation timeline with delivery team', 'Sarah Chen'),

(1, 1, 'Call', 'CFO Introduction',
 'CFO intro call. Lisa wants to understand 3-year TCO vs buying point solutions. Skeptical but open to hearing more.',
 ARRAY['Lisa Park', 'Sarah Chen'], 30, '2026-03-01 11:00:00', 'Prepare TCO comparison document', 'Sarah Chen'),

(1, 1, 'Meeting', 'Initial Discovery',
 'Discovery meeting with engineering team. Identified pain points: manual reporting, disconnected systems, compliance tracking.',
 ARRAY['John Smith', 'Mike Chen', 'Sarah Chen'], 90, '2026-02-15 09:00:00', 'Send initial proposal', 'Sarah Chen');

-- Health Metrics
INSERT INTO health_metrics (client_id, engagement_score, nps_score, support_tickets_open, last_login, usage_trend, risk_level)
VALUES (1, 85, 42, 0, '2026-03-20', 'up', 'low');

-- ============================================================================
-- DEMO DATA: GLOBEX INDUSTRIES (second client for variety)
-- ============================================================================

INSERT INTO clients (id, name, industry, company_size, headquarters, website)
VALUES (2, 'Globex Industries', 'Logistics', '800 employees', 'Austin, TX', 'https://globex.example.com');

INSERT INTO contacts (client_id, name, role, email, phone, sentiment, notes, is_primary) VALUES
(2, 'Rachel Torres', 'COO', 'rachel.torres@globex.com', '+1 512-555-0234', 'Champion',
 'Driving the digital transformation initiative. Very responsive, pushes internal team to move fast.', TRUE),
(2, 'David Kim', 'Head of IT', 'david.kim@globex.com', '+1 512-555-0267', 'Neutral',
 'Concerned about change management. Wants phased rollout.', FALSE);

INSERT INTO deals (id, client_id, name, stage, deal_type, value, close_date, probability, owner, competitor)
VALUES (2, 2, 'Globex - Pilot Program', 'Proposal', '6-month Pilot', 75000.00, '2026-05-01', 60, 'Sarah Chen', NULL);

INSERT INTO activities (client_id, deal_id, activity_type, subject, description, participants, duration_minutes, activity_date, next_steps, created_by) VALUES
(2, 2, 'Meeting', 'Pilot Scope Discussion',
 'Defined pilot scope: 2 warehouses, 50 users. Rachel wants to prove value before full rollout.',
 ARRAY['Rachel Torres', 'David Kim', 'Sarah Chen'], 45, '2026-03-19 15:00:00', 'Send pilot proposal by Friday', 'Sarah Chen');

INSERT INTO health_metrics (client_id, engagement_score, nps_score, support_tickets_open, last_login, usage_trend, risk_level)
VALUES (2, 72, NULL, 1, '2026-03-18', 'stable', 'medium');

-- ============================================================================
-- USEFUL VIEWS
-- ============================================================================

CREATE VIEW client_summary AS
SELECT 
    c.id,
    c.name AS client_name,
    c.industry,
    c.company_size,
    c.headquarters,
    d.name AS deal_name,
    d.stage AS deal_stage,
    d.value AS deal_value,
    d.close_date,
    d.probability,
    d.owner AS deal_owner,
    d.competitor,
    h.engagement_score,
    h.risk_level
FROM clients c
LEFT JOIN deals d ON c.id = d.client_id
LEFT JOIN health_metrics h ON c.id = h.client_id;

CREATE VIEW recent_activities AS
SELECT 
    c.name AS client_name,
    a.activity_type,
    a.subject,
    a.description,
    a.participants,
    a.activity_date,
    a.next_steps
FROM activities a
JOIN clients c ON a.client_id = c.id
ORDER BY a.activity_date DESC;
