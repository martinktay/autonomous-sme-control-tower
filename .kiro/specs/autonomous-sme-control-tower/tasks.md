# Implementation Plan: Autonomous SME Control Tower

## Overview

This implementation plan breaks down the Autonomous SME Control Tower into discrete coding tasks. The system is a multi-agent AI platform that monitors operational signals, diagnoses business instability, simulates strategies, executes workflows autonomously, and re-evaluates outcomes in a closed loop using AWS Bedrock Nova models.

The implementation follows a layered approach:
1. Infrastructure and project setup
2. Core backend services and data models
3. Agent implementations with prompt templates
4. Frontend UI components and pages
5. Integration and end-to-end workflows
6. Testing and validation

## Tasks

- [x] 1. Project infrastructure and configuration setup
  - [x] 1.1 Set up Docker development environment
    - Create docker-compose.yml with backend, frontend services
    - Configure .env files for AWS credentials and configuration
    - Set up network connectivity between services
    - Expose backend on port 8000, frontend on port 3000
    - _Requirements: 15.1, 15.2, 15.3, 15.4_

  - [x] 1.2 Initialize backend FastAPI application structure
    - Create backend/app/main.py with FastAPI app initialization
    - Set up CORS middleware for frontend communication
    - Create backend/app/config.py for environment configuration
    - Create directory structure: routers/, agents/, services/, models/, utils/
    - _Requirements: 15.1, 15.4_

  - [x] 1.3 Initialize frontend Next.js application structure
    - Create Next.js 14 app with TypeScript and Tailwind CSS
    - Set up app directory structure for pages
    - Configure API client for backend communication
    - _Requirements: 15.1, 15.4_

  - [x] 1.4 Set up AWS service integrations
    - Create backend/app/utils/bedrock_client.py for Nova model invocations
    - Create backend/app/services/ddb_service.py for DynamoDB operations
    - Create backend/app/services/s3_service.py for document storage
    - Implement error handling with retry logic and circuit breaker patterns
    - _Requirements: 1.5, 2.4, 3.1, 6.1, 12.1_

- [x] 2. Core data models and validation
  - [x] 2.1 Implement Pydantic data models
    - Create backend/app/models/invoice.py with Invoice model
    - Create backend/app/models/email.py with Email model
    - Create backend/app/models/signal.py with Signal model
    - Create backend/app/models/nsi.py with NSISnapshot model
    - Create backend/app/models/strategy.py with Strategy model
    - Create backend/app/models/action.py with ActionExecution model
    - Create backend/app/models/evaluation.py with Evaluation model
    - Add field validation and type constraints to all models
    - _Requirements: 1.2, 2.2, 5.5, 14.1, 14.3_

  - [x]* 2.2 Write unit tests for data models
    - Test field validation and type constraints
    - Test edge cases for numeric ranges (NSI 0-100, confidence 0-1)
    - Test datetime serialization and deserialization
    - _Requirements: 1.2, 2.2, 5.5_

- [x] 3. DynamoDB table setup and data access layer
  - [x] 3.1 Create DynamoDB service layer
    - Implement create, read, update operations in ddb_service.py
    - Add org_id partition key enforcement for all operations
    - Implement query methods filtered by org_id
    - Add error handling for DynamoDB exceptions
    - _Requirements: 1.5, 2.4, 12.1, 12.2_

  - [x] 3.2 Implement data isolation validation
    - Add org_id validation middleware for all API requests
    - Implement cross-organization access prevention
    - Log security events for access violations
    - Return HTTP 403 for unauthorized access attempts
    - _Requirements: 12.2, 12.3_

  - [x]* 3.3 Write property tests for data isolation
    - Test that queries with different org_ids return isolated data
    - Test that cross-organization access attempts are rejected
    - _Requirements: 12.2, 12.3_

- [x] 4. Prompt template management system
  - [x] 4.1 Create prompt template directory structure
    - Create /prompts/v1/ directory
    - Create signal_invoice.md template for invoice extraction
    - Create signal_email.md template for email classification
    - Create risk_diagnosis.md template for NSI calculation
    - Create strategy_planning.md template for strategy generation
    - Create reeval.md template for post-action evaluation
    - Create voice.md template for voice query responses
    - _Requirements: 13.1, 13.2_

  - [x] 4.2 Implement prompt loading utility
    - Create backend/app/utils/prompt_loader.py
    - Implement load_prompt(template_name) function
    - Add template variable substitution support
    - Add error handling for missing templates
    - _Requirements: 13.1, 13.2_

  - [x] 4.3 Implement JSON output validation
    - Add strict JSON parsing with Pydantic schema validation
    - Log raw output when parsing fails
    - Return descriptive parsing errors
    - _Requirements: 13.3, 13.4_

