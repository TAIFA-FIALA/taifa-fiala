import { notFound } from 'next/navigation';
import { getBlogPost, getAllBlogPosts } from '@/lib/blog';
import { ArrowLeft, Calendar, Clock, User } from 'lucide-react';
import Link from 'next/link';
import { MDXRemote } from 'next-mdx-remote/rsc';

interface BlogPostPageProps {
  params: Promise<{
    slug: string;
  }>;
}

export async function generateStaticParams() {
  const posts = getAllBlogPosts();
  return posts.map((post) => ({
    slug: post.slug,
  }));
}

export async function generateMetadata({ params }: BlogPostPageProps) {
  const { slug } = await params;
  const post = getBlogPost(slug);
  
  if (!post) {
    return {
      title: 'Post Not Found | TAIFA-FIALA',
    };
  }

  return {
    title: `${post.title} | TAIFA-FIALA Blog`,
    description: post.excerpt,
  };
}

export default async function BlogPostPage({ params }: BlogPostPageProps) {
  const { slug } = await params;
  const post = getBlogPost(slug);

  if (!post) {
    notFound();
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Link 
            href="/funding-landscape" 
            className="inline-flex items-center text-taifa-accent hover:text-taifa-primary transition-colors duration-200 mb-8"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Funding Landscape
          </Link>
          
          <div className="mb-6">
            <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium border ${post.bgClass} ${post.borderClass} ${post.textClass} mb-4`}>
              {post.category}
            </span>
            
            <h1 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4 leading-tight">
              {post.title}
            </h1>
            
            <p className="text-xl text-slate-600 mb-6 leading-relaxed">
              {post.excerpt}
            </p>
            
            <div className="flex items-center space-x-6 text-sm text-slate-500">
              <div className="flex items-center space-x-2">
                <User className="h-4 w-4" />
                <span>{post.author}</span>
              </div>
              <div className="flex items-center space-x-2">
                <Calendar className="h-4 w-4" />
                <span>{new Date(post.date).toLocaleDateString('en-US', { 
                  year: 'numeric', 
                  month: 'long', 
                  day: 'numeric' 
                })}</span>
              </div>
              <div className="flex items-center space-x-2">
                <Clock className="h-4 w-4" />
                <span>{post.readTime}</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <article className="prose prose-lg prose-slate max-w-none">
          <MDXRemote source={post.content} />
        </article>
        
        {/* Back to blog link */}
        <div className="mt-12 pt-8 border-t border-slate-200">
          <Link 
            href="/funding-landscape" 
            className="inline-flex items-center text-taifa-accent hover:text-taifa-primary transition-colors duration-200"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Funding Landscape
          </Link>
        </div>
      </main>
    </div>
  );
}
