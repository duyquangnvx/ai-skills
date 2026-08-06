---
paths:
  - "**/api/**"
  - "**/routes/**"
  - "**/*.route.ts"
---

# API Response Format

Use a consistent envelope for all API responses:

- Include a success/status indicator
- Include the data payload (nullable on error)
- Include an error message field (nullable on success)
- Include metadata for paginated responses (total, page, limit)
