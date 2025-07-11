import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Link from "next/link";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AI Africa Funding Tracker",
  description: "Comprehensive platform to track AI funding opportunities in Africa",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <nav className="bg-gray-800 p-4">
          <div className="container mx-auto flex justify-between items-center">
            <Link href="/" className="text-white text-lg font-bold">
              AI Africa Funding Tracker
            </Link>
            <div className="space-x-4">
              <Link href="/funding" className="text-gray-300 hover:text-white">
                Funding Opportunities
              </Link>
              <Link href="/organizations" className="text-gray-300 hover:text-white">
                Our Partners
              </Link>
              <Link href="/submit-rfp" className="text-gray-300 hover:text-white">
                Submit RFP
              </Link>
            </div>
          </div>
        </nav>
        {children}
      </body>
    </html>
  );
}
