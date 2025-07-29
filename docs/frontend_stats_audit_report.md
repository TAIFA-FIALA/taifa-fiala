# Frontend Statistics Audit Report

## 1. Executive Summary

This report provides a comprehensive audit of the statistical data displayed on the frontend of the application. The audit reveals that **all statistical values, including those in cards and graphs, are currently placeholders or generated from mock data hardcoded in the frontend components.**

While many components are designed to fetch data from a backend API, they all contain hardcoded fallback data that is used if the API calls fail or are not implemented. This means the frontend is currently operating with placeholder data and is not connected to a live backend data source for its statistical reporting.

## 2. Homepage (`app/page.tsx`)

The main homepage displays several key metrics and a longitudinal graph of database records over time.

*   **Static Cards:** The four main static cards ("Total Opportunities," "Active Opportunities," "Total Funding Tracked," and "Organizations") are populated by the `getAnalyticsSummary` function. This function attempts to fetch data from the `/api/v1/analytics/summary` endpoint. If the fetch fails, it returns a hardcoded object with demo data.
*   **Longitudinal Graph:** The "Live Intelligence Collection - Database Growth" graph is rendered by the `DatabaseGrowthChart` component. This component uses a `generateMockData` function to create sample data for the chart. The code explicitly states that this is for demonstration purposes and should be replaced with an actual API call.

## 3. Analytics Pages (`app/analytics/`)

The analytics section contains multiple pages with detailed statistical information. All of this information is currently hardcoded.

*   **Main Analytics Dashboard (`app/analytics/page.tsx`):** The main dashboard uses a `getAnalyticsData` function that returns a hardcoded object with sample data.
*   **Sub-pages:** The sub-pages, including `funding-lifecycle/page.tsx`, `gender-inclusion/page.tsx`, and `geographic-equity/page.tsx`, all contain numerous hardcoded statistics directly in the JSX.

## 4. Funding Landscape (`app/funding-landscape/page.tsx`)

This page is the most significant source of hardcoded data. It contains multiple data arrays for charts and metrics, including:

*   `fundingByCountryData`
*   `sectorDistributionData`
*   `fundingTimelineData`
*   `regionalGapsData`
*   `keyMetrics`
*   `topCountries`
*   `sectorData`

All of these are populated with hardcoded sample data.

## 5. Reusable Components

Many of the charts and statistical displays are encapsulated in reusable components. The audit of these components reveals the same pattern of using hardcoded or mock data.

*   **`components/analytics/`**: The components in this directory (`GeographicAnalysis.tsx`, `NetworkAnalysis.tsx`, `TemporalAnalysis.tsx`) all use hardcoded data.
*   **`components/equity-focus/`**: The components in this directory (`FundingLifecycleSupport.tsx`, `GenderInclusionDashboard.tsx`, `GeographicEquityMap.tsx`, `SectoralAlignmentDashboard.tsx`) are all designed to fetch data from a backend API but contain extensive hardcoded fallback data that is used if the API calls fail.
*   **`components/homepage/`**: The components in this directory, including `DatabaseGrowthChart.tsx`, `GeographicDistributionMapWrapper.tsx`, `SectorAllocationChart.tsx`, and `GenderEquityDashboard.tsx`, all use hardcoded or mock data.

## 6. Data Files

The only data file referenced, `frontend/nextjs/src/data/african_countries_geo.json`, contains geographic data for rendering maps and does not contain any statistical data.

## 7. Conclusion

The frontend of the application is currently a high-fidelity prototype with a rich display of statistical information. However, none of this information is sourced from a live backend API. All data is either hardcoded directly in the components or generated as mock data for demonstration purposes. To make the application functional, all API calls need to be implemented and connected to a live backend, and the fallback mock data should be removed or used only for development and testing.