- [x] 5. Signal Intake Agent implementation
  - [x] 5.1 Implement invoice processing
    - Create backend/app/agents/signal_agent.py
    - Implement process_invoice() method using Nova 2 Lite
    - Extract vendor_name, invoice_id, amount, due_date, currency, description
    - Return structured Invoice model
    - Add 5-second timeout enforcement
    - _Requirements: 1.1, 1.2, 1.4_

  - [x] 5.2 Implement email processing
    - Implement process_email() method using Nova 2 Lite
    - Classify as payment_reminder, customer_inquiry, operational_message, or other
    - Extract sender, subject, classification
    - Return structured Email model
    - Add 3-second timeout enforcement
    - _Requirements: 2.1, 2.2, 2.3, 2.5_

  - [x] 5.3 Implement signal storage
    - Store processed signals in DynamoDB with org_id partition key
    - Generate unique signal_id for each signal
    - Set processing_status to "processed"
    - _Requirements: 1.5, 2.4, 10.1_

  - [x]* 5.4 Write unit tests for signal processing
    - Test invoice extraction with sample documents
    - Test email classification for each category
    - Test error handling for extraction failures
    - _Requirements: 1.1, 1.3, 2.1_

- [x] 6. Context Memory Service implementation
  - [x] 6.1 Implement embedding generation
    - Create backend/app/services/memory_service.py
    - Implement generate_embedding() using Nova embeddings model
    - Store embedding vector reference with signal metadata
    - Associate embedding with signal_id, org_id, signal_type, timestamp
    - _Requirements: 3.1, 3.2, 3.3_

  - [x] 6.2 Implement semantic search
    - Implement search_signals() method for semantic similarity search
    - Query embeddings by org_id to enforce data isolation
    - Return ranked results by similarity score
    - _Requirements: 3.1, 3.3_

  - [x] 6.3 Add error handling for embedding failures
    - Log errors when embedding generation fails
    - Continue processing without blocking signal storage
    - _Requirements: 3.4_

  - [x]* 6.4 Write unit tests for memory service
    - Test embedding generation for various signal types
    - Test semantic search with sample queries
    - Test error handling for API failures
    - _Requirements: 3.1, 3.4_

- [x] 7. Checkpoint - Verify signal intake and memory pipeline
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Stability Intelligence Agent implementation
  - [x] 8.1 Implement NSI calculation
    - Create backend/app/agents/risk_agent.py
    - Implement calculate_nsi() method using Nova 2 Lite
    - Calculate liquidity_index, revenue_stability_index, operational_latency_index, vendor_risk_index
    - Compute NSI using weighted formula: (liquidity × 0.30) + (revenue_stability × 0.25) + (operational_latency × 0.25) + (vendor_risk × 0.20)
    - Return NSI value between 0 and 100
    - _Requirements: 4.1, 4.2_

  - [x] 8.2 Implement risk assessment reasoning
    - Use Nova 2 Lite to generate reasoning for each risk component
    - Include cash_runway_risk, invoice_aging_risk, revenue_concentration_risk, expense_volatility_risk, response_latency_risk
    - Store reasoning with NSI snapshot
    - _Requirements: 4.2, 4.4, 11.1_

  - [x] 8.3 Implement NSI snapshot storage
    - Store NSI snapshot in DynamoDB with timestamp and org_id
    - Include all sub-indices and confidence flag
    - _Requirements: 4.3_

  - [x] 8.4 Handle insufficient data scenarios
    - Return NSI of 50 when insufficient data exists
    - Set confidence flag to "low" indicating limited data
    - _Requirements: 4.5_

  - [x]* 8.5 Write unit tests for NSI calculation
    - Test NSI calculation with various signal combinations
    - Test insufficient data handling
    - Test NSI bounds (0-100)
    - _Requirements: 4.1, 4.5_

