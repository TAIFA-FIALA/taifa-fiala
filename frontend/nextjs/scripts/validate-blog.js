#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const matter = require('gray-matter');

const blogDir = path.join(process.cwd(), 'src/content/blog');

function validateBlogPost(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const { data, content: mdxContent } = matter(content);
  
  const requiredFields = ['title', 'excerpt', 'author', 'date', 'category'];
  const errors = [];
  
  // Check required frontmatter fields
  for (const field of requiredFields) {
    if (!data[field]) {
      errors.push(`Missing required field: ${field}`);
    }
  }
  
  // Validate date format
  if (data.date && isNaN(Date.parse(data.date))) {
    errors.push(`Invalid date format: ${data.date}. Use YYYY-MM-DD format.`);
  }
  
  // Check if content exists
  if (!mdxContent.trim()) {
    errors.push('Blog post content is empty');
  }
  
  // Validate category
  const validCategories = ['Funding Analysis', 'Investment Strategy', 'Infrastructure', 'AI Development'];
  if (data.category && !validCategories.includes(data.category)) {
    errors.push(`Invalid category: ${data.category}. Valid categories: ${validCategories.join(', ')}`);
  }
  
  return errors;
}

function main() {
  console.log('🔍 Validating blog posts...');
  
  if (!fs.existsSync(blogDir)) {
    console.log('📁 No blog directory found. Creating...');
    fs.mkdirSync(blogDir, { recursive: true });
    console.log('✅ Blog directory created.');
    return;
  }
  
  const files = fs.readdirSync(blogDir).filter(file => file.endsWith('.mdx'));
  
  if (files.length === 0) {
    console.log('📝 No blog posts found.');
    return;
  }
  
  let hasErrors = false;
  
  for (const file of files) {
    const filePath = path.join(blogDir, file);
    const errors = validateBlogPost(filePath);
    
    if (errors.length > 0) {
      console.log(`❌ ${file}:`);
      errors.forEach(error => console.log(`   - ${error}`));
      hasErrors = true;
    } else {
      console.log(`✅ ${file}`);
    }
  }
  
  if (hasErrors) {
    console.log('\n💥 Blog validation failed. Please fix the errors above.');
    process.exit(1);
  } else {
    console.log(`\n🎉 All ${files.length} blog posts are valid!`);
  }
}

main();
