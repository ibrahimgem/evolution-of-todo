# Neon PostgreSQL Deployment

## Database Provisioning

1.  **Create Project**: Log in to Neon and create a new project.
2.  **Get Connection String**: Use the "Connection Details" widget to get the `DATABASE_URL`. Ensure you select "Pooled connection" for serverless functions.
3.  **Branching**: Use Neon branches for development and staging environments.

## Schema Migrations

Always run migrations against the production database using environment variables.

```bash
DATABASE_URL=postgres://user:pass@ep-hostname-pooler.region.aws.neon.tech/neondb?sslmode=require
python -m src.database
```

## Security

- Enable **IP Allowlisting** in Neon settings if your compute has a static IP.
- Rotate credentials regularly.
