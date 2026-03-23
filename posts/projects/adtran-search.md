---
title: "Elasticsearch DSL Migration"
summary: "Refactoring a documentation portal's search at Adtran"
coverImage: "/assets/adtran-search.png"
order: 6
---

During my Summer 2025 internship at Adtran, I refactored the search functionality of an internal documentation portal from native Elasticsearch queries to Elasticsearch DSL.

## Why

The existing search implementation used raw Elasticsearch queries scattered throughout the codebase. They were hard to maintain, difficult to test, and tightly coupled to specific Elasticsearch versions.

## What I Did

I migrated the search layer to use Elasticsearch DSL, a high-level Python library that provides a more Pythonic way to write and compose queries. This made the codebase cleaner, more maintainable, and easier for other developers to work with.

## Presentation

At the end of the internship, I prepared and delivered a final presentation to a mixed audience of technical and non-technical stakeholders, explaining both the technical changes and the business value of the refactor.

## Tech

- Python
- Elasticsearch / Elasticsearch DSL
- Documentation portal infrastructure
