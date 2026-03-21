-- PreCall Briefing CRM Database
-- Enhanced Salesforce-like schema with standardized dimensions

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
    year_established INTEGER,
    annual_revenue_musd DECIMAL(12, 2),
    employee_count INTEGER,
    parent_company VARCHAR(255),
    data_quality_flag VARCHAR(50) DEFAULT 'clean',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sales_reps (
    id SERIAL PRIMARY KEY,
    rep_name VARCHAR(255) NOT NULL UNIQUE,
    manager_name VARCHAR(255),
    regional_office VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    series VARCHAR(100),
    list_price DECIMAL(12, 2),
    is_active BOOLEAN DEFAULT TRUE,
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
    external_opportunity_id VARCHAR(50) UNIQUE,
    client_id INTEGER REFERENCES clients(id),
    product_id INTEGER REFERENCES products(id),
    owner_id INTEGER REFERENCES sales_reps(id),
    name VARCHAR(255) NOT NULL,
    stage VARCHAR(50), -- Prospecting, Engaging, Won, Lost
    deal_type VARCHAR(100),
    value DECIMAL(12, 2),
    list_price_snapshot DECIMAL(12, 2),
    currency VARCHAR(3) DEFAULT 'USD',
    engage_date DATE,
    close_date DATE,
    probability INTEGER,
    owner VARCHAR(255), -- kept for backward compatibility with existing agent output
    competitor VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE deal_stage_history (
    id SERIAL PRIMARY KEY,
    deal_id INTEGER REFERENCES deals(id),
    stage VARCHAR(50) NOT NULL,
    entered_at TIMESTAMP NOT NULL,
    exited_at TIMESTAMP,
    source_system VARCHAR(50) DEFAULT 'crm_pipeline'
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
    win_rate_90d DECIMAL(5, 2),
    avg_cycle_days_90d DECIMAL(8, 2),
    avg_closed_value_90d DECIMAL(12, 2),
    open_pipeline_value DECIMAL(12, 2),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- STANDARDIZED DIMENSION DATA
-- ============================================================================

INSERT INTO sales_reps (id, rep_name, manager_name, regional_office) VALUES
(1, 'Sarah Chen', 'Cara Losch', 'East'),
(2, 'Jonathan Berthelot', 'Melvin Marxen', 'Central'),
(3, 'Violet Mclelland', 'Cara Losch', 'East');

-- Canonical product naming (e.g. GTX Pro, not GTXPro)
INSERT INTO products (id, name, series, list_price) VALUES
(1, 'GTX Basic', 'GTX', 550.00),
(2, 'GTX Pro', 'GTX', 4821.00),
(3, 'GTX Plus Basic', 'GTX', 1096.00),
(4, 'GTX Plus Pro', 'GTX', 5482.00),
(5, 'MG Advanced', 'MG', 3393.00),
(6, 'MG Special', 'MG', 55.00),
(7, 'GTK 500', 'GTK', 26768.00);

-- ============================================================================
-- DEMO DATA: ACME CORP
-- ============================================================================

INSERT INTO clients (
    id, name, industry, company_size, headquarters, website,
    year_established, annual_revenue_musd, employee_count, parent_company, data_quality_flag
) VALUES (
    1, 'Acme Corp', 'manufacturing', '2,500 employees', 'Chicago, IL', 'https://acmecorp.example.com',
    1996, 1100.04, 2822, NULL, 'clean'
);

INSERT INTO contacts (client_id, name, role, email, phone, sentiment, notes, is_primary) VALUES
(1, 'John Smith', 'VP Engineering', 'john.smith@acmecorp.com', '+1 312-555-0142', 'Champion',
 'Primary technical decision maker. Very hands-on, wants to see demos. Previously worked at a company that used our competitor.', TRUE),
(1, 'Lisa Park', 'CFO', 'lisa.park@acmecorp.com', '+1 312-555-0198', 'Neutral',
 'Focused on ROI and total cost of ownership. Has not attended recent calls. May need executive alignment meeting.', FALSE),
(1, 'Mike Chen', 'IT Director', 'mike.chen@acmecorp.com', '+1 312-555-0156', 'Supportive',
 'Concerned about integration with existing ERP. Wants detailed security documentation. Satisfied after technical deep-dive.', FALSE);

INSERT INTO deals (
    id, external_opportunity_id, client_id, product_id, owner_id, name, stage, deal_type, value,
    list_price_snapshot, engage_date, close_date, probability, owner, competitor
) VALUES (
    1, 'OPP-ACME-0001', 1, 2, 1, 'Acme Corp - Enterprise License', 'Engaging',
    '3-year Enterprise License', 450000.00, 4821.00, '2026-02-20', '2026-04-15', 75, 'Sarah Chen', 'TechRival Inc'
);

INSERT INTO deal_stage_history (deal_id, stage, entered_at, exited_at, source_system) VALUES
(1, 'Prospecting', '2026-02-01 09:00:00', '2026-02-20 09:00:00', 'crm_pipeline'),
(1, 'Engaging', '2026-02-20 09:00:00', NULL, 'crm_pipeline');

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

INSERT INTO health_metrics (
    client_id, engagement_score, nps_score, support_tickets_open, last_login, usage_trend, risk_level,
    win_rate_90d, avg_cycle_days_90d, avg_closed_value_90d, open_pipeline_value
) VALUES (
    1, 85, 42, 0, '2026-03-20', 'up', 'low', 64.20, 47.50, 325000.00, 450000.00
);

-- ============================================================================
-- DEMO DATA: GLOBEX INDUSTRIES
-- ============================================================================

INSERT INTO clients (
    id, name, industry, company_size, headquarters, website,
    year_established, annual_revenue_musd, employee_count, parent_company, data_quality_flag
) VALUES (
    2, 'Globex Industries', 'logistics', '800 employees', 'Austin, TX', 'https://globex.example.com',
    2000, 1223.72, 2497, NULL, 'clean'
);

INSERT INTO contacts (client_id, name, role, email, phone, sentiment, notes, is_primary) VALUES
(2, 'Rachel Torres', 'COO', 'rachel.torres@globex.com', '+1 512-555-0234', 'Champion',
 'Driving the digital transformation initiative. Very responsive, pushes internal team to move fast.', TRUE),
(2, 'David Kim', 'Head of IT', 'david.kim@globex.com', '+1 512-555-0267', 'Neutral',
 'Concerned about change management. Wants phased rollout.', FALSE);

INSERT INTO deals (
    id, external_opportunity_id, client_id, product_id, owner_id, name, stage, deal_type, value,
    list_price_snapshot, engage_date, close_date, probability, owner, competitor
) VALUES (
    2, 'OPP-GLOBEX-0001', 2, 3, 1, 'Globex - Pilot Program', 'Engaging',
    '6-month Pilot', 75000.00, 1096.00, '2026-03-05', '2026-05-01', 60, 'Sarah Chen', NULL
);

INSERT INTO deal_stage_history (deal_id, stage, entered_at, exited_at, source_system) VALUES
(2, 'Prospecting', '2026-02-25 10:00:00', '2026-03-05 10:00:00', 'crm_pipeline'),
(2, 'Engaging', '2026-03-05 10:00:00', NULL, 'crm_pipeline');

INSERT INTO activities (client_id, deal_id, activity_type, subject, description, participants, duration_minutes, activity_date, next_steps, created_by) VALUES
(2, 2, 'Meeting', 'Pilot Scope Discussion',
 'Defined pilot scope: 2 warehouses, 50 users. Rachel wants to prove value before full rollout.',
 ARRAY['Rachel Torres', 'David Kim', 'Sarah Chen'], 45, '2026-03-19 15:00:00', 'Send pilot proposal by Friday', 'Sarah Chen');

INSERT INTO health_metrics (
    client_id, engagement_score, nps_score, support_tickets_open, last_login, usage_trend, risk_level,
    win_rate_90d, avg_cycle_days_90d, avg_closed_value_90d, open_pipeline_value
) VALUES (
    2, 72, NULL, 1, '2026-03-18', 'stable', 'medium', 61.80, 39.00, 68000.00, 75000.00
);

-- ============================================================================
-- DEMO DATA: UNKNOWN ACCOUNT (data quality fallback)
-- ============================================================================

INSERT INTO clients (
    id, name, industry, company_size, headquarters, website,
    year_established, annual_revenue_musd, employee_count, parent_company, data_quality_flag
) VALUES (
    3, 'Unknown Account', 'unknown', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'missing_account'
);

INSERT INTO deals (
    id, external_opportunity_id, client_id, product_id, owner_id, name, stage, deal_type, value,
    list_price_snapshot, engage_date, close_date, probability, owner, competitor
) VALUES (
    3, 'OPP-UNK-0001', 3, 2, 2, 'Unattributed Opportunity - GTX Pro', 'Prospecting',
    'Inbound Qualification', NULL, 4821.00, NULL, NULL, 20, 'Jonathan Berthelot', NULL
);

INSERT INTO deal_stage_history (deal_id, stage, entered_at, exited_at, source_system) VALUES
(3, 'Prospecting', '2026-03-12 09:30:00', NULL, 'crm_pipeline');

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
    c.year_established,
    c.annual_revenue_musd,
    c.employee_count,
    c.parent_company,
    c.data_quality_flag,
    d.external_opportunity_id,
    d.name AS deal_name,
    d.stage AS deal_stage,
    d.value AS deal_value,
    d.engage_date,
    d.close_date,
    d.probability,
    d.owner AS deal_owner,
    sr.manager_name AS deal_owner_manager,
    sr.regional_office AS deal_owner_region,
    p.name AS product_name,
    p.series AS product_series,
    d.competitor,
    h.engagement_score,
    h.risk_level,
    h.win_rate_90d,
    h.avg_cycle_days_90d,
    h.avg_closed_value_90d,
    h.open_pipeline_value
FROM clients c
LEFT JOIN deals d ON c.id = d.client_id
LEFT JOIN sales_reps sr ON d.owner_id = sr.id
LEFT JOIN products p ON d.product_id = p.id
LEFT JOIN health_metrics h ON c.id = h.client_id;

CREATE VIEW recent_activities AS
SELECT
    c.name AS client_name,
    d.external_opportunity_id,
    p.name AS product_name,
    a.activity_type,
    a.subject,
    a.description,
    a.participants,
    a.activity_date,
    a.next_steps
FROM activities a
JOIN clients c ON a.client_id = c.id
LEFT JOIN deals d ON a.deal_id = d.id
LEFT JOIN products p ON d.product_id = p.id
ORDER BY a.activity_date DESC;
