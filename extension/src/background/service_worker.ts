/**
 * Chrome Manifest V3 Extension Service Worker.
 * Manages side panel routing, tab session state, and messaging relays.
 */

// Enable Side Panel on action click
chrome.sidePanel
  .setPanelBehavior({ openPanelOnActionClick: true })
  .catch((error) => console.error('Failed to set side panel behavior:', error));

// Tab-isolated payload cache
const tabPayloadCache = new Map<number, any>();

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  const tabId = sender.tab?.id;

  if (message.type === 'OPEN_SIDE_PANEL_REQUEST') {
    if (tabId) {
      chrome.sidePanel.open({ tabId }).catch(() => {});
    }
    sendResponse({ opened: true });
    return true;
  }

  if (message.type === 'OPEN_DASHBOARD_REQUEST') {
    const payload = message.payload || (tabId ? tabPayloadCache.get(tabId) : null);
    const platform = payload?.platform || 'UNKNOWN';
    const sku = payload?.sku || 'UNKNOWN';
    const canonicalId = `${platform}_${sku}`.toLowerCase();

    // Deterministic state handoff: persist in chrome.storage.local before spawning tab
    if (payload) {
      chrome.storage.local.set({
        [`product_${canonicalId}`]: payload,
        latest_dashboard_product: payload
      }, () => {
        const dashboardUrl = chrome.runtime.getURL(
          `src/dashboard/index.html?id=${encodeURIComponent(canonicalId)}&platform=${encodeURIComponent(platform)}&sku=${encodeURIComponent(sku)}`
        );
        chrome.tabs.create({ url: dashboardUrl });
      });
    } else {
      const dashboardUrl = chrome.runtime.getURL('src/dashboard/index.html');
      chrome.tabs.create({ url: dashboardUrl });
    }
    sendResponse({ opened: true });
    return true;
  }

  if (message.type === 'PRODUCT_DETECTED') {
    if (tabId) {
      tabPayloadCache.set(tabId, message.payload);

      // Set contextual badge indicating shopping intelligence is available
      chrome.action.setBadgeText({ tabId, text: '✓' });
      chrome.action.setBadgeBackgroundColor({ tabId, color: '#2563eb' });
    }

    // Forward to any open Side Panel
    chrome.runtime.sendMessage({
      type: 'BROADCAST_PRODUCT_UPDATE',
      payload: message.payload,
      tabId
    }).catch(() => {
      // Side panel might not be active
    });

    sendResponse({ received: true });
    return true;
  }

  if (message.type === 'GET_ACTIVE_TAB_PRODUCT') {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const activeTabId = tabs[0]?.id;
      if (activeTabId && tabPayloadCache.has(activeTabId)) {
        sendResponse({ payload: tabPayloadCache.get(activeTabId) });
      } else {
        // Query content script directly
        if (activeTabId) {
          chrome.tabs.sendMessage(activeTabId, { type: 'GET_CURRENT_PAGE_PRODUCT' }, (res) => {
            sendResponse({ payload: res?.payload || null });
          });
        } else {
          sendResponse({ payload: null });
        }
      }
    });
    return true;
  }
});

// Clear cache when tab is closed
chrome.tabs.onRemoved.addListener((tabId) => {
  tabPayloadCache.delete(tabId);
});
