# TAIFA-FIALA Blog System

## Overview

The TAIFA-FIALA blog system allows you to easily add blog posts to the Funding Landscape page by dropping MDX files into the content directory. The system automatically generates blog post cards and handles routing.

## Quick Start

### 1. Add a New Blog Post

Create a new `.mdx` file in `src/content/blog/` with the following structure:

```mdx
---
title: "Your Blog Post Title"
excerpt: "A compelling excerpt that will appear on the card and as the meta description."
author: "Dr. Jamie Forrest" # or "Co-founder"
date: "2025-01-29" # YYYY-MM-DD format
category: "Funding Analysis" # See categories below
---

# Your Blog Post Title

Your blog content goes here. You can use:

- **Markdown formatting**
- Lists and bullet points
- Code blocks
- Links and images
- All standard MDX features

## Subheadings

Write your content naturally. The system will automatically:
- Calculate read time
- Generate the blog card
- Create the individual blog post page
- Handle routing
```

### 2. Valid Categories

Choose from these predefined categories (affects card colors):
- `Funding Analysis` - Purple accent (taifa-accent)
- `Investment Strategy` - Amber accent (taifa-secondary) 
- `Infrastructure` - Slate accent (taifa-primary)
- `AI Development` - Amber accent (taifa-secondary)

### 3. File Naming

Use kebab-case for filenames:
- ✅ `two-track-funding-reality.mdx`
- ✅ `patient-capital-africa.mdx`
- ❌ `Two Track Funding Reality.mdx`
- ❌ `patient_capital_africa.mdx`

## Automated Features

### Blog Card Generation
- Automatically appears on `/funding-landscape` page
- Shows latest 4 posts
- Includes author avatar (initials)
- Color-coded by category
- Read time calculation
- Hover effects and animations

### Individual Post Pages
- Accessible at `/blog/[slug]`
- Full MDX rendering
- Proper SEO metadata
- Navigation back to funding landscape
- Responsive design

### CI/CD Integration

The system includes GitHub Actions automation:

```bash
# Validate all blog posts
npm run validate-blog

# Generate blog summary
npm run blog-summary
```

## Workflow

### For New Posts:

1. **Create MDX file** in `src/content/blog/`
2. **Validate locally**: `npm run validate-blog`
3. **Test locally**: `npm run dev`
4. **Commit with message**: `git commit -m "Add blog post: Your Title"`
5. **Push to main**: Triggers automatic validation and deployment

### For Updates:

1. **Edit existing MDX file**
2. **Validate**: `npm run validate-blog`
3. **Commit and push**: Same as new posts

## File Structure

```
src/
├── content/
│   └── blog/
│       ├── two-track-funding-reality.mdx
│       ├── patient-capital-africa.mdx
│       └── your-new-post.mdx
├── lib/
│   └── blog.ts                    # Blog utilities
├── app/
│   ├── blog/
│   │   └── [slug]/
│   │       └── page.tsx           # Individual post template
│   └── funding-landscape/
│       └── page.tsx               # Contains BlogPostsSection
└── scripts/
    ├── validate-blog.js           # Validation script
    └── blog-summary.js            # Summary generator
```

## Troubleshooting

### Common Issues:

1. **Missing frontmatter fields**: Ensure all required fields are present
2. **Invalid date format**: Use YYYY-MM-DD format
3. **Invalid category**: Use one of the predefined categories
4. **Empty content**: Make sure there's actual content below the frontmatter

### Validation Errors:

Run `npm run validate-blog` to see specific errors:
```bash
❌ your-post.mdx:
   - Missing required field: excerpt
   - Invalid date format: Jan 29, 2025. Use YYYY-MM-DD format.
```

## Advanced Features

### Custom Styling
Blog posts inherit TAIFA brand colors and styling automatically.

### SEO Optimization
- Automatic meta descriptions from excerpts
- Proper title formatting
- Structured data for blog posts

### Performance
- Static generation at build time
- Optimized for fast loading
- Automatic read time calculation

## Examples

See the existing blog posts in `src/content/blog/` for reference:
- `two-track-funding-reality.mdx` - Funding analysis example
- `patient-capital-africa.mdx` - Investment strategy example

## Support

For issues or questions about the blog system, check:
1. Validation output: `npm run validate-blog`
2. Blog summary: `npm run blog-summary`
3. Build logs during deployment
4. GitHub Actions workflow results
