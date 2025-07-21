"use client";

import { useRouter } from 'next/navigation';
import { ChevronRight } from 'lucide-react';

export default function SearchBar() {
  const router = useRouter();

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const query = formData.get('query') as string;
    router.push(`/funding?q=${encodeURIComponent(query)}`);
  };

  return (
    <form 
      className="relative flex shadow-md rounded-lg overflow-hidden"
      onSubmit={handleSubmit}
    >
      <input
        type="text"
        name="query"
        placeholder="Search for funds by funder, recipient, or project"
        className="pl-6 pr-4 py-4 w-full rounded-l-lg border border-gray-200 focus:ring-2 focus:ring-taifa-secondary focus:border-taifa-secondary text-lg bg-white/90 backdrop-blur-sm"
      />
      <button 
        type="submit" 
        className="bg-taifa-secondary hover:bg-yellow-400 text-taifa-primary px-6 py-4 font-medium text-lg transition-colors duration-200 flex items-center"
      >
        Search
        <ChevronRight className="ml-2 h-5 w-5" />
      </button>
    </form>
  );
}