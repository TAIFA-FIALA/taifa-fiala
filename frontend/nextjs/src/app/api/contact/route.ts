import { NextRequest, NextResponse } from 'next/server'
import nodemailer from 'nodemailer'

interface ContactFormData {
  name: string
  email: string
  subject: string
  message: string
  inquiryType: 'general' | 'partnership' | 'data' | 'funding' | 'other'
}

export async function POST(request: NextRequest) {
  try {
    const formData: ContactFormData = await request.json()
    
    // Validate required fields
    if (!formData.name || !formData.email || !formData.subject || !formData.message) {
      return NextResponse.json(
        { 
          success: false,
          message: 'All fields are required'
        },
        { status: 400 }
      )
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(formData.email)) {
      return NextResponse.json(
        { 
          success: false,
          message: 'Please provide a valid email address'
        },
        { status: 400 }
      )
    }

    // Create email transporter (using Gmail SMTP as a reliable option)
    // In production, you would use environment variables for these credentials
    const transporter = nodemailer.createTransport({
      service: 'gmail',
      auth: {
        user: process.env.SMTP_USER || 'your-email@gmail.com',
        pass: process.env.SMTP_PASSWORD || 'your-app-password'
      }
    })

    // Email content
    const mailOptions = {
      from: process.env.SMTP_USER || 'noreply@taifa-fiala.org',
      to: 'drjforrest@outlook.com',
      subject: `TAIFA-FIALA Contact Form: ${formData.subject}`,
      html: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <div style="background: linear-gradient(135deg, #3E4B59 0%, #F0A621 100%); padding: 20px; text-align: center;">
            <h1 style="color: white; margin: 0;">TAIFA-FIALA Contact Form</h1>
          </div>
          
          <div style="padding: 30px; background: #f8f9fa;">
            <h2 style="color: #3E4B59; margin-bottom: 20px;">New Contact Form Submission</h2>
            
            <div style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #F0A621;">
              <h3 style="color: #3E4B59; margin-top: 0;">Contact Information</h3>
              <p><strong>Name:</strong> ${formData.name}</p>
              <p><strong>Email:</strong> ${formData.email}</p>
              <p><strong>Inquiry Type:</strong> ${formData.inquiryType}</p>
            </div>
            
            <div style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #007A56;">
              <h3 style="color: #3E4B59; margin-top: 0;">Subject</h3>
              <p>${formData.subject}</p>
            </div>
            
            <div style="background: white; padding: 20px; border-radius: 8px; border-left: 4px solid #3E4B59;">
              <h3 style="color: #3E4B59; margin-top: 0;">Message</h3>
              <p style="white-space: pre-wrap;">${formData.message}</p>
            </div>
          </div>
          
          <div style="background: #3E4B59; padding: 15px; text-align: center;">
            <p style="color: white; margin: 0; font-size: 12px;">
              This message was sent via the TAIFA-FIALA contact form at ${new Date().toLocaleString()}
            </p>
          </div>
        </div>
      `,
      replyTo: formData.email
    }

    // Send email
    await transporter.sendMail(mailOptions)

    return NextResponse.json({
      success: true,
      message: 'Thank you for your message! We will get back to you soon.'
    })

  } catch (error) {
    console.error('Contact form error:', error)
    
    return NextResponse.json(
      {
        success: false,
        message: 'Failed to send message. Please try again later or contact us directly at drjforrest@outlook.com'
      },
      { status: 500 }
    )
  }
}

// Handle unsupported methods
export async function GET() {
  return NextResponse.json(
    { error: 'Method not allowed. Use POST to send contact messages.' },
    { status: 405 }
  )
}

export async function PUT() {
  return NextResponse.json(
    { error: 'Method not allowed. Use POST to send contact messages.' },
    { status: 405 }
  )
}

export async function DELETE() {
  return NextResponse.json(
    { error: 'Method not allowed. Use POST to send contact messages.' },
    { status: 405 }
  )
}
