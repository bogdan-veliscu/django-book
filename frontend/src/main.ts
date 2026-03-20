import { html, render } from 'lit';
import './app';

// Render the app
const app = html`<app-root></app-root>`;
render(app, document.getElementById('app')!);

// Register service worker for PWA
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch((error) => {
      console.error('Service worker registration failed:', error);
    });
  });
}
