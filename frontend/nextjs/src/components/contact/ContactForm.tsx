'use client'

import React, { useState } from 'react'
import { Send, Mail, User, MessageSquare, Tag, CheckCircle, AlertCircle } from 'lucide-react'

interface ContactFormData {
  name: string
  email: string
  subject: string
  message: string
  inquiryType: 'general' | 'partnership' | 'data' | 'funding' | 'other'
}

interface FormStatus {
  type: 'idle' | 'loading' | 'success' | 'error'
  message: string
}

export default function ContactForm() {
  const [formData, setFormData] = useState<ContactFormData>({
    name: '',
    email: '',
    subject: '',
    message: '',
    inquiryType: 'general'
  })

  const [status, setStatus] = useState<FormStatus>({
    type: 'idle',
    message: ''
  })

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    setStatus({ type: 'loading', message: 'Sending your message...' })

    try {
      const response = await fetch('/api/contact', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      })

      const result = await response.json()

      if (result.success) {
        setStatus({
          type: 'success',
          message: result.message
        })
        // Reset form
        setFormData({
          name: '',
          email: '',
          subject: '',
          message: '',
          inquiryType: 'general'
        })
      } else {
        setStatus({
          type: 'error',
          message: result.message
        })
      }
    } catch (error) {
      console.error('Contact form submission error:', error);
      setStatus({
        type: 'error',
        message: 'Failed to send message. Please try again later.'
      })
    }
  }

  const inquiryTypeOptions = [
    { value: 'general', label: 'General Inquiry' },
    { value: 'partnership', label: 'Research Partnership' },
    { value: 'data', label: 'Data Access Request' },
    { value: 'funding', label: 'Grant Funding' },
    { value: 'other', label: 'Other' }
  ]

  return (
    <div className="max-w-4xl mx-auto">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid md:grid-cols-2 gap-6">
          {/* Name Field */}
          <div className="space-y-2">
            <label htmlFor="name" className="flex items-center text-sm font-medium text-white">
              <User className="h-4 w-4 mr-2 text-amber-400" />
              Full Name *
            </label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              required
              className="w-full px-4 py-3 border-2 border-white/20 rounded-xl focus:border-amber-400 focus:ring-0 transition-colors duration-200 bg-white/10 backdrop-blur-sm text-white placeholder-white/60"
              placeholder="Enter your full name"
            />
          </div>

          {/* Email Field */}
          <div className="space-y-2">
            <label htmlFor="email" className="flex items-center text-sm font-medium text-white">
              <Mail className="h-4 w-4 mr-2 text-amber-400" />
              Email Address *
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              required
              className="w-full px-4 py-3 border-2 border-white/20 rounded-xl focus:border-amber-400 focus:ring-0 transition-colors duration-200 bg-white/10 backdrop-blur-sm text-white placeholder-white/60"
              placeholder="Enter your email address"
            />
          </div>
        </div>

        {/* Inquiry Type */}
        <div className="space-y-2">
          <label htmlFor="inquiryType" className="flex items-center text-sm font-medium text-white">
            <Tag className="h-4 w-4 mr-2 text-amber-400" />
            Inquiry Type
          </label>
          <select
            id="inquiryType"
            name="inquiryType"
            value={formData.inquiryType}
            onChange={handleInputChange}
            className="w-full px-4 py-3 border-2 border-white/20 rounded-xl focus:border-amber-400 focus:ring-0 transition-colors duration-200 bg-white/10 backdrop-blur-sm text-white"
          >
            {inquiryTypeOptions.map(option => (
              <option key={option.value} value={option.value} className="bg-slate-700 text-white">
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {/* Subject Field */}
        <div className="space-y-2">
          <label htmlFor="subject" className="flex items-center text-sm font-medium text-white">
            <MessageSquare className="h-4 w-4 mr-2 text-amber-400" />
            Subject *
          </label>
          <input
            type="text"
            id="subject"
            name="subject"
            value={formData.subject}
            onChange={handleInputChange}
            required
            className="w-full px-4 py-3 border-2 border-white/20 rounded-xl focus:border-amber-400 focus:ring-0 transition-colors duration-200 bg-white/10 backdrop-blur-sm text-white placeholder-white/60"
            placeholder="Brief subject of your inquiry"
          />
        </div>

        {/* Message Field */}
        <div className="space-y-2">
          <label htmlFor="message" className="flex items-center text-sm font-medium text-white">
            <MessageSquare className="h-4 w-4 mr-2 text-amber-400" />
            Message *
          </label>
          <textarea
            id="message"
            name="message"
            value={formData.message}
            onChange={handleInputChange}
            required
            rows={6}
            className="w-full px-4 py-3 border-2 border-white/20 rounded-xl focus:border-amber-400 focus:ring-0 transition-colors duration-200 bg-white/10 backdrop-blur-sm text-white placeholder-white/60 resize-none"
            placeholder="Please provide details about your inquiry..."
          />
        </div>

        {/* Status Messages */}
        {status.type !== 'idle' && (
          <div className={`p-4 rounded-xl border-2 flex items-center space-x-3 backdrop-blur-sm ${
            status.type === 'success' 
              ? 'bg-green-500/20 border-green-400/30 text-green-100' 
              : status.type === 'error'
              ? 'bg-red-500/20 border-red-400/30 text-red-100'
              : 'bg-blue-500/20 border-blue-400/30 text-blue-100'
          }`}>
            {status.type === 'success' && <CheckCircle className="h-5 w-5 text-green-400" />}
            {status.type === 'error' && <AlertCircle className="h-5 w-5 text-red-400" />}
            {status.type === 'loading' && (
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-amber-400"></div>
            )}
            <span className="font-medium">{status.message}</span>
          </div>
        )}

        {/* Submit Button */}
        <div className="flex justify-center">
          <button
            type="submit"
            disabled={status.type === 'loading'}
            className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-amber-500 to-amber-600 text-slate-900 font-semibold rounded-xl hover:from-amber-400 hover:to-amber-500 focus:outline-none focus:ring-4 focus:ring-amber-400/30 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl"
          >
            {status.type === 'loading' ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-slate-900 mr-3"></div>
                Sending...
              </>
            ) : (
              <>
                <Send className="h-5 w-5 mr-3" />
                Send Message
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  )
}
