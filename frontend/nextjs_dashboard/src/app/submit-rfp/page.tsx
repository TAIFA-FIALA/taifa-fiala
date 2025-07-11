import React, { useState } from 'react';

interface FormData {
  title: string;
  description: string;
  organization_id: number;
  deadline: string;
  amount_usd?: number;
  currency?: string;
  link?: string;
  contact_email?: string;
  status?: string;
  categories?: string[];
}

export default function SubmitRFPPage() {
  const [formData, setFormData] = useState<FormData>({
    title: '',
    description: '',
    organization_id: 1, // Default to 1 for now, will need a way to select organization
    deadline: '',
    currency: 'USD',
    status: 'open',
    categories: [],
  });

  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: name === 'organization_id' || name === 'amount_usd' ? Number(value) : value,
    }));
  };

  const handleCategoryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { value, checked } = e.target;
    setFormData((prevData) => {
      const currentCategories = prevData.categories || [];
      if (checked) {
        return { ...prevData, categories: [...currentCategories, value] };
      } else {
        return { ...prevData, categories: currentCategories.filter((cat) => cat !== value) };
      }
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);

    try {
      const res = await fetch('http://localhost:8000/api/v1/rfps/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          deadline: new Date(formData.deadline).toISOString(), // Ensure ISO format
        }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || `HTTP error! status: ${res.status}`);
      }

      setMessage({ type: 'success', text: 'RFP submitted successfully!' });
      // Optionally reset form
      setFormData({
        title: '',
        description: '',
        organization_id: 1,
        deadline: '',
        currency: 'USD',
        status: 'open',
        categories: [],
      });
    } catch (error: any) {
      setMessage({ type: 'error', text: `Submission failed: ${error.message}` });
    }
  };

  return (
    <div className="container mx-auto p-4 py-8">
      <h1 className="text-3xl font-extrabold text-gray-900 mb-8 text-center">Submit a New RFP</h1>
      {message && (
        <div className={`p-3 mb-4 rounded ${message.type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
          {message.text}
        </div>
      )}
      <form onSubmit={handleSubmit} className="card p-6 space-y-6">
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-700">Title</label>
          <input
            type="text"
            name="title"
            id="title"
            value={formData.title}
            onChange={handleChange}
            required
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50"
          />
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700">Description</label>
          <textarea
            name="description"
            id="description"
            value={formData.description}
            onChange={handleChange}
            required
            rows={5}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50"
          ></textarea>
        </div>

        <div>
          <label htmlFor="organization_id" className="block text-sm font-medium text-gray-700">Organization ID</label>
          <input
            type="number"
            name="organization_id"
            id="organization_id"
            value={formData.organization_id}
            onChange={handleChange}
            required
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50"
          />
        </div>

        <div>
          <label htmlFor="deadline" className="block text-sm font-medium text-gray-700">Deadline</label>
          <input
            type="datetime-local"
            name="deadline"
            id="deadline"
            value={formData.deadline}
            onChange={handleChange}
            required
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50"
          />
        </div>

        <div>
          <label htmlFor="amount_usd" className="block text-sm font-medium text-gray-700">Amount (USD)</label>
          <input
            type="number"
            name="amount_usd"
            id="amount_usd"
            value={formData.amount_usd || ''}
            onChange={handleChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50"
          />
        </div>

        <div>
          <label htmlFor="currency" className="block text-sm font-medium text-gray-700">Currency</label>
          <input
            type="text"
            name="currency"
            id="currency"
            value={formData.currency}
            onChange={handleChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50"
          />
        </div>

        <div>
          <label htmlFor="link" className="block text-sm font-medium text-gray-700">Link to RFP</label>
          <input
            type="url"
            name="link"
            id="link"
            value={formData.link || ''}
            onChange={handleChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50"
          />
        </div>

        <div>
          <label htmlFor="contact_email" className="block text-sm font-medium text-gray-700">Contact Email</label>
          <input
            type="email"
            name="contact_email"
            id="contact_email"
            value={formData.contact_email || ''}
            onChange={handleChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50"
          />
        </div>

        <div>
          <label htmlFor="status" className="block text-sm font-medium text-gray-700">Status</label>
          <select
            name="status"
            id="status"
            value={formData.status}
            onChange={handleChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50"
          >
            <option value="open">Open</option>
            <option value="closed">Closed</option>
            <option value="awarded">Awarded</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Categories</label>
          <div className="mt-1 space-y-2">
            {['AI', 'Education', 'Health', 'Agriculture', 'Fintech', 'Other'].map((category) => (
              <div key={category} className="flex items-center">
                <input
                  type="checkbox"
                  id={`category-${category}`}
                  name="categories"
                  value={category}
                  checked={formData.categories?.includes(category) || false}
                  onChange={handleCategoryChange}
                  className="h-4 w-4 text-primary border-gray-300 rounded focus:ring-primary"
                />
                <label htmlFor={`category-${category}`} className="ml-2 text-sm text-gray-700">{category}</label>
              </div>
            ))}
          </div>
        </div>

        <button
          type="submit"
          className="btn-primary w-full"
        >
          Submit RFP
        </button>
      </form>
    </div>
  );
}