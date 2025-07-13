import { NextRequest, NextResponse } from 'next/server'

interface SubmissionData {
  title: string
  organization: string
  description: string
  url: string
  amount?: number
  currency: string
  deadline?: string
  contactEmail?: string
}

// Get backend URL from environment or default to backend service
const BACKEND_URL = process.env.BACKEND_URL || 'http://backend:8000'

export async function POST(request: NextRequest) {
  try {
    // Parse the incoming submission data
    const submissionData: SubmissionData = await request.json()
    
    // Validate required fields
    if (!submissionData.title || !submissionData.organization || !submissionData.description || !submissionData.url) {
      return NextResponse.json(
        { 
          status: 'validation_error',
          message: 'Missing required fields: title, organization, description, and url are required',
          requires_review: false,
          submission_id: '' 
        },
        { status: 400 }
      )
    }
    
    // Forward the submission to our FastAPI backend
    const backendResponse = await fetch(`${BACKEND_URL}/api/v1/submissions/create`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(submissionData)
    })
    
    const result = await backendResponse.json()
    
    if (backendResponse.ok) {
      // Success response from backend
      return NextResponse.json(result)
    } else {
      // Error response from backend
      console.error('Backend submission error:', result)
      return NextResponse.json(
        {
          status: 'error',
          message: result.detail || 'Submission failed. Please try again.',
          requires_review: false,
          submission_id: ''
        },
        { status: backendResponse.status }
      )
    }
    
  } catch (error) {
    console.error('Submission API error:', error)
    
    // Check if it's a network error (backend not available)
    if (error instanceof TypeError && error.message.includes('fetch')) {
      return NextResponse.json(
        {
          status: 'service_unavailable',
          message: 'Submission service is temporarily unavailable. Please try again later.',
          requires_review: false,
          submission_id: ''
        },
        { status: 503 }
      )
    }
    
    // Generic error response
    return NextResponse.json(
      {
        status: 'error',
        message: 'An unexpected error occurred. Please try again.',
        requires_review: false,
        submission_id: ''
      },
      { status: 500 }
    )
  }
}

// Handle unsupported methods
export async function GET() {
  return NextResponse.json(
    { error: 'Method not allowed. Use POST to submit opportunities.' },
    { status: 405 }
  )
}

export async function PUT() {
  return NextResponse.json(
    { error: 'Method not allowed. Use POST to submit opportunities.' },
    { status: 405 }
  )
}

export async function DELETE() {
  return NextResponse.json(
    { error: 'Method not allowed. Use POST to submit opportunities.' },
    { status: 405 }
  )
}