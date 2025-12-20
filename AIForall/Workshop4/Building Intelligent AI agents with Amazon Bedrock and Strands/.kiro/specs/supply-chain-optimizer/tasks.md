# Implementation Plan: Supply Chain Optimizer

## Overview
This implementation plan breaks down the Supply Chain Optimizer feature into discrete, manageable coding tasks. Each task builds incrementally on previous tasks, with property-based tests integrated throughout to validate correctness properties.

---

## Tasks

- [x] 1. Set up project structure and core infrastructure





  - Create project directory structure (src/, tests/, config/)
  - Initialize Strands Agents SDK and dependencies
  - Set up AWS service clients (RDS, DynamoDB, S3, Lambda, EventBridge, SNS)
  - Configure environment variables and credentials
  - Set up logging and observability
  - _Requirements: 8.1_

- [x] 2. Implement data models and database schema


  - Create Product, Inventory, Forecast, PurchaseOrder, Supplier, Anomaly, and Report data models
  - Implement data validation functions for all models
  - Create RDS schema for relational data (products, suppliers, purchase orders)
  - Create DynamoDB tables for real-time data (inventory, forecasts)
  - Implement database connection utilities and transaction support
  - _Requirements: 8.1, 8.2, 8.3_

- [x] 2.1 Write property test for data persistence round trip

  - **Property 32: Data Persistence Round Trip**
  - **Validates: Requirements 8.1, 8.2**

- [x] 3. Implement Demand Forecasting Agent
  - Create agent class with tools for historical data analysis
  - Implement `analyze_sales_history()` tool to retrieve and analyze past sales
  - Implement `generate_forecast()` tool using statistical forecasting (exponential smoothing, ARIMA, or similar)
  - Implement `incorporate_seasonality()` tool to adjust for seasonal patterns
  - Implement `apply_external_factors()` tool to adjust forecasts for promotions/events
  - Store forecasts in DynamoDB with timestamps and confidence intervals
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 3.1 Write property test for demand forecast generation

  - **Property 1: Demand Forecast Generation**
  - **Validates: Requirements 1.1, 1.4**

- [x] 3.2 Write property test for seasonal pattern incorporation

  - **Property 2: Seasonal Pattern Incorporation**
  - **Validates: Requirements 1.2**

- [x] 3.3 Write property test for external factor adjustment

  - **Property 3: External Factor Adjustment**
  - **Validates: Requirements 1.3**

- [x] 3.4 Write unit tests for Demand Forecasting Agent

  - Test forecast generation with various data patterns
  - Test seasonality detection and incorporation
  - Test external factor application
  - Test fallback behavior with insufficient data (edge case)

- [x] 4. Implement Inventory Optimizer Agent
  - Create agent class with tools for inventory optimization
  - Implement `calculate_eoq()` tool using EOQ formula: EOQ = √(2DS/H)
  - Implement `calculate_reorder_point()` tool: (avg daily demand × lead time) + safety stock
  - Implement `optimize_warehouse_distribution()` tool to allocate inventory across warehouses
  - Implement `generate_po_recommendation()` tool to create purchase order suggestions
  - Trigger PO recommendations when inventory falls below reorder point
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 4.1 Write property test for EOQ calculation

  - **Property 4: Economic Order Quantity Calculation**
  - **Validates: Requirements 2.1**

- [x] 4.2 Write property test for reorder point determination

  - **Property 5: Reorder Point Determination**
  - **Validates: Requirements 2.2**

- [x] 4.3 Write property test for purchase order trigger

  - **Property 6: Purchase Order Trigger**
  - **Validates: Requirements 2.3**

- [x] 4.4 Write property test for multi-warehouse optimization

  - **Property 7: Multi-Warehouse Inventory Optimization**
  - **Validates: Requirements 2.4, 6.1, 6.2**

- [x] 4.5 Write property test for inventory recalculation timeliness

  - **Property 8: Inventory Recalculation Timeliness**
  - **Validates: Requirements 2.5**
  - **Status: PASSED** - All 3 property-based tests pass:
    - test_inventory_recalculation_on_demand_change: Validates EOQ recalculation when demand changes
    - test_reorder_point_recalculation_on_lead_time_change: Validates reorder point recalculation when lead time changes
    - test_complete_inventory_recalculation_on_multiple_changes: Validates both parameters changing simultaneously

- [x] 4.6 Write unit tests for Inventory Optimizer Agent

  - Test EOQ calculation with various cost parameters
  - Test reorder point calculation with different lead times
  - Test multi-warehouse distribution optimization
  - Test PO recommendation generation