- [x] 9. Strategy Simulation Agent implementation
  - [x] 9.1 Implement strategy generation
    - Create backend/app/agents/strategy_agent.py
    - Implement generate_strategies() method using Nova 2 Lite
    - Generate 2-3 strategies when NSI < 70
    - Include description, predicted_nsi_improvement, confidence_score, automation_eligibility
    - _Requirements: 5.1, 5.2_

  - [x] 9.2 Implement strategy reasoning
    - Use Nova 2 Lite to reason about strategy effectiveness
    - Provide reasoning for predicted impact
    - Store reasoning with strategy record
    - _Requirements: 5.3, 11.2_

  - [x] 9.3 Implement strategy storage
    - Store strategies in DynamoDB keyed by org_id
    - Link strategies to NSI snapshot via nsi_snapshot_id
    - Return Strategy Pydantic model
    - _Requirements: 5.4, 5.5_

  - [x]* 9.4 Write unit tests for strategy generation
    - Test strategy generation for NSI < 70
    - Test strategy model validation
    - Test reasoning quality
    - _Requirements: 5.1, 5.2, 5.5_

- [x] 10. Workflow Automation Agent implementation
  - [x] 10.1 Implement workflow execution
    - Create backend/app/agents/action_agent.py
    - Implement execute_workflow() method using Nova Act
    - Support update_invoice_status workflow type
    - Log execution with action_type, target_entity, execution_status, timestamp
    - _Requirements: 6.1, 6.2, 6.5_

  - [x] 10.2 Implement execution result storage
    - Store execution results in DynamoDB keyed by org_id
    - Link execution to strategy via strategy_id
    - _Requirements: 6.3_

  - [x] 10.3 Implement failure handling
    - Log failure reason when workflow execution fails
    - Mark execution_status as "failed"
    - _Requirements: 6.4_

  - [x]* 10.4 Write unit tests for workflow execution
    - Test successful workflow execution
    - Test failure handling and logging
    - Test execution result storage
    - _Requirements: 6.1, 6.3, 6.4_

- [x] 11. Re-evaluation Agent implementation
  - [x] 11.1 Implement post-action NSI recalculation
    - Create backend/app/agents/reeval_agent.py
    - Implement recalculate_nsi() method after workflow execution
    - Use same risk calculation methodology as Stability Intelligence Agent
    - _Requirements: 7.1, 7.5_

  - [x] 11.2 Implement prediction accuracy calculation
    - Compare new NSI with predicted NSI improvement
    - Compute prediction_accuracy as percentage difference
    - Formula: 1 - abs(predicted_improvement - actual_improvement) / predicted_improvement
    - _Requirements: 7.2, 7.3_

  - [x] 11.3 Implement evaluation storage
    - Store evaluation results in DynamoDB with execution_id reference
    - Include old_nsi, new_nsi, predicted_improvement, actual_improvement, prediction_accuracy
    - _Requirements: 7.4_

  - [x]* 11.4 Write unit tests for re-evaluation
    - Test NSI recalculation after actions
    - Test prediction accuracy calculation
    - Test evaluation storage
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [x] 12. Checkpoint - Verify agent implementations
  - Ensure all tests pass, ask the user if questions arise.

