'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Party, Rocket, BarChart3, Plus, Search, CheckCircle, ClipboardList } from 'lucide-react'

interface SubmissionFormData {
  title: string
  organization: string
  description: string
  url: string
  amount: string
  currency: string
  deadline: string
  contactEmail: string
}

interface SubmissionResponse {
  status: string
  opportunity_id?: number
  validation_score?: number
  requires_review: boolean
  message: string
  submission_id: string
}

export default function SubmitOpportunity() {
  const router = useRouter()
  const [formData, setFormData] = useState<SubmissionFormData>({
    title: '',
    organization: '',
    description: '',
    url: '',
    amount: '',
    currency: 'USD',
    deadline: '',
    contactEmail: ''
  })
  
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitSuccess, setSubmitSuccess] = useState(false)
  const [submitResult, setSubmitResult] = useState<SubmissionResponse | null>(null)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}
    
    if (!formData.title.trim()) {
      newErrors.title = 'Title is required'
    }
    
    if (!formData.organization.trim()) {
      newErrors.organization = 'Organization is required'
    }
    
    if (!formData.description.trim()) {
      newErrors.description = 'Description is required'
    } else if (formData.description.length < 50) {
      newErrors.description = 'Description must be at least 50 characters'
    }
    
    if (!formData.url.trim()) {
      newErrors.url = 'URL is required'
    } else if (!formData.url.match(/^https?:\/\/.+/)) {
      newErrors.url = 'Please enter a valid URL starting with http:// or https://'
    }
    
    if (formData.amount && isNaN(Number(formData.amount))) {
      newErrors.amount = 'Amount must be a valid number'
    }
    
    if (formData.contactEmail && !formData.contactEmail.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
      newErrors.contactEmail = 'Please enter a valid email address'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }
    
    setIsSubmitting(true)
    setErrors({})
    
    try {
      const response = await fetch('/api/submissions/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          amount: formData.amount ? parseFloat(formData.amount) : null
        })
      })
      
      const result: SubmissionResponse = await response.json()
      
      if (response.ok) {
        setSubmitSuccess(true)
        setSubmitResult(result)
        
        // Reset form after successful submission
        setFormData({
          title: '',
          organization: '',
          description: '',
          url: '',
          amount: '',
          currency: 'USD',
          deadline: '',
          contactEmail: ''
        })
      } else {
        setErrors({ submit: result.message || 'Submission failed. Please try again.' })
      }
    } catch (error) {
      console.error('Submission error:', error)
      setErrors({ submit: 'Network error. Please check your connection and try again.' })
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleInputChange = (field: keyof SubmissionFormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    
    // Clear field-specific error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }))
    }
  }

  if (submitSuccess && submitResult) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12">
        <div className="container mx-auto px-4">
          <div className="max-w-2xl mx-auto">
            {/* Success Message */}
            <div className="bg-white rounded-xl shadow-lg p-8 text-center">
              <div className="mb-6">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <h1 className="text-2xl font-bold text-gray-800 mb-2">
                  <Party className="w-6 h-6 inline mr-2" />
                Submission Successful!
                </h1>
                <p className="text-gray-600">
                  Thank you for contributing to the TAIFA-FIALA community
                </p>
              </div>
              
              {/* Submission Details */}
              <div className="bg-gray-50 rounded-lg p-6 mb-6">
                <h2 className="text-lg font-semibold text-gray-800 mb-4">Submission Details</h2>
                
                <div className="space-y-3 text-left">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Submission ID:</span>
                    <code className="bg-gray-200 px-2 py-1 rounded text-sm">{submitResult.submission_id}</code>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-gray-600">Status:</span>
                    <span className="capitalize font-medium text-green-600">{submitResult.status}</span>
                  </div>
                  
                  {submitResult.validation_score && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Quality Score:</span>
                      <span className="font-medium">
                        {(submitResult.validation_score * 100).toFixed(0)}%
                      </span>
                    </div>
                  )}
                  
                  <div className="flex justify-between">
                    <span className="text-gray-600">Review Status:</span>
                    <span className={`font-medium ${submitResult.requires_review ? 'text-orange-600' : 'text-green-600'}`}>
                      {submitResult.requires_review ? 'Under Review' : 'Auto-Approved'}
                    </span>
                  </div>
                </div>
              </div>
              
              {/* Next Steps */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <h3 className="font-semibold text-blue-800 mb-2">What happens next?</h3>
                <div className="text-sm text-blue-700 space-y-1">
                  {submitResult.requires_review ? (
                    <>
                      <p>• Your submission will be reviewed by our community within 24-48 hours</p>
                      <p>• You'll receive an email notification once the review is complete</p>
                      <p>• Track your submission status using the ID above</p>
                    </>
                  ) : (
                    <>
                      <p>• Your submission has been automatically approved and published</p>
                      <p>• It will appear in search results within the next hour</p>
                      <p>• Thank you for the high-quality submission!</p>
                    </>
                  )}
                </div>
              </div>
              
              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <button
                  onClick={() => router.push(`/submissions/track?id=${submitResult.submission_id}`)}
                  className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <BarChart3 className="w-5 h-5 inline mr-2" />
                  Track Submission
                </button>
                
                <button
                  onClick={() => setSubmitSuccess(false)}
                  className="bg-gray-600 text-white px-6 py-3 rounded-lg hover:bg-gray-700 transition-colors"
                >
                  <Plus className="w-5 h-5 inline mr-2" />
                  Submit Another
                </button>
                
                <button
                  onClick={() => router.push('/funding')}
                  className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors"
                >
                  <Search className="w-5 h-5 inline mr-2" />
                  Browse Opportunities
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-800 mb-3">
              <Rocket className="w-6 h-6 inline mr-2" />
            Submit Funding Opportunity
            </h1>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Help the African AI community by sharing funding opportunities you've discovered. 
              Your contribution helps researchers and entrepreneurs across the continent.
            </p>
          </div>
          
          {/* Guidelines */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
            <h2 className="text-lg font-semibold text-blue-800 mb-3 flex items-center space-x-2">
              <ClipboardList className="w-5 h-5" />
              <span>Submission Guidelines</span>
            </h2>
            <div className="grid md:grid-cols-2 gap-4 text-sm text-blue-700">
              <div>
                <h3 className="font-medium mb-2 flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4" />
                  <span>Good submissions include:</span>
                </h3>
                <ul className="space-y-1">
                  <li>• Clear, descriptive titles</li>
                  <li>• AI or technology-related funding</li>
                  <li>• Opportunities open to African applicants</li>
                  <li>• Accurate deadlines and amounts</li>
                  <li>• Links to official application pages</li>
                </ul>
              </div>
              <div>
                <h3 className="font-medium mb-2">❌ Please don't submit:</h3>
                <ul className="space-y-1">
                  <li>• Expired opportunities</li>
                  <li>• Opportunities not relevant to AI/tech</li>
                  <li>• Duplicate submissions</li>
                  <li>• Non-African or restricted funding</li>
                  <li>• Links to general websites</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Submission Form */}
          <div className="bg-white rounded-xl shadow-lg p-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Title */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Funding Title *
                </label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => handleInputChange('title', e.target.value)}
                  className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                    errors.title ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="e.g., AI for Healthcare Innovation Grant Program"
                />
                {errors.title && <p className="text-red-500 text-sm mt-1">{errors.title}</p>}
              </div>

              {/* Organization */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Funding Organization *
                </label>
                <input
                  type="text"
                  value={formData.organization}
                  onChange={(e) => handleInputChange('organization', e.target.value)}
                  className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                    errors.organization ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="e.g., Gates Foundation, World Bank, African Development Bank"
                />
                {errors.organization && <p className="text-red-500 text-sm mt-1">{errors.organization}</p>}
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description *
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  rows={5}
                  className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                    errors.description ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="Provide a detailed description of the funding opportunity including eligibility criteria, focus areas, and application requirements..."
                />
                <div className="flex justify-between items-center mt-1">
                  {errors.description && <p className="text-red-500 text-sm">{errors.description}</p>}
                  <p className="text-gray-500 text-sm ml-auto">
                    {formData.description.length}/500 characters (minimum 50)
                  </p>
                </div>
              </div>

              {/* URL */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Application URL *
                </label>
                <input
                  type="url"
                  value={formData.url}
                  onChange={(e) => handleInputChange('url', e.target.value)}
                  className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                    errors.url ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="https://example.com/apply"
                />
                {errors.url && <p className="text-red-500 text-sm mt-1">{errors.url}</p>}
              </div>

              {/* Amount and Currency */}
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Funding Amount (Optional)
                  </label>
                  <input
                    type="number"
                    value={formData.amount}
                    onChange={(e) => handleInputChange('amount', e.target.value)}
                    className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                      errors.amount ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="50000"
                  />
                  {errors.amount && <p className="text-red-500 text-sm mt-1">{errors.amount}</p>}
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Currency
                  </label>
                  <select
                    value={formData.currency}
                    onChange={(e) => handleInputChange('currency', e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="USD">USD ($)</option>
                    <option value="EUR">EUR (€)</option>
                    <option value="GBP">GBP (£)</option>
                    <option value="CAD">CAD (C$)</option>
                    <option value="ZAR">ZAR (R)</option>
                    <option value="NGN">NGN (₦)</option>
                    <option value="KES">KES (KSh)</option>
                    <option value="GHS">GHS (₵)</option>
                  </select>
                </div>
              </div>

              {/* Deadline */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Application Deadline (Optional)
                </label>
                <input
                  type="date"
                  value={formData.deadline}
                  onChange={(e) => handleInputChange('deadline', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              {/* Contact Email */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Contact Email (Optional)
                </label>
                <input
                  type="email"
                  value={formData.contactEmail}
                  onChange={(e) => handleInputChange('contactEmail', e.target.value)}
                  className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                    errors.contactEmail ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="contact@organization.org"
                />
                {errors.contactEmail && <p className="text-red-500 text-sm mt-1">{errors.contactEmail}</p>}
              </div>

              {/* Submit Error */}
              {errors.submit && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <p className="text-red-700">{errors.submit}</p>
                </div>
              )}

              {/* Submit Button */}
              <div className="pt-4">
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className={`w-full py-4 px-6 rounded-lg font-medium text-white transition-colors ${
                    isSubmitting 
                      ? 'bg-gray-400 cursor-not-allowed' 
                      : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700'
                  }`}
                >
                  {isSubmitting ? (
                    <span className="flex items-center justify-center">
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Processing Submission...
                    </span>
                  ) : (
                    <><Rocket className="w-5 h-5 inline mr-2" />Submit Funding Opportunity</>
                  )}
                </button>
              </div>
            </form>
          </div>

          {/* Community Info */}
          <div className="mt-8 text-center">
            <p className="text-gray-600">
              By submitting, you agree to share this information with the TAIFA-FIALA community. 
              All submissions are reviewed for quality and relevance.
            </p>
            <p className="text-sm text-gray-500 mt-2">
              Need help? Contact us at <a href="mailto:support@taifa-fiala.org" className="text-blue-600 hover:underline">support@taifa-fiala.org</a>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}