- [x] 5. Implement Supplier Coordination Agent
  - Create agent class with tools for supplier management
  - Implement `send_purchase_order()` tool to submit orders to suppliers
  - Implement `track_delivery()` tool to monitor order status
  - Implement `compare_suppliers()` tool to evaluate supplier options (price, lead time, reliability)
  - Implement `update_delivery_status()` tool to record delivery information
  - Implement `get_supplier_performance()` tool to retrieve supplier metrics
  - Store supplier data and order history in RDS
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 5.1 Write property test for purchase order placement

  - **Property 9: Purchase Order Placement**
  - **Validates: Requirements 3.1**

- [x] 5.2 Write property test for order tracking

  - **Property 10: Order Tracking**
  - **Validates: Requirements 3.2**

- [x] 5.3 Write property test for forecast update on order confirmation

  - **Property 11: Forecast Update on Order Confirmation**
  - **Validates: Requirements 3.3**

- [x] 5.4 Write property test for delivery delay alert

  - **Property 12: Delivery Delay Alert**
  - **Validates: Requirements 3.4**

- [x] 5.5 Write property test for supplier comparison

  - **Property 13: Supplier Comparison**
  - **Validates: Requirements 3.5**

- [x] 5.6 Write unit tests for Supplier Coordination Agent

  - Test order placement with various suppliers
  - Test delivery tracking and status updates
  - Test supplier comparison logic
  - Test delay alert generation

- [x] 6. Implement Anomaly Detection Agent
  - Create agent class with tools for anomaly detection
  - Implement `detect_inventory_anomaly()` tool to identify unusual inventory levels
  - Implement `detect_supplier_anomaly()` tool to flag supplier performance issues
  - Implement `detect_demand_spike()` tool to identify unexpected demand changes
  - Implement `analyze_root_cause()` tool to investigate anomaly causes
  - Implement `generate_recommendations()` tool to suggest corrective actions
  - Store anomalies in DynamoDB with severity levels and confidence scores
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 6.1 Write property test for inventory deviation detection

  - **Property 14: Inventory Deviation Detection**
  - **Validates: Requirements 4.1**

- [x] 6.2 Write property test for supplier performance degradation detection

  - **Property 15: Supplier Performance Degradation Detection**
  - **Validates: Requirements 4.2**

- [x] 6.3 Write property test for demand spike detection

  - **Property 16: Demand Spike Detection**
  - **Validates: Requirements 4.3**

- [x] 6.4 Write property test for inventory shrinkage detection

  - **Property 17: Inventory Shrinkage Detection**
  - **Validates: Requirements 4.4**

- [x] 6.5 Write property test for anomaly output completeness

  - **Property 18: Anomaly Output Completeness**
  - **Validates: Requirements 4.5**

- [x] 6.6 Write unit tests for Anomaly Detection Agent

  - Test inventory deviation detection with various thresholds
  - Test supplier performance monitoring
  - Test demand spike identification
  - Test root cause analysis

- [x] 7. Implement Report Generation Agent
  - Create agent class with tools for analytics and reporting
  - Implement `calculate_kpis()` tool to compute inventory turnover, stockout rates, supplier performance
  - Implement `generate_report()` tool to create comprehensive analytics reports
  - Implement `create_visualizations()` tool to generate charts and graphs
  - Implement `compare_periods()` tool for year-over-year and period-over-period analysis
  - Implement `generate_recommendations()` tool to provide actionable insights
  - Store reports in S3 with metadata in RDS
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 7.1 Write property test for report generation completeness

  - **Property 19: Report Generation Completeness**
  - **Validates: Requirements 5.1**

- [x] 7.2 Write property test for report visualization inclusion

  - **Property 20: Report Visualization Inclusion**
  - **Validates: Requirements 5.2**

- [x] 7.3 Write property test for period comparison

  - **Property 21: Period Comparison**
  - **Validates: Requirements 5.3**

- [x] 7.4 Write property test for report generation performance

  - **Property 22: Report Generation Performance**
  - **Validates: Requirements 5.4**

- [x] 7.5 Write property test for report recommendations

  - **Property 23: Report Recommendations**
  - **Validates: Requirements 5.5**

- [x] 7.6 Write unit tests for Report Generation Agent

  - Test KPI calculation accuracy
  - Test report generation with various data sets
  - Test visualization generation
  - Test period comparison logic

- [x] 8. Implement multi-warehouse management features
  - Implement warehouse capacity tracking
  - Implement inventory transfer logic between warehouses
  - Implement warehouse disruption handling
  - Implement regional demand-based allocation
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 8.1 Write property test for warehouse capacity management

  - **Property 24: Warehouse Capacity Management**
  - **Validates: Requirements 6.3**

- [x] 8.2 Write property test for supply disruption redistribution

  - **Property 25: Supply Disruption Redistribution**
  - **Validates: Requirements 6.4**

