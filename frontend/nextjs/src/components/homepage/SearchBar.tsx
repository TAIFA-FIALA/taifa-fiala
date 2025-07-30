"use client";

import { useState } from 'react';
import { ChevronRight } from 'lucide-react';
import SearchModal from './SearchModal';

export default function SearchBar() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const query = formData.get('query') as string;
    if (query.trim()) {
      setSearchQuery(query);
      setIsModalOpen(true);
    }
  };

  return (
    <>
      <form 
        className="relative flex shadow-md rounded-lg overflow-hidden"
        onSubmit={handleSubmit}
      >
        <input
          type="text"
          name="query"
          placeholder="Search funding announcements by funder, recipient, or project"
          className="pl-6 pr-4 py-4 w-full rounded-l-lg border border-gray-200 focus:ring-2 focus:ring-amber-500 focus:border-amber-500 text-lg bg-white/90 backdrop-blur-sm"
        />
        <button 
          type="submit" 
          className="bg-amber-400 hover:bg-amber-500 text-white px-6 py-4 font-medium text-lg transition-colors duration-200 flex items-center"
        >
          Search
          <ChevronRight className="ml-2 h-5 w-5" />
        </button>
      </form>
      
      <SearchModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        initialQuery={searchQuery}
      />
    </>
  );
}