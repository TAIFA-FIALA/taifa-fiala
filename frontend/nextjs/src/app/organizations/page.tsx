"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { Search, Filter, MapPin, Globe, Users, TrendingUp } from 'lucide-react';
import { getApiUrl, API_ENDPOINTS } from '@/lib/api-config';
import { Swiper, SwiperSlide } from 'swiper/react';
import { Navigation, Pagination, Scrollbar, A11y } from 'swiper/modules';

import 'swiper/css';
import 'swiper/css/navigation';
import 'swiper/css/pagination';
import 'swiper/css/scrollbar';

interface Organization {
  id: number;
  name: string;
  description: string;
  website: string;
  email: string;
  country: string;
  region: string;
  funding_capacity: string;
  focus_areas: string;
  established_year: number;
  type: string;
  logo_url?: string;
}

export default function OrganizationsPage() {
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function getOrganizations() {
      try {
        setLoading(true);
        const res = await fetch(getApiUrl(API_ENDPOINTS.organizations));
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        const data = await res.json();
        setOrganizations(data);
      } catch (error) {
        console.error("Failed to fetch organizations:", error);
      } finally {
        setLoading(false);
      }
    }

    getOrganizations();
  }, []);

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-extrabold text-gray-900 mb-6 text-center">Our Valued Partners</h1>
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
        </div>
      ) : organizations.length === 0 ? (
        <p className="text-center text-gray-600">No organizations found.</p>
      ) : (
        <Swiper
          modules={[Navigation, Pagination, Scrollbar, A11y]}
          spaceBetween={30}
          slidesPerView={3}
          navigation
          pagination={{ clickable: true }}
          scrollbar={{ draggable: true }}
          breakpoints={{
            // when window width is >= 640px
            640: {
              slidesPerView: 1,
            },
            // when window width is >= 768px
            768: {
              slidesPerView: 2,
            },
            // when window width is >= 1024px
            1024: {
              slidesPerView: 3,
            },
          }}
          className="mySwiper"
        >
          {organizations.map((org) => (
            <SwiperSlide key={org.id}>
              <div className="flex flex-col items-center justify-between h-full p-6 bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 ease-in-out border border-gray-200">
                <Image src={org.logo_url || 'https://via.placeholder.com/150'} alt={org.name} width={128} height={128} className="object-contain mb-4 rounded-full border-2 border-indigo-500 p-1" />
                <h2 className="text-xl font-bold text-gray-800 text-center mb-2">{org.name}</h2>
                <p className="text-gray-600 text-sm text-center mb-3 line-clamp-4">{org.description}</p>
                <div className="text-gray-700 text-xs text-center mb-4">
                  <p><strong>Type:</strong> {org.type}</p>
                  <p><strong>Country:</strong> {org.country}</p>
                  <p><strong>Region:</strong> {org.region}</p>
                  <p><strong>Funding Capacity:</strong> {org.funding_capacity}</p>
                  <p><strong>Focus Areas:</strong> {org.focus_areas}</p>
                  <p><strong>Established:</strong> {org.established_year}</p>
                  <p><strong>Contact:</strong> {org.email}</p>
                </div>
                <div className="flex flex-col space-y-2 w-full">
                  <a href={org.website} target="_blank" rel="noopener noreferrer" className="w-full text-center bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 transition-colors duration-300 text-sm font-medium">
                    Visit Website
                  </a>
                  <Link href={`/funding?organization_id=${org.id}`} className="w-full text-center bg-gray-200 text-gray-800 py-2 px-4 rounded-md hover:bg-gray-300 transition-colors duration-300 text-sm font-medium">
                    View Opportunities
                  </Link>
                </div>
              </div>
            </SwiperSlide>
          ))}
        </Swiper>
      )}
    </div>
  );
}
