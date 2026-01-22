#!/usr/bin/env node
/**
 * Health check script for Docker HEALTHCHECK
 * [Task]: T019
 * [From]: specs/004-local-k8s-deployment/spec.md §US1, plan.md §DD-006
 *
 * This script performs a simple HTTP GET request to the /healthz endpoint
 * to verify the Next.js application is running and responding.
 */

const http = require('http');

const options = {
  hostname: 'localhost',
  port: process.env.PORT || 3000,
  path: '/api/healthz',
  method: 'GET',
  timeout: 2000
};

const req = http.request(options, (res) => {
  if (res.statusCode === 200) {
    process.exit(0);
  } else {
    console.error(`Health check failed with status: ${res.statusCode}`);
    process.exit(1);
  }
});

req.on('error', (err) => {
  console.error(`Health check error: ${err.message}`);
  process.exit(1);
});

req.on('timeout', () => {
  console.error('Health check timed out');
  req.destroy();
  process.exit(1);
});

req.end();