- [x] 13. API router implementations
  - [x] 13.1 Implement Invoice Router
    - Create backend/app/routers/invoices.py
    - Implement POST /api/invoices/upload endpoint
    - Implement GET /api/invoices/{invoice_id} endpoint
    - Implement GET /api/invoices endpoint with org_id filtering
    - Add request/response validation with Pydantic models
    - _Requirements: 1.1, 1.2, 12.2, 14.1, 14.3_

  - [x] 13.2 Implement Signal Router
    - Create backend/app/routers/signals.py
    - Implement POST /api/signals/email endpoint
    - Implement GET /api/signals endpoint with org_id filtering
    - Implement GET /api/signals/{signal_id} endpoint
    - Add request/response validation with Pydantic models
    - _Requirements: 2.1, 2.2, 12.2, 14.1, 14.3_

  - [x] 13.3 Implement Memory Router
    - Create backend/app/routers/memory.py
    - Implement POST /api/memory/search endpoint for semantic search
    - Implement GET /api/memory/embeddings/{signal_id} endpoint
    - Add org_id filtering for all queries
    - _Requirements: 3.1, 12.2_

  - [x] 13.4 Implement Stability Router
    - Create backend/app/routers/stability.py
    - Implement POST /api/stability/calculate endpoint
    - Implement GET /api/stability/history endpoint for NSI trend
    - Implement GET /api/stability/risks endpoint for risk assessment
    - Add org_id filtering for all queries
    - _Requirements: 4.1, 4.3, 8.1, 12.2_

  - [x] 13.5 Implement Strategy Router
    - Create backend/app/routers/strategy.py
    - Implement POST /api/strategy/simulate endpoint
    - Implement GET /api/strategy endpoint with org_id filtering
    - Implement GET /api/strategy/{strategy_id} endpoint
    - _Requirements: 5.1, 5.4, 12.2_

  - [x] 13.6 Implement Action Router
    - Create backend/app/routers/actions.py
    - Implement POST /api/actions/execute endpoint
    - Implement GET /api/actions endpoint for action history
    - Implement GET /api/actions/{action_id} endpoint
    - Add org_id filtering for all queries
    - _Requirements: 6.1, 6.3, 12.2_

  - [x] 13.7 Implement Voice Router
    - Create backend/app/routers/voice.py
    - Implement POST /api/voice/query endpoint for voice queries
    - Implement GET /api/voice/briefing endpoint for operational briefings
    - Add org_id filtering for all queries
    - _Requirements: 9.1, 9.2, 9.4_

  - [x] 13.8 Implement Orchestration Router
    - Create backend/app/routers/orchestration.py
    - Implement POST /api/orchestration/run-loop endpoint for full closed-loop cycle
    - Coordinate signal intake → NSI calculation → strategy generation → execution → re-evaluation
    - _Requirements: 1.1, 2.1, 4.1, 5.1, 6.1, 7.1_

  - [x]* 13.9 Write integration tests for API routers
    - Test each endpoint with valid and invalid inputs
    - Test org_id isolation across endpoints
    - Test error responses and validation
    - _Requirements: 12.2, 12.3, 14.1, 14.2_

- [x] 14. Voice Interface implementation (optional feature)
  - [x] 14.1 Implement voice query processing
    - Create backend/app/agents/voice_agent.py
    - Implement transcribe_query() using Nova Sonic
    - Support queries: "How stable is my business?" and "Which invoices are overdue?"
    - _Requirements: 9.1, 9.2_

  - [x] 14.2 Implement voice response generation
    - Implement generate_voice_response() using Nova Sonic
    - Retrieve current NSI and relevant signals
    - Generate spoken operational summary
    - _Requirements: 9.3, 9.4_

  - [x] 14.3 Implement transcription error handling
    - Return error message when transcription fails
    - Log transcription errors for debugging
    - _Requirements: 9.5_

  - [x]* 14.4 Write unit tests for voice interface
    - Test query transcription
    - Test response generation
    - Test error handling
    - _Requirements: 9.1, 9.3, 9.5_

- [x] 15. Frontend UI components
  - [x] 15.1 Create NSI Card component
    - Create frontend/components/NSICard.tsx
    - Display current NSI value with color-coded health indicator
    - Green (70-100), Yellow (40-69), Red (0-39)
    - _Requirements: 8.1_

  - [x] 15.2 Create Risk Panel component
    - Create frontend/components/RiskPanel.tsx
    - Display top 5 operational risks ranked by severity
    - Show risk descriptions and severity levels
    - _Requirements: 8.3_

  - [x] 15.3 Create Strategy List component
    - Create frontend/components/StrategyList.tsx
    - Display active strategies with predicted impact
    - Show confidence scores and automation eligibility
    - Add action buttons for strategy execution
    - _Requirements: 8.4_

  - [x] 15.4 Create Action Log component
    - Create frontend/components/ActionLog.tsx
    - Display action execution history with timestamps
    - Show execution status and outcomes
    - _Requirements: 8.5_

  - [x] 15.5 Create NSI Trend Chart component
    - Create frontend/components/NSITrendChart.tsx
    - Display NSI trend over time as line chart
    - Use chart library (e.g., recharts)
    - _Requirements: 8.2_

  - [x] 15.6 Create Voice Widget component
    - Create frontend/components/VoiceWidget.tsx
    - Add voice query input interface
    - Add audio response playback
    - _Requirements: 9.1, 9.3_

