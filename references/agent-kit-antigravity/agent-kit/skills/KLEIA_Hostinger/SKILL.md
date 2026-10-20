---
name: KLEIA Framework
description: Guidelines for building the KLEIA ecosystem (Hostinger/Static/SSG).
---

# KLEIA Framework: Hosting & Architecture

This skill defines the technical constraints and design standards for the **KLEIA** web ecosystem.

## Environment: Hostinger (Static/SSG)

1. **Static-First**: For the public site, prioritize SSG (Static Site Generation) or static HTML/JS/CSS. Hostinger's performance is optimized for this.
2. **Optimized Assets**:
   - Use web-standard image formats (WebP/AVIF).
   - Minimize CSS and JS bundles.
   - Favor Vanilla CSS or Tailwind (if requested) with zero-redundancy.
3. **Internal Apps Separation**:
   - Differentiate the public site (Hostinger) from internal tools (Firebase/VPS).
   - Use APIs or Firebase Functions to bridge internal logic and the public site.

## Design Aesthetics (KLEIA Brand)

1. **Visual Excellence**: Implement the "WOW" factor.
   - Use high-end typography (Inter, Outfit).
   - Fluid animations and glassmorphism.
   - Dark mode by default or as a primary toggle.
2. **Modular Components**:
   - Build UI components using a "Brick" approach.
   - Each component must be independent and easily adaptable.

## Project Structure

- `/public`: Assets and static files.
- `/src`: Modular code (TypeScript favored).
- `/scripts`: Deployment and optimization scripts.
