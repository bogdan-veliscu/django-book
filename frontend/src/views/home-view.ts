import { LitElement, html, css } from 'lit';
import { customElement } from 'lit/decorators.js';

@customElement('home-view')
export class HomeView extends LitElement {
  static styles = css`
    :host {
      display: block;
    }

    .banner {
      background: #5cb85c;
      color: white;
      padding: 2rem;
      text-align: center;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
    }

    h1 {
      font-size: 3.5rem;
      font-family: 'Titillium Web', serif;
      margin: 0 0 0.5rem 0;
      font-weight: 700;
    }

    p {
      font-size: 1.5rem;
      margin: 0;
    }

    .container {
      max-width: 1140px;
      margin: 2rem auto;
      padding: 0 1rem;
    }

    .message {
      text-align: center;
      padding: 2rem;
    }
  `;

  render() {
    return html`
      <div class="banner">
        <div class="container">
          <h1>conduit</h1>
          <p>A place to share your knowledge.</p>
        </div>
      </div>

      <div class="container">
        <div class="message">
          <h2>Welcome to Conduit</h2>
          <p>Frontend is loading... Articles will appear here soon!</p>
        </div>
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'home-view': HomeView;
  }
}