- [x] 16. Frontend page implementations
  - [x] 16.1 Create Dashboard page
    - Create frontend/app/dashboard/page.tsx
    - Integrate NSICard, NSITrendChart, RiskPanel, StrategyList, ActionLog components
    - Fetch data from backend API filtered by org_id
    - Implement 30-second auto-refresh
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7_

  - [x] 16.2 Create Upload page
    - Create frontend/app/upload/page.tsx
    - Add invoice document upload interface
    - Add email text submission interface
    - Call /api/invoices/upload and /api/signals/email endpoints
    - Display processing status and results
    - _Requirements: 1.1, 2.1_

  - [x] 16.3 Create Memory page
    - Create frontend/app/memory/page.tsx
    - Add semantic search input interface
    - Display search results with signal details
    - Call /api/memory/search endpoint
    - _Requirements: 3.1_

  - [x] 16.4 Create Strategy page
    - Create frontend/app/strategy/page.tsx
    - Display strategy simulation interface
    - Show generated strategies with details
    - Add strategy execution controls
    - Call /api/strategy/simulate and /api/actions/execute endpoints
    - _Requirements: 5.1, 6.1_

  - [x] 16.5 Create Actions page
    - Create frontend/app/actions/page.tsx
    - Display action execution history
    - Show execution details and outcomes
    - Call /api/actions endpoint
    - _Requirements: 6.3, 8.5_

  - [x] 16.6 Create Portal page
    - Create frontend/app/portal/page.tsx
    - Implement one-click closed-loop demo
    - Call /api/orchestration/run-loop endpoint
    - Display progress through each stage
    - _Requirements: 1.1, 2.1, 4.1, 5.1, 6.1, 7.1_

  - [x] 16.7 Create Voice page
    - Create frontend/app/voice/page.tsx
    - Integrate VoiceWidget component
    - Display voice query history
    - Call /api/voice/query and /api/voice/briefing endpoints
    - _Requirements: 9.1, 9.2, 9.3_

- [x] 17. Logging and error handling
  - [x] 17.1 Implement structured logging
    - Add logging for all signal processing operations
    - Log signal_id, org_id, signal_type, processing_status, timestamp
    - Use structured JSON format
    - _Requirements: 10.1, 10.3_

  - [x] 17.2 Implement error logging
    - Log error message, stack trace, and context for all failures
    - Include request context (org_id) in error logs
    - Log operation and input parameters
    - _Requirements: 10.2, 10.3_

  - [x] 17.3 Implement log retention
    - Configure log storage with 30-day retention
    - Store logs in accessible format for debugging
    - _Requirements: 10.4_

- [x] 18. Explainability features
  - [x] 18.1 Implement NSI reasoning display
    - Add reasoning text to NSI snapshot storage
    - Display reasoning in Dashboard UI when user clicks NSI
    - _Requirements: 11.1, 11.3, 11.4_

  - [x] 18.2 Implement strategy reasoning display
    - Add reasoning text to strategy storage
    - Display reasoning in Strategy UI when user clicks strategy
    - _Requirements: 11.2, 11.3, 11.4_

- [x] 19. Checkpoint - Verify end-to-end workflows
  - Ensure all tests pass, ask the user if questions arise.

- [x] 20. Integration and final wiring
  - [x] 20.1 Wire all routers to FastAPI app
    - Register all routers in backend/app/main.py
    - Configure route prefixes (/api/invoices, /api/signals, etc.)
    - Add global error handlers
    - _Requirements: 14.1, 14.2_

  - [x] 20.2 Configure frontend API client
    - Set up axios or fetch client with base URL
    - Add org_id header to all requests
    - Add error handling for API failures
    - _Requirements: 8.6, 12.2_

  - [x] 20.3 Implement organization initialization
    - Add endpoint for new organization onboarding
    - Initialize default NSI baseline of 50
    - _Requirements: 12.4_

  - [x]* 20.4 Write end-to-end integration tests
    - Test full closed-loop workflow: ingest → diagnose → simulate → execute → evaluate
    - Test multi-organization data isolation
    - Test error recovery and graceful degradation
    - _Requirements: 1.1, 2.1, 4.1, 5.1, 6.1, 7.1, 12.2, 12.3_

- [x] 21. Final checkpoint - Complete system validation
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- The implementation uses Python (FastAPI) for backend and TypeScript (Next.js) for frontend
- All AI capabilities leverage AWS Bedrock Nova models
- Multi-tenancy is enforced through org_id partition keys in all data operations
