/**
 * In-Page Sensory Content Script.
 * Dispatches detected product payload to Extension Service Worker and Side Panel.
 */

import { extractSchemaOrgMicrodata } from './extractors/schema_org';
import { extractAmazonProduct } from './extractors/amazon';
import { extractFlipkartProduct } from './extractors/flipkart';
import { ExtractedProductPayload } from '../types/contracts';

let cachedPayload: ExtractedProductPayload | null = null;

function scanPage(): ExtractedProductPayload | null {
  const host = window.location.hostname.toLowerCase();
  let payload: ExtractedProductPayload | null = null;

  if (host.includes('amazon.')) {
    payload = extractAmazonProduct();
  } else if (host.includes('flipkart.')) {
    payload = extractFlipkartProduct();
  }

  if (!payload) {
    return null;
  }

  // Enrich with Schema.org JSON-LD microdata if available
  const microdata = extractSchemaOrgMicrodata();
  if (microdata.title && !payload.title) {
    payload.title = microdata.title;
  }
  if (microdata.brand && !payload.brand) {
    payload.brand = microdata.brand;
  }
  if (microdata.price && !payload.listed_price) {
    payload.listed_price = microdata.price;
  }
  if (microdata.reviews && microdata.reviews.length > payload.reviews.length) {
    payload.reviews = microdata.reviews;
  }

  cachedPayload = payload;
  injectFloatingBadge(payload);
  return payload;
}

function injectFloatingBadge(payload: ExtractedProductPayload) {
  if (document.getElementById('ai-shopping-intelligence-badge')) return;

  const badge = document.createElement('div');
  badge.id = 'ai-shopping-intelligence-badge';
  badge.style.cssText = `
    position: fixed;
    bottom: 24px;
    right: 24px;
    z-index: 999999;
    background: #ffffff;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
    border-radius: 9999px;
    padding: 8px 14px;
    display: flex;
    align-items: center;
    gap: 8px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease-in-out;
    user-select: none;
  `;

  const priceText = payload.listed_price ? `₹${payload.listed_price.toLocaleString('en-IN')}` : 'Detected';

  badge.innerHTML = `
    <div style="width: 22px; height: 22px; background: #2563eb; color: #ffffff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 900;">AI</div>
    <span>Shopping Intelligence: <strong style="color: #2563eb;">${priceText}</strong></span>
    <span style="background: #eff6ff; color: #1d4ed8; font-size: 10px; padding: 2px 7px; border-radius: 4px; border: 1px solid #bfdbfe; font-weight: 700;">Deep Dashboard ↗</span>
    <button id="ai-badge-close" style="background: transparent; border: none; color: #94a3b8; font-size: 14px; cursor: pointer; padding: 0 2px; margin-left: 2px;" title="Dismiss">✕</button>
  `;

  badge.addEventListener('mouseenter', () => {
    badge.style.transform = 'translateY(-2px)';
  });
  badge.addEventListener('mouseleave', () => {
    badge.style.transform = 'translateY(0)';
  });

  badge.addEventListener('click', (e) => {
    if ((e.target as HTMLElement).id === 'ai-badge-close') {
      badge.remove();
      return;
    }
    chrome.runtime.sendMessage({
      type: 'OPEN_DASHBOARD_REQUEST',
      payload
    });
  });

  document.body.appendChild(badge);
}

function notifyBackground() {
  const payload = scanPage();
  if (payload) {
    chrome.runtime.sendMessage({
      type: 'PRODUCT_DETECTED',
      payload
    }).catch(() => {
      // Background receiver may be inactive or side panel not open yet
    });
  }
}

// 1. Initial scan on document ready
if (document.readyState === 'complete' || document.readyState === 'interactive') {
  notifyBackground();
} else {
  window.addEventListener('DOMContentLoaded', notifyBackground);
}

// 2. Handle dynamic Single Page App (SPA) navigations (common on Flipkart)
let lastUrl = location.href;
new MutationObserver(() => {
  const url = location.href;
  if (url !== lastUrl) {
    lastUrl = url;
    setTimeout(notifyBackground, 1200);
  }
}).observe(document, { subtree: true, childList: true });

// 3. Listen for pull requests from Side Panel
chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message.type === 'GET_CURRENT_PAGE_PRODUCT') {
    const payload = cachedPayload || scanPage();
    sendResponse({ payload });
  }
  return true;
});
