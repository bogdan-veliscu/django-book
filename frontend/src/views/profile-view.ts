import { LitElement, html, css } from 'lit';
import { customElement, state } from 'lit/decorators.js';
import type { Profile } from '@/types/models';
import { profilesApi } from '@services/api/profiles';
import { authService } from '@services/auth-service';
import '../components/profiles/profile-header';
import '../components/profiles/profile-articles';

interface RouterLocation {
  params: {
    username?: string;
  };
}

@customElement('profile-view')
export class ProfileView extends LitElement {
  @state() private profile: Profile | null = null;
  @state() private isLoading = true;
  @state() private error: string | null = null;
  @state() private isOwnProfile = false;

  location?: RouterLocation;

  static styles = css`
    :host {
      display: block;
      min-height: 100vh;
      background: white;
    }

    .loading,
    .error {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 400px;
      font-size: 1.2rem;
      color: #999;
    }

    .error {
      color: #b85c5c;
      flex-direction: column;
      gap: 1rem;
    }

    .retry-btn {
      background: #5cb85c;
      color: white;
      border: none;
      padding: 0.75rem 1.5rem;
      font-size: 1rem;
      border-radius: 0.25rem;
      cursor: pointer;
      transition: background 0.2s;
    }

    .retry-btn:hover {
      background: #449d44;
    }

    profile-articles {
      margin-top: 2rem;
      padding-bottom: 2rem;
    }
  `;

  async connectedCallback(): Promise<void> {
    super.connectedCallback();
    await this.loadProfile();
  }

  private getUsername(): string | null {
    return this.location?.params?.username || null;
  }

  private async loadProfile(): Promise<void> {
    const username = this.getUsername();

    if (!username) {
      this.error = 'No username provided';
      this.isLoading = false;
      return;
    }

    this.isLoading = true;
    this.error = null;

    try {
      const response = await profilesApi.getProfile(username);
      this.profile = response.profile;

      // Check if viewing own profile
      const currentUser = authService.getUser();
      this.isOwnProfile = currentUser?.username === username;
    } catch (error) {
      console.error('Error loading profile:', error);
      this.error = 'Failed to load profile. The user may not exist.';
      this.profile = null;
    } finally {
      this.isLoading = false;
    }
  }

  private handleProfileUpdated(e: CustomEvent): void {
    // Update profile when follow/unfollow happens
    this.profile = e.detail.profile;
  }

  private handleRetry(): void {
    this.loadProfile();
  }

  render() {
    if (this.isLoading) {
      return html`<div class="loading">Loading profile...</div>`;
    }

    if (this.error || !this.profile) {
      return html`
        <div class="error">
          <div>${this.error || 'Profile not found'}</div>
          <button class="retry-btn" @click=${this.handleRetry}>Try Again</button>
        </div>
      `;
    }

    return html`
      <profile-header
        .profile=${this.profile}
        .isOwnProfile=${this.isOwnProfile}
        @profile-updated=${this.handleProfileUpdated}
      ></profile-header>

      <profile-articles .username=${this.profile.username}></profile-articles>
    `;
  }
}
