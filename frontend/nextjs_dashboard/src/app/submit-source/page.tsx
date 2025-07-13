'use client';

import React, { useState, useEffect } from 'react';

interface FormOptions {
  source_types: { value: string; label: string }[];
  update_frequencies: { value: string; label: string }[];
  expected_volumes: { value: string; label: string }[];
  languages: { value: string; label: string }[];
  african_countries: string[];
  african_regions: string[];
}

interface FormData {
  name: string;
  url: string;
  contact_person: string;
  contact_email: string;
  source_type: string;
  update_frequency: string;
  geographic_focus: string[];
  expected_volume: string;
  sample_urls: string[];
  ai_relevance_estimate: number;
  africa_relevance_estimate: number;
  language: string;
  submitter_role: string;
  has_permission: boolean;
  preferred_contact: string;
}

export default function SubmitSourcePage() {
  const [formData, setFormData] = useState<FormData>({
    name: '',
    url: '',
    contact_person: '',
    contact_email: '',
    source_type: 'webpage',
    update_frequency: 'monthly',
    geographic_focus: [],
    expected_volume: '5-20',
    sample_urls: [''],
    ai_relevance_estimate: 80,
    africa_relevance_estimate: 80,
    language: 'English',
    submitter_role: '',
    has_permission: false,
    preferred_contact: 'email',
  });

  const [formOptions, setFormOptions] = useState<FormOptions | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    async function fetchFormOptions() {
      try {
        const res = await fetch('http://localhost:8000/api/v1/source-validation/submit-form');
        if (!res.ok) throw new Error('Failed to fetch form options');
        const data = await res.json();
        setFormOptions(data);
      } catch (error) {
        setMessage({ type: 'error', text: 'Could not load form options. Please try again later.' });
      }
    }
    fetchFormOptions();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    const checked = (e.target as HTMLInputElement).checked;
    
    setFormData((prevData) => ({
      ...prevData,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleMultiSelectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const { name, options } = e.target;
    const value: string[] = [];
    for (let i = 0, l = options.length; i < l; i++) {
      if (options[i].selected) {
        value.push(options[i].value);
      }
    }
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSampleUrlChange = (index: number, value: string) => {
    const newSampleUrls = [...formData.sample_urls];
    newSampleUrls[index] = value;
    setFormData(prev => ({ ...prev, sample_urls: newSampleUrls }));
  };

  const addSampleUrl = () => {
    setFormData(prev => ({ ...prev, sample_urls: [...prev.sample_urls, ''] }));
  };

  const removeSampleUrl = (index: number) => {
    const newSampleUrls = formData.sample_urls.filter((_, i) => i !== index);
    setFormData(prev => ({ ...prev, sample_urls: newSampleUrls }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);
    setIsLoading(true);

    try {
      const res = await fetch('http://localhost:8000/api/v1/source-validation/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          ai_relevance_estimate: Number(formData.ai_relevance_estimate),
          africa_relevance_estimate: Number(formData.africa_relevance_estimate),
        }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || `HTTP error! status: ${res.status}`);
      }

      const result = await res.json();
      setMessage({ type: 'success', text: `Source submitted successfully! Submission ID: ${result.submission_id}. Next steps: ${result.next_steps.join(', ')}` });
      // Reset form
    } catch (error: any) {
      setMessage({ type: 'error', text: `Submission failed: ${error.message}` });
    } finally {
      setIsLoading(false);
    }
  };

  if (!formOptions) {
    return <div className="container mx-auto p-4 text-center">Loading form...</div>;
  }

  return (
    <div className="container mx-auto p-4 py-8">
      <h1 className="text-3xl font-extrabold text-gray-900 mb-2 text-center">Submit a New Funding Source</h1>
      <p className="text-center text-gray-600 mb-8">Help us grow our database by submitting a new source of funding opportunities.</p>
      
      {message && (
        <div className={`p-3 mb-4 rounded ${message.type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
          {message.text}
        </div>
      )}

      <form onSubmit={handleSubmit} className="card p-6 space-y-6">
        {/* Form fields will be added in subsequent steps */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Source Details */}
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700">Source Name</label>
            <input type="text" name="name" id="name" value={formData.name} onChange={handleChange} required className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50" />
          </div>
          <div>
            <label htmlFor="url" className="block text-sm font-medium text-gray-700">Source URL</label>
            <input type="url" name="url" id="url" value={formData.url} onChange={handleChange} required className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50" />
          </div>
          <div>
            <label htmlFor="source_type" className="block text-sm font-medium text-gray-700">Source Type</label>
            <select name="source_type" id="source_type" value={formData.source_type} onChange={handleChange} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50">
              {formOptions.source_types.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
            </select>
          </div>
          <div>
            <label htmlFor="language" className="block text-sm font-medium text-gray-700">Primary Language</label>
            <select name="language" id="language" value={formData.language} onChange={handleChange} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50">
              {formOptions.languages.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
            </select>
          </div>
        </div>
        
        {/* Contact Information */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label htmlFor="contact_person" className="block text-sm font-medium text-gray-700">Your Name</label>
            <input type="text" name="contact_person" id="contact_person" value={formData.contact_person} onChange={handleChange} required className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50" />
          </div>
          <div>
            <label htmlFor="contact_email" className="block text-sm font-medium text-gray-700">Your Email</label>
            <input type="email" name="contact_email" id="contact_email" value={formData.contact_email} onChange={handleChange} required className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50" />
          </div>
        </div>

        {/* Relevance & Scope */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
                <label htmlFor="geographic_focus" className="block text-sm font-medium text-gray-700">Geographic Focus</label>
                <select multiple name="geographic_focus" id="geographic_focus" value={formData.geographic_focus} onChange={handleMultiSelectChange} className="mt-1 block w-full h-32 rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50">
                    <optgroup label="Regions">
                        {formOptions.african_regions.map(region => <option key={region} value={region}>{region}</option>)}
                    </optgroup>
                    <optgroup label="Countries">
                        {formOptions.african_countries.map(country => <option key={country} value={country}>{country}</option>)}
                    </optgroup>
                </select>
            </div>
            <div className="space-y-6">
                <div>
                    <label htmlFor="ai_relevance_estimate" className="block text-sm font-medium text-gray-700">AI Relevance Estimate: {formData.ai_relevance_estimate}%</label>
                    <input type="range" min="0" max="100" step="5" name="ai_relevance_estimate" id="ai_relevance_estimate" value={formData.ai_relevance_estimate} onChange={handleChange} className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer" />
                </div>
                <div>
                    <label htmlFor="africa_relevance_estimate" className="block text-sm font-medium text-gray-700">Africa Relevance Estimate: {formData.africa_relevance_estimate}%</label>
                    <input type="range" min="0" max="100" step="5" name="africa_relevance_estimate" id="africa_relevance_estimate" value={formData.africa_relevance_estimate} onChange={handleChange} className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer" />
                </div>
            </div>
        </div>

        {/* Sample URLs */}
        <div>
          <label className="block text-sm font-medium text-gray-700">Sample URLs</label>
          {formData.sample_urls.map((url, index) => (
            <div key={index} className="flex items-center mt-1">
              <input type="url" value={url} onChange={(e) => handleSampleUrlChange(index, e.target.value)} placeholder="https://example.com/funding-opportunity" required className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50" />
              {formData.sample_urls.length > 1 && <button type="button" onClick={() => removeSampleUrl(index)} className="ml-2 text-red-600">Remove</button>}
            </div>
          ))}
          <button type="button" onClick={addSampleUrl} className="mt-2 text-sm text-primary">Add another URL</button>
        </div>

        <div className="flex items-center">
            <input type="checkbox" name="has_permission" id="has_permission" checked={formData.has_permission} onChange={handleChange} className="h-4 w-4 text-primary border-gray-300 rounded focus:ring-primary" />
            <label htmlFor="has_permission" className="ml-2 block text-sm text-gray-900">I have permission to submit this source on behalf of the organization.</label>
        </div>

        <button type="submit" disabled={isLoading} className="btn-primary w-full disabled:bg-gray-400">
          {isLoading ? 'Submitting...' : 'Submit Source'}
        </button>
      </form>
    </div>
  );
}