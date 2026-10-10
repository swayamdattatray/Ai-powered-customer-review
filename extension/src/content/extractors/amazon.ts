/**
 * Amazon.in Resilient Fallback DOM Extractor.
 */

import { ClientReviewItem, ExtractedProductPayload } from '../../types/contracts';

export function extractAmazonProduct(): ExtractedProductPayload | null {
  const url = window.location.href;
  const asinMatch = url.match(/(?:\/dp\/|\/gp\/product\/|\/ASIN\/)([A-Z0-9]{10})/i);
  const sku = asinMatch ? asinMatch[1].toUpperCase() : '';

  if (!sku) {
    return null;
  }

  // 1. Title
  const titleElem = document.getElementById('productTitle') || document.getElementById('title');
  const title = titleElem ? titleElem.textContent?.trim() || '' : '';

  // 2. Price extraction with prioritized buybox selectors
  let price: number | undefined;
  const priceSelectors = [
    '#corePriceDisplay_desktop_feature_div .priceToPay .a-price-whole',
    '#corePriceDisplay_desktop_feature_div .a-price-whole',
    '#corePrice_desktop .priceToPay .a-price-whole',
    '.priceToPay .a-price-whole',
    '.apexPriceToPay .a-price-whole',
    '#priceblock_dealprice',
    '#priceblock_ourprice',
    '#corePrice_feature_div .a-price-whole',
    'span[data-a-color="price"] .a-price-whole',
    '.a-price .a-price-whole'
  ];

  for (const sel of priceSelectors) {
    const elems = document.querySelectorAll(sel);
    for (const el of Array.from(elems)) {
      const raw = el.textContent?.replace(/[^0-9]/g, '') || '';
      if (raw && parseInt(raw, 10) > 0) {
        price = parseInt(raw, 10);
        break;
      }
    }
    if (price) break;
  }

  // Fallback: look for meta tags or offer microdata
  if (!price) {
    const metaPrice = document.querySelector('meta[property="product:price:amount"], meta[name="twitter:data1"]');
    if (metaPrice) {
      const val = metaPrice.getAttribute('content')?.replace(/[^0-9]/g, '');
      if (val && parseInt(val, 10) > 0) price = parseInt(val, 10);
    }
  }

  // 3. Rating & Count
  let rating: number | undefined;
  const popover = document.getElementById('acrPopover');
  if (popover) {
    const titleAttr = popover.getAttribute('title') || '';
    const m = titleAttr.match(/([0-9.]+)\s*out of 5/);
    if (m) rating = parseFloat(m[1]);
  }

  let ratingCount: number | undefined;
  const countElem = document.getElementById('acrCustomerReviewText');
  if (countElem) {
    const m = countElem.textContent?.match(/([0-9,]+)/);
    if (m) ratingCount = parseInt(m[1].replace(/,/g, ''), 10);
  }

  // 4. Seller and Fulfillment Extraction
  let sellerName: string | undefined;
  const sellerElem = document.getElementById('sellerProfileTriggerId') ||
                     document.querySelector('#tabular-buybox .tabular-buybox-text[tabular-attribute-name="Sold by"] a') ||
                     document.querySelector('#merchant-info');
  if (sellerElem) {
    const sText = sellerElem.textContent?.trim() || '';
    const mSold = sText.match(/Sold by\s+([^,.\n]+)/i);
    sellerName = mSold ? mSold[1].trim() : sText.replace(/Sold by/i, '').trim();
    if (sellerName.length > 50) sellerName = sellerName.slice(0, 50);
  }

  const isFulfilled = Boolean(
    document.getElementById('fulfillerInfoFeature_div')?.textContent?.includes('Amazon') ||
    document.getElementById('merchant-info')?.textContent?.includes('Fulfilled by Amazon') ||
    document.querySelector('.tabular-buybox-text[tabular-attribute-name="Ships from"]')?.textContent?.includes('Amazon')
  );

  let returnPolicy: string | undefined;
  const retElem = document.querySelector('#RETURNS_POLICY .icon-box-text, [data-feature-name="returnsPolicy"]');
  if (retElem) {
    returnPolicy = retElem.textContent?.trim();
  }

  // 5. On-page visible customer reviews
  const reviews: ClientReviewItem[] = [];
  const reviewNodes = document.querySelectorAll('[data-hook="review"]');

  for (const node of Array.from(reviewNodes)) {
    // Body text
    const textElem = node.querySelector('[data-hook="reviewText"]') ||
                     node.querySelector('[data-hook="review-body"]') ||
                     node.querySelector('.review-text-content');
    let text = textElem ? textElem.textContent?.trim() || '' : '';
    // Clean accessibility noise
    text = text.replace(/Brief content visible, double tap to read full content\./gi, '')
               .replace(/Full content visible, double tap to read brief content\./gi, '')
               .replace(/Read more\s*Read less/gi, '')
               .trim();

    if (text.length < 10) continue;

    // Title
    const titleElem = node.querySelector('[data-hook="reviewTitle"]') ||
                      node.querySelector('[data-hook="review-title"]');
    const rTitle = titleElem ? titleElem.textContent?.trim() || '' : '';

    // Star rating
    let rRating: number | undefined;
    const starElem = node.querySelector('[data-hook="review-star-rating"]') ||
                     node.querySelector('.a-icon-alt');
    if (starElem) {
      const sm = starElem.textContent?.match(/([0-9.]+)/);
      if (sm) rRating = parseFloat(sm[1]);
    }

    // Verified
    const verified = Boolean(
      node.querySelector('[data-hook="avp-badge"]') ||
      node.textContent?.includes('Verified Purchase')
    );

    reviews.push({
      text,
      title: rTitle,
      rating: rRating,
      verified_purchase: verified
    });
  }

  return {
    url,
    platform: 'AMAZON_IN',
    sku,
    title,
    listed_price: price,
    currency: 'INR',
    rating,
    rating_count: ratingCount,
    availability: !document.body.innerText.includes('Currently unavailable'),
    seller_name: sellerName,
    is_fulfilled_by_platform: isFulfilled,
    return_policy: returnPolicy,
    attributes: {},
    reviews
  };
}
