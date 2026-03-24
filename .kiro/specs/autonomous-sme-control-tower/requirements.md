# Requirements Document

## Introduction

NovaSME is a multi-agent AI system that provides autonomous operational intelligence for small and medium enterprises (SMEs). The system monitors operational signals (invoices, emails), diagnoses business instability, simulates corrective strategies, executes operational workflows autonomously, and re-evaluates outcomes in a closed loop. It acts as an operational control tower that continuously optimizes business health through AI-driven decision-making powered by Amazon Nova models.

## Glossary

- **NovaSME_System**: The complete autonomous SME control tower platform
- **Signal_Intake_Agent**: Component responsible for ingesting and extracting structured data from operational signals
- **Context_Memory_Service**: Service that stores operational signals with semantic embeddings for retrieval
- **Stability_Intelligence_Agent**: Component that calculates the Business Stability Index (BSI)
- **Strategy_Simulation_Agent**: Component that generates corrective operational strategies
- **Workflow_Automation_Agent**: Component that executes operational workflows using Nova Act
- **Reeval_Agent**: Component that recalculates BSI and measures prediction accuracy after actions
- **Dashboard_UI**: Frontend interface displaying operational health and recommendations
- **Voice_Interface**: Optional voice-based query and response system using Nova Sonic
- **BSI**: Business Stability Index - a metric between 0 and 100 representing operational health
- **Operational_Signal**: Business data input such as invoices or emails
- **Embedding_Vector**: Semantic representation of signal content for memory retrieval
- **Strategy**: A recommended corrective action with predicted impact
- **Workflow_Execution**: An automated operational task performed by the system
- **Org_ID**: Organization identifier used as partition key in DynamoDB

## Requirements

### Requirement 1: Invoice Signal Intake

**User Story:** As a business owner, I want to upload invoice documents, so that the system can extract structured information and monitor payment obligations.

#### Acceptance Criteria

1. WHEN an invoice document is uploaded, THE Signal_Intake_Agent SHALL extract vendor name, invoice_id, amount, due_date, currency, and description fields
2. WHEN invoice extraction completes, THE Signal_Intake_Agent SHALL return structured data conforming to the Invoice Pydantic model
3. IF invoice extraction fails, THEN THE Signal_Intake_Agent SHALL return a descriptive error message
4. THE Signal_Intake_Agent SHALL process invoice documents within 5 seconds
5. WHEN an invoice is processed, THE NovaSME_System SHALL store the structured data in DynamoDB keyed by org_id

### Requirement 2: Email Signal Intake

**User Story:** As a business owner, I want to submit email text, so that the system can classify and analyze operational communications.

#### Acceptance Criteria

1. WHEN email text is submitted, THE Signal_Intake_Agent SHALL classify it as one of: payment_reminder, customer_inquiry, operational_message, or other
2. WHEN email classification completes, THE Signal_Intake_Agent SHALL return structured data conforming to the Email Pydantic model
3. THE Signal_Intake_Agent SHALL extract sender, subject, and classification from email content
4. WHEN an email is processed, THE NovaSME_System SHALL store the structured data in DynamoDB keyed by org_id
5. THE Signal_Intake_Agent SHALL process email submissions within 3 seconds

### Requirement 3: Signal Embedding Generation

**User Story:** As the system, I want to generate semantic embeddings for signals, so that I can enable contextual memory retrieval.

#### Acceptance Criteria

1. WHEN a signal is processed, THE Context_Memory_Service SHALL generate an embedding vector using Nova embeddings model
2. THE Context_Memory_Service SHALL store the embedding vector reference with signal metadata in DynamoDB
3. THE Context_Memory_Service SHALL associate each embedding with its signal_id, org_id, signal_type, and timestamp
4. WHEN embedding generation fails, THE Context_Memory_Service SHALL log the error and continue processing

### Requirement 4: Business Stability Index Calculation

**User Story:** As a business owner, I want a measurable operational health score, so that I can understand my business stability at a glance.

#### Acceptance Criteria