- [x] 8.3 Write property test for inventory transfer tracking

  - **Property 26: Inventory Transfer Tracking**
  - **Validates: Requirements 6.5**

- [x] 8.4 Write unit tests for multi-warehouse management

  - Test warehouse capacity calculations
  - Test inventory transfer logic
  - Test disruption handling
  - Test regional allocation

- [x] 9. Implement alert and notification system
  - Set up SNS topics for different alert types
  - Implement critical inventory alerts
  - Implement delivery delay notifications
  - Implement anomaly alerts with severity levels
  - Implement purchase order status notifications
  - Implement forecast change notifications
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 9.1 Write property test for critical inventory alert

  - **Property 27: Critical Inventory Alert**
  - **Validates: Requirements 7.1**

- [x] 9.2 Write property test for delivery delay impact notification

  - **Property 28: Delivery Delay Impact Notification**
  - **Validates: Requirements 7.2**

- [x] 9.3 Write property test for anomaly alert completeness

  - **Property 29: Anomaly Alert Completeness**
  - **Validates: Requirements 7.3**

- [x] 9.4 Write property test for purchase order status notification

  - **Property 30: Purchase Order Status Notification**
  - **Validates: Requirements 7.4**

- [x] 9.5 Write property test for forecast change notification

  - **Property 31: Forecast Change Notification**
  - **Validates: Requirements 7.5**

- [x] 9.6 Write unit tests for alert and notification system

  - Test alert generation for various conditions
  - Test notification delivery
  - Test alert severity levels

- [x] 10. Implement data integrity and concurrent access handling
  - Implement optimistic locking for concurrent updates
  - Implement transaction support for multi-step operations
  - Implement data validation and checksums
  - Implement conflict resolution strategies
  - _Requirements: 8.3, 8.4_

- [x] 10.1 Write property test for data integrity

  - **Property 33: Data Integrity**
  - **Validates: Requirements 8.3**

- [x] 10.2 Write property test for concurrent access safety

  - **Property 34: Concurrent Access Safety**
  - **Validates: Requirements 8.4**

- [x] 10.3 Write unit tests for data integrity and concurrency

  - Test concurrent access scenarios
  - Test transaction rollback on errors
  - Test data validation

- [x] 11. Implement data archival and retention policies
  - Implement data archival to S3 for old records
  - Implement retention policy enforcement
  - Implement queryable archive access
  - _Requirements: 8.5_

- [x] 11.1 Write property test for data archival and accessibility

  - **Property 35: Data Archival and Accessibility**
  - **Validates: Requirements 8.5**

- [x] 11.2 Write unit tests for data archival

  - Test archival process
  - Test archive queryability
  - Test retention policy enforcement

- [x] 12. Implement event-driven orchestration
  - Set up EventBridge rules for inventory updates
  - Set up scheduled forecasting jobs (daily)
  - Set up scheduled optimization jobs (daily)
  - Set up scheduled anomaly detection jobs (hourly)
  - Set up scheduled report generation jobs (weekly)
  - Implement Lambda functions to trigger agent workflows
  - _Requirements: 1.1, 2.1, 4.1, 5.1_

- [x] 12.1 Write integration tests for event-driven workflows

  - Test end-to-end inventory update workflow
  - Test forecasting job execution
  - Test optimization job execution
  - Test anomaly detection workflow
  - Test report generation workflow

- [x] 13. Implement agent orchestration and communication
  - Create orchestrator to coordinate agent execution
  - Implement agent communication patterns (sequential, parallel, conditional)
  - Implement error handling and retry logic
  - Implement agent state management
  - _Requirements: 1.1, 2.1, 3.1, 4.1, 5.1_

- [x] 13.1 Write integration tests for agent orchestration

  - Test agent communication and data passing
  - Test error handling and recovery
  - Test orchestration workflows

- [x] 14. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 15. Implement API endpoints for system interaction
  - Create REST API for inventory queries
  - Create API for purchase order management
  - Create API for report retrieval
  - Create API for anomaly queries
  - Create API for supplier management
  - Implement authentication and authorization
  - _Requirements: 1.1, 2.1, 3.1, 4.1, 5.1_

- [x] 15.1 Write integration tests for API endpoints

  - Test inventory query endpoints
  - Test PO management endpoints
  - Test report retrieval endpoints
  - Test anomaly query endpoints

- [x] 16. Implement monitoring and observability
  - Set up CloudWatch dashboards for key metrics
  - Implement distributed tracing with X-Ray
  - Implement custom metrics for agent performance
  - Set up alarms for SLA violations
  - _Requirements: 5.4_

- [x] 16.1 Write tests for monitoring and observability

  - Test metric collection
  - Test dashboard data accuracy
  - Test alarm triggering

- [x] 17. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

