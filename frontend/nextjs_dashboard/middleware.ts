import { NextRequest, NextResponse } from 'next/server'
import { match } from '@formatjs/intl-localematcher'
import Negotiator from 'negotiator'

// List of supported locales
export const locales = ['en', 'fr']
export const defaultLocale = 'en'

// Domain-specific locale mapping
const domainLocaleMap: Record<string, string> = {
  'taifa-africa.com': 'en',
  'fiala-afrique.com': 'fr',
}

// Get the preferred locale from headers and domain
function getLocale(request: NextRequest): string {
  // Check if we should use domain-specific locale
  const host = request.headers.get('host') || ''
  for (const domain in domainLocaleMap) {
    if (host.includes(domain)) {
      return domainLocaleMap[domain]
    }
  }
  
  // Otherwise use headers for locale detection
  const negotiatorHeaders: Record<string, string> = {}
  request.headers.forEach((value, key) => (negotiatorHeaders[key] = value))

  // Use negotiator and intl-localematcher to get the best locale
  const languages = new Negotiator({ headers: negotiatorHeaders }).languages()
  
  // Match locales using the formatjs/intl-localematcher
  try {
    return match(languages, locales, defaultLocale)
  } catch (e) {
    return defaultLocale
  }
}

// Middleware function
export function middleware(request: NextRequest) {
  // Check if there is a preferred locale
  const pathname = request.nextUrl.pathname
  
  // Skip for non-page requests (public files, api, etc.)
  const pathnameIsMissingLocale = locales.every(
    (locale) => !pathname.startsWith(`/${locale}/`) && pathname !== `/${locale}`
  )
  
  // Skip for files and API routes
  if (
    pathname.startsWith('/_next') || 
    pathname.startsWith('/api/') ||
    pathname.includes('.') // files like favicon.ico, etc.
  ) {
    return NextResponse.next()
  }

  // Redirect if there is no locale
  if (pathnameIsMissingLocale) {
    const locale = getLocale(request)
    
    // e.g. incoming request is /funding
    // The new URL is /en/funding or /fr/funding
    return NextResponse.redirect(
      new URL(
        `/${locale}${pathname.startsWith('/') ? '' : '/'}${pathname}`,
        request.url
      )
    )
  }
}

export const config = {
  // Match all request paths except for the ones starting with:
  // - _next/static (static files)
  // - _next/image (image optimization files)
  // - favicon.ico (favicon file)
  // - public (public files)
  matcher: ['/((?!_next/static|_next/image|favicon.ico|public).*)'],
}
