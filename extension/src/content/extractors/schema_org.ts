/**
 * Schema.org JSON-LD Microdata Extractor.
 * Extracts standardized product structured data directly from the document.
 */

import { ClientReviewItem } from '../../types/contracts';

export interface SchemaOrgResult {
  title?: string;
  brand?: string;
  price?: number;
  currency?: string;
  rating?: number;
  ratingCount?: number;
  sku?: string;
  reviews: ClientReviewItem[];
}

export function extractSchemaOrgMicrodata(): SchemaOrgResult {
  const result: SchemaOrgResult = {
    currency: 'INR',
    reviews: []
  };

  const scripts = document.querySelectorAll('script[type="application/ld+json"]');

  for (const script of Array.from(scripts)) {
    try {
      const data = JSON.parse(script.textContent || '{}');
      const items = Array.isArray(data) ? data : (data['@graph'] ? data['@graph'] : [data]);

      for (const item of items) {
        if (item['@type'] === 'Product' || (Array.isArray(item['@type']) && item['@type'].includes('Product'))) {
          if (item.name) result.title = String(item.name).trim();
          if (item.brand?.name) result.brand = String(item.brand.name).trim();
          if (item.sku) result.sku = String(item.sku).trim();

          // Offers
          const offers = Array.isArray(item.offers) ? item.offers[0] : item.offers;
          if (offers) {
            const rawPrice = offers.price || offers.lowPrice;
            if (rawPrice) {
              const parsed = parseFloat(String(rawPrice).replace(/[^0-9.]/g, ''));
              if (!isNaN(parsed)) result.price = parsed;
            }
            if (offers.priceCurrency) result.currency = offers.priceCurrency;
          }

          // Aggregate Rating
          if (item.aggregateRating) {
            const rVal = parseFloat(item.aggregateRating.ratingValue);
            if (!isNaN(rVal)) result.rating = rVal;
            const rCount = parseInt(item.aggregateRating.ratingCount || item.aggregateRating.reviewCount, 10);
            if (!isNaN(rCount)) result.ratingCount = rCount;
          }

          // Embedded Reviews
          if (Array.isArray(item.review)) {
            for (const r of item.review) {
              const body = r.reviewBody || r.description;
              if (body && String(body).trim().length > 10) {
                result.reviews.push({
                  author: r.author?.name || 'Customer',
                  rating: r.reviewRating?.ratingValue ? parseFloat(r.reviewRating.ratingValue) : undefined,
                  title: r.headline || '',
                  text: String(body).trim(),
                  date: r.datePublished || '',
                  verified_purchase: true
                });
              }
            }
          }
        }
      }
    } catch {
      // Continue to next script tag
    }
  }

  return result;
}