1. WHEN operational signals exist for an organization, THE Stability_Intelligence_Agent SHALL calculate a BSI value between 0 and 100
2. THE Stability_Intelligence_Agent SHALL incorporate cash_runway_risk, invoice_aging_risk, revenue_concentration_risk, expense_volatility_risk, and response_latency_risk into BSI calculation
3. WHEN BSI is calculated, THE Stability_Intelligence_Agent SHALL store a BSI snapshot with timestamp and org_id in DynamoDB
4. THE Stability_Intelligence_Agent SHALL use Nova 2 Lite model for risk assessment reasoning
5. WHEN insufficient data exists, THE Stability_Intelligence_Agent SHALL return BSI of 50 with a confidence flag indicating limited data

### Requirement 5: Strategy Simulation

**User Story:** As a business owner, I want AI-generated corrective strategies, so that I can improve operational stability.

#### Acceptance Criteria

1. WHEN BSI is below 70, THE Strategy_Simulation_Agent SHALL generate between 2 and 3 corrective strategies
2. FOR EACH strategy, THE Strategy_Simulation_Agent SHALL include description, predicted_bsi_improvement, confidence_score, and automation_eligibility fields
3. THE Strategy_Simulation_Agent SHALL use Nova 2 Lite model to reason about strategy effectiveness
4. WHEN strategies are generated, THE NovaSME_System SHALL store them in DynamoDB keyed by org_id
5. THE Strategy_Simulation_Agent SHALL return strategies conforming to the Strategy Pydantic model

### Requirement 6: Workflow Automation Execution

**User Story:** As a business owner, I want the system to execute operational workflows automatically, so that corrective actions happen without manual intervention.

#### Acceptance Criteria

1. WHEN a strategy is marked as automation_eligible, THE Workflow_Automation_Agent SHALL execute the corresponding operational workflow using Nova Act
2. THE Workflow_Automation_Agent SHALL log workflow execution with action_type, target_entity, execution_status, and timestamp
3. WHEN workflow execution completes, THE Workflow_Automation_Agent SHALL store execution results in DynamoDB keyed by org_id
4. IF workflow execution fails, THEN THE Workflow_Automation_Agent SHALL log the failure reason and mark execution_status as failed
5. THE Workflow_Automation_Agent SHALL support at least one workflow type: update_invoice_status

### Requirement 7: Post-Action Re-evaluation

**User Story:** As the system, I want to measure prediction accuracy after executing actions, so that I can improve future strategy recommendations.

#### Acceptance Criteria

1. WHEN a workflow execution completes, THE Reeval_Agent SHALL recalculate BSI for the organization
2. THE Reeval_Agent SHALL compare the new BSI with the predicted BSI improvement from the executed strategy
3. THE Reeval_Agent SHALL compute prediction_accuracy as a percentage difference between predicted and actual improvement
4. WHEN re-evaluation completes, THE Reeval_Agent SHALL store the evaluation results in DynamoDB with execution_id reference
5. THE Reeval_Agent SHALL use the same risk calculation methodology as the Stability_Intelligence_Agent

### Requirement 8: Dashboard Visualization

**User Story:** As a business owner, I want a visual dashboard, so that I can monitor operational health and review recommendations.

#### Acceptance Criteria

1. THE Dashboard_UI SHALL display the current BSI value with visual indicator (color-coded by health level)
2. THE Dashboard_UI SHALL display BSI trend over time as a line chart
3. THE Dashboard_UI SHALL display top 5 operational risks ranked by severity
4. THE Dashboard_UI SHALL display active strategy recommendations with predicted impact
5. THE Dashboard_UI SHALL display action execution history with timestamps and outcomes
6. WHEN dashboard data is requested, THE NovaSME_System SHALL retrieve data from DynamoDB filtered by org_id
7. THE Dashboard_UI SHALL refresh data every 30 seconds while active

### Requirement 9: Voice Operational Summaries

**User Story:** As a business owner, I want to ask voice questions about my business, so that I can get operational insights hands-free.

