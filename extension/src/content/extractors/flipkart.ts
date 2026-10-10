/**
 * Flipkart.com Resilient Fallback DOM Extractor.
 */

import { ClientReviewItem, ExtractedProductPayload } from '../../types/contracts';

export function extractFlipkartProduct(): ExtractedProductPayload | null {
  const url = window.location.href;
  const pidMatch = url.match(/(?:pid=|\/p\/)([a-zA-Z0-9]+)/i);
  const sku = pidMatch ? pidMatch[1].toUpperCase() : '';

  if (!sku) {
    return null;
  }

  // 1. Title
  const titleElem = document.querySelector('span.B_NuCI') ||
                    document.querySelector('h1.yhB1nd') ||
                    document.querySelector('h1');
  const title = titleElem ? titleElem.textContent?.trim() || '' : '';

  // 2. Price
  let price: number | undefined;
  const priceElem = document.querySelector('div._30jeq3._16Jk6d') ||
                    document.querySelector('div.Nx9bqj.CxhGGd') ||
                    document.querySelector('div._30jeq3');
  if (priceElem) {
    const raw = priceElem.textContent?.replace(/[^0-9]/g, '') || '';
    if (raw) price = parseInt(raw, 10);
  }

  // 3. Rating & Count
  let rating: number | undefined;
  const ratingElem = document.querySelector('div._3LWZlK') ||
                     document.querySelector('div.XQDdHH');
  if (ratingElem) {
    const m = ratingElem.textContent?.match(/([0-9.]+)/);
    if (m) rating = parseFloat(m[1]);
  }

  let ratingCount: number | undefined;
  const countElem = document.querySelector('span._2_R_DZ') ||
                    document.querySelector('span.Wphh3N');
  if (countElem) {
    const m = countElem.textContent?.match(/([0-9,]+)\s*(?:Ratings|Reviews)/i);
    if (m) ratingCount = parseInt(m[1].replace(/,/g, ''), 10);
  }

  // 4. Seller and Fulfillment Extraction
  let sellerName: string | undefined;
  const sellerElem = document.getElementById('sellerName') ||
                     document.querySelector('div._1RLviY') ||
                     document.querySelector('div.G6XhRU');
  if (sellerElem) {
    sellerName = sellerElem.textContent?.replace(/[0-9.]+\s*★/g, '').trim();
    if (sellerName && sellerName.length > 50) sellerName = sellerName.slice(0, 50);
  }

  const isFulfilled = Boolean(
    document.querySelector('img[src*="fa_"]') ||
    document.querySelector('img[src*="flipkart-plus"]') ||
    document.querySelector('div._1pL-8T')
  );

  let returnPolicy: string | undefined;
  const retElem = document.querySelector('li._3L5H3s, div._3XINqZ, div._2tw8q-');
  if (retElem && (retElem.textContent?.includes('Return') || retElem.textContent?.includes('Replacement'))) {
    returnPolicy = retElem.textContent?.trim();
  }

  // 5. On-page visible customer reviews
  const reviews: ClientReviewItem[] = [];
  const reviewCards = document.querySelectorAll('div.col.EPCmJX, div._1AtVbE div._2w1YVo, div.RCXBOT');

  for (const card of Array.from(reviewCards)) {
    const textElem = card.querySelector('div.t-ZTKy') ||
                     card.querySelector('div.ZmyHeo') ||
                     card.querySelector('div._6K-7Co');
    const text = textElem ? textElem.textContent?.replace(/READ MORE/gi, '').trim() || '' : '';
    if (text.length < 10) continue;

    const titleElem = card.querySelector('p._2-N8zT') || card.querySelector('p.z9E0IG');
    const rTitle = titleElem ? titleElem.textContent?.trim() || '' : '';

    let rRating: number | undefined;
    const starElem = card.querySelector('div._3LWZlK') || card.querySelector('div.XQDdHH');
    if (starElem) {
      const sm = starElem.textContent?.match(/([0-9.]+)/);
      if (sm) rRating = parseFloat(sm[1]);
    }

    reviews.push({
      text,
      title: rTitle,
      rating: rRating,
      verified_purchase: true
    });
  }

  return {
    url,
    platform: 'FLIPKART',
    sku,
    title,
    listed_price: price,
    currency: 'INR',
    rating,
    rating_count: ratingCount,
    availability: !document.body.innerText.includes('Sold Out') && !document.body.innerText.includes('Currently Unavailable'),
    seller_name: sellerName,
    is_fulfilled_by_platform: isFulfilled,
    return_policy: returnPolicy,
    attributes: {},
    reviews
  };
}
