import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { Router } from '@vaadin/router';
import type { Profile } from '@/types/models';
import { profilesApi } from '@services/api/profiles';
import { authService } from '@services/auth-service';

@customElement('profile-header')
export class ProfileHeader extends LitElement {
  @property({ type: Object }) profile!: Profile;
  @property({ type: Boolean }) isOwnProfile = false;

  @state() private isFollowing = false;
  @state() private isLoading = false;

  static styles = css`
    :host {
      display: block;
      background: #f3f3f3;
      padding: 2rem 0;
    }

    .container {
      max-width: 1140px;
      margin: 0 auto;
      padding: 0 15px;
    }

    .profile-info {
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
    }

    .profile-image {
      width: 100px;
      height: 100px;
      border-radius: 50%;
      object-fit: cover;
      margin-bottom: 1rem;
    }

    .username {
      font-size: 1.5rem;
      font-weight: bold;
      color: #373a3c;
      margin: 0 0 0.5rem 0;
    }

    .bio {
      color: #999;
      font-size: 1rem;
      margin: 0 0 1rem 0;
      max-width: 600px;
    }

    .actions {
      display: flex;
      gap: 0.5rem;
      align-items: center;
      justify-content: center;
    }

    .btn {
      padding: 0.5rem 1rem;
      font-size: 0.875rem;
      border-radius: 0.25rem;
      border: 1px solid;
      cursor: pointer;
      transition: all 0.2s;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 0.25rem;
    }

    .btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .btn-outline-secondary {
      background: transparent;
      border-color: #ccc;
      color: #999;
    }

    .btn-outline-secondary:hover:not(:disabled) {
      background: #ccc;
      color: #373a3c;
    }

    .btn-outline-secondary.following {
      background: #ccc;
      color: #373a3c;
    }

    .settings-link {
      background: transparent;
      border-color: #ccc;
      color: #999;
      padding: 0.5rem 1rem;
      font-size: 0.875rem;
      border-radius: 0.25rem;
      border: 1px solid;
      cursor: pointer;
      transition: all 0.2s;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 0.25rem;
    }

    .settings-link:hover {
      background: #ccc;
      color: #373a3c;
    }
  `;

  connectedCallback(): void {
    super.connectedCallback();
    this.isFollowing = this.profile?.following || false;
  }

  willUpdate(changedProperties: Map<string, unknown>): void {
    if (changedProperties.has('profile')) {
      this.isFollowing = this.profile?.following || false;
    }
  }

  private async handleFollowToggle(): Promise<void> {
    if (!authService.isAuthenticated()) {
      Router.go('/login');
      return;
    }

    if (this.isLoading) return;

    this.isLoading = true;
    try {
      const response = this.isFollowing
        ? await profilesApi.unfollowUser(this.profile.username)
        : await profilesApi.followUser(this.profile.username);

      this.profile = response.profile;
      this.isFollowing = response.profile.following;

      // Dispatch event to notify parent components
      this.dispatchEvent(
        new CustomEvent('profile-updated', {
          detail: { profile: this.profile },
          bubbles: true,
          composed: true,
        })
      );
    } catch (error) {
      console.error('Error toggling follow:', error);
    } finally {
      this.isLoading = false;
    }
  }

  private handleSettingsClick(): void {
    Router.go('/settings');
  }

  render() {
    return html`
      <div class="container">
        <div class="profile-info">
          <img
            class="profile-image"
            src=${this.profile?.image || 'https://api.realworld.io/images/smiley-cyrus.jpeg'}
            alt=${this.profile?.username || 'User'}
          />
          <h1 class="username">${this.profile?.username || ''}</h1>
          ${this.profile?.bio ? html`<p class="bio">${this.profile.bio}</p>` : ''}

          <div class="actions">
            ${this.isOwnProfile
              ? html`
                  <button class="settings-link" @click=${this.handleSettingsClick}>
                    <span>⚙️</span>
                    <span>Edit Profile Settings</span>
                  </button>
                `
              : html`
                  <button
                    class="btn btn-outline-secondary ${this.isFollowing ? 'following' : ''}"
                    @click=${this.handleFollowToggle}
                    ?disabled=${this.isLoading}
                  >
                    <span>${this.isFollowing ? '✓' : '+'}</span>
                    <span>${this.isFollowing ? 'Unfollow' : 'Follow'} ${this.profile?.username}</span>
                  </button>
                `}
          </div>
        </div>
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'profile-header': ProfileHeader;
  }
}