#### Acceptance Criteria

1. WHERE voice interface is enabled, WHEN a voice query is received, THE Voice_Interface SHALL transcribe it using Nova Sonic
2. WHERE voice interface is enabled, THE Voice_Interface SHALL support queries: "How stable is my business?" and "Which invoices are overdue?"
3. WHERE voice interface is enabled, WHEN a query is processed, THE Voice_Interface SHALL generate a voice response summarizing operational state using Nova Sonic
4. WHERE voice interface is enabled, THE Voice_Interface SHALL retrieve current BSI and relevant signals to answer queries
5. WHERE voice interface is enabled, IF transcription fails, THEN THE Voice_Interface SHALL return an error message

### Requirement 10: Signal Processing Logging

**User Story:** As a system administrator, I want all processed signals logged, so that I can audit system behavior and troubleshoot issues.

#### Acceptance Criteria

1. WHEN any signal is processed, THE NovaSME_System SHALL log the signal_id, org_id, signal_type, processing_status, and timestamp
2. WHEN any agent operation fails, THE NovaSME_System SHALL log the error message, stack trace, and context
3. THE NovaSME_System SHALL store logs in a structured format accessible for debugging
4. THE NovaSME_System SHALL retain logs for at least 30 days

### Requirement 11: Decision Explainability

**User Story:** As a business owner, I want to understand why the system made specific recommendations, so that I can trust and validate AI decisions.

#### Acceptance Criteria

1. WHEN BSI is calculated, THE Stability_Intelligence_Agent SHALL provide reasoning for each risk component score
2. WHEN strategies are generated, THE Strategy_Simulation_Agent SHALL provide reasoning for predicted impact
3. THE Dashboard_UI SHALL display explainability information when a user clicks on a recommendation
4. THE NovaSME_System SHALL store reasoning text with each BSI snapshot and strategy record

### Requirement 12: Multi-Organization Support

**User Story:** As a platform operator, I want to support multiple organizations, so that the system can scale to serve many SMEs.

#### Acceptance Criteria

1. THE NovaSME_System SHALL partition all data by org_id in DynamoDB
2. WHEN any API request is received, THE NovaSME_System SHALL validate org_id and enforce data isolation
3. THE NovaSME_System SHALL prevent cross-organization data access
4. WHEN a new organization is onboarded, THE NovaSME_System SHALL initialize default BSI baseline of 50

### Requirement 13: Prompt Template Management

**User Story:** As a developer, I want prompt templates stored separately from code, so that I can version and modify prompts without code changes.

#### Acceptance Criteria

1. THE NovaSME_System SHALL store all prompt templates in /prompts/v1/ directory
2. THE NovaSME_System SHALL load prompts from files at runtime, not hardcode them in Python modules
3. WHEN a prompt is used, THE NovaSME_System SHALL enforce strict JSON output validation against Pydantic schemas
4. IF prompt output parsing fails, THEN THE NovaSME_System SHALL log the raw output and return a parsing error

### Requirement 14: API Response Validation

**User Story:** As a developer, I want all API responses validated, so that frontend receives consistent, type-safe data.

#### Acceptance Criteria

1. THE NovaSME_System SHALL validate all API responses against Pydantic models before returning to clients
2. IF response validation fails, THEN THE NovaSME_System SHALL return HTTP 500 with error details
3. THE NovaSME_System SHALL use FastAPI automatic validation for request bodies
4. THE NovaSME_System SHALL return validation errors with field-level detail for client debugging

### Requirement 15: Docker Development Environment

**User Story:** As a developer, I want a Docker-first development setup, so that I can run the entire system locally with one command.

#### Acceptance Criteria

1. THE NovaSME_System SHALL provide a docker-compose.yml file that starts backend, frontend, and dependencies
2. WHEN docker-compose up is executed, THE NovaSME_System SHALL start all services and establish network connectivity
3. THE NovaSME_System SHALL use .env files for configuration management
4. THE NovaSME_System SHALL expose backend API on port 8000 and frontend on port 3000 in local development

