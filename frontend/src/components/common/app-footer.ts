import { LitElement, html, css } from 'lit';
import { customElement } from 'lit/decorators.js';

@customElement('app-footer')
export class AppFooter extends LitElement {
  static styles = css`
    :host {
      display: block;
      margin-top: auto;
    }

    footer {
      background: #f3f3f3;
      padding: 1.5rem 0;
      margin-top: 3rem;
    }

    .container {
      max-width: 1140px;
      margin: 0 auto;
      padding: 0 1rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 1rem;
    }

    .brand {
      color: #5cb85c;
      text-decoration: none;
      font-weight: bold;
      font-size: 1.25rem;
      font-family: 'Titillium Web', serif;
      transition: color 0.2s;
    }

    .brand:hover {
      color: #449d44;
    }

    .attribution {
      color: #999;
      font-size: 0.875rem;
    }

    .attribution a {
      color: #5cb85c;
      text-decoration: none;
      transition: color 0.2s;
    }

    .attribution a:hover {
      color: #449d44;
      text-decoration: underline;
    }

    .footer-links {
      display: flex;
      gap: 1.5rem;
      list-style: none;
      margin: 0;
      padding: 0;
    }

    .footer-link {
      color: #999;
      text-decoration: none;
      font-size: 0.875rem;
      transition: color 0.2s;
    }

    .footer-link:hover {
      color: #5cb85c;
      text-decoration: underline;
    }

    @media (max-width: 768px) {
      .container {
        flex-direction: column;
        text-align: center;
      }

      .footer-links {
        justify-content: center;
      }
    }
  `;

  render() {
    return html`
      <footer>
        <div class="container">
          <a href="/" class="brand">conduit</a>
          <p class="attribution">
            An interactive learning project from
            <a
              href="https://thinkster.io"
              target="_blank"
              rel="noopener noreferrer"
            >
              Thinkster
            </a>
            . Code &amp; design licensed under MIT.
          </p>
          <ul class="footer-links">
            <li>
              <a href="/" class="footer-link">Home</a>
            </li>
            <li>
              <a
                href="https://github.com/gothinkster/realworld"
                target="_blank"
                rel="noopener noreferrer"
                class="footer-link"
              >
                GitHub
              </a>
            </li>
          </ul>
        </div>
      </footer>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'app-footer': AppFooter;
  }
}
