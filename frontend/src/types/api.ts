import type { User, Profile, Article, Comment } from './models';

export interface ApiError {
  errors: {
    [key: string]: string[];
  };
}

export interface UserResponse {
  user: User;
}

export interface ProfileResponse {
  profile: Profile;
}

export interface ArticleResponse {
  article: Article;
}

export interface MultipleArticlesResponse {
  articles: Article[];
  articlesCount: number;
}

export interface CommentResponse {
  comment: Comment;
}

export interface MultipleCommentsResponse {
  comments: Comment[];
}

export interface TagsResponse {
  tags: string[];
}

export interface ApiRequestOptions extends RequestInit {
  token?: string;
}
