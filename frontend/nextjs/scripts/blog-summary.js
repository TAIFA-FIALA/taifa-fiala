#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const matter = require('gray-matter');

const blogDir = path.join(process.cwd(), 'src/content/blog');

function generateBlogSummary() {
  console.log('📊 Generating blog post summary...');
  
  if (!fs.existsSync(blogDir)) {
    console.log('📁 No blog directory found.');
    return;
  }
  
  const files = fs.readdirSync(blogDir).filter(file => file.endsWith('.mdx'));
  
  if (files.length === 0) {
    console.log('📝 No blog posts found.');
    return;
  }
  
  const posts = files.map(file => {
    const filePath = path.join(blogDir, file);
    const content = fs.readFileSync(filePath, 'utf8');
    const { data } = matter(content);
    
    return {
      file,
      title: data.title,
      author: data.author,
      date: data.date,
      category: data.category
    };
  });
  
  // Sort by date (newest first)
  posts.sort((a, b) => new Date(b.date) - new Date(a.date));
  
  console.log('\n📚 Blog Post Summary:');
  console.log('='.repeat(50));
  
  posts.forEach((post, index) => {
    console.log(`${index + 1}. ${post.title}`);
    console.log(`   Author: ${post.author}`);
    console.log(`   Date: ${post.date}`);
    console.log(`   Category: ${post.category}`);
    console.log(`   File: ${post.file}`);
    console.log('');
  });
  
  console.log(`Total posts: ${posts.length}`);
  
  // Generate categories summary
  const categories = {};
  posts.forEach(post => {
    categories[post.category] = (categories[post.category] || 0) + 1;
  });
  
  console.log('\n📂 Posts by Category:');
  Object.entries(categories).forEach(([category, count]) => {
    console.log(`   ${category}: ${count} post${count > 1 ? 's' : ''}`);
  });
}

generateBlogSummary();
