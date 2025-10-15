# SE Q&A Prep

## Security
- **Data handling:** This demo uses anonymized/aggregate data; no PII required. In production, we'll enforce **encryption in transit (TLS 1.2+)** and **at rest (KMS-managed keys)**, with **column-level masking** for sensitive fields.
- **Access control:** SSO via **SAML/OIDC** (Okta, Azure AD). **RBAC** for analyst vs. investigator roles; **RLS** (row-level security) by region or LoB.
- **Auditability:** Immutable audit logs, export to SIEM (Splunk, Datadog). All model versions and thresholds tracked.
- **Data residency:** Regionalized deployment and storage (AWS Regions / Azure). Configurable retention + right-to-be-forgotten workflows.

## Performance & Scalability
- Stateless app layer autoscaled on containers/serverless (ECS/Fargate, GKE, Azure Container Apps).
- Data plane: Columnar storage (Parquet) in **S3/GCS/Azure Blob** with **Snowflake/BigQuery** or **Databricks** for heavy analytics. **Caching** via Redis for hot queries.
- Batch + streaming ingestion; **feature store** for model inputs; **orchestration** via Airflow or Step Functions.
- Load testing baseline and SLOs (p95 latency < 1s for dashboard queries; larger batch jobs async).

## Integrations
- **Read:** S3/Blob, Snowflake, BigQuery, Redshift, Databricks, Postgres.
- **Write-back:** Case IDs to Jira/ServiceNow; alerts to Slack/Teams/Email.
- **APIs:** REST/GraphQL endpoints; webhooks; CDC via Kafka for real-time scoring.
- **Partners:** Optional enrichment (address validation, device fingerprinting) via pluggable connectors.

## Model & Analytics
- Isolation Forest baseline + rules. Optionally upgrade to gradient boosting or autoencoder.
- **MLOps:** Model registry, CI/CD, A/B testing, bias/variance tracking, drift alerts.
- **Explainability:** Feature importance, SHAP summaries, reason codes surfaced in UI.

## Roadmap / Gaps
- Case management UI (assign, comment, SLA)
- Multi-tenant admin console
- Advanced explainability views
- SOC 2 Type II / HIPAA BAAs as needed
