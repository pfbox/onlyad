export interface Ad {
  id: string;
  title: string;
  brand: string;
  description: string | null;
  media_url: string;
  media_type: 'video' | 'image';
  category: string;
  tags: string | null;
  upvotes: number;
  downvotes: number;
  views_count: number;
  score: number;
  created_at: string;
}

export interface AdFeedItem {
  id: string;
  title: string;
  brand: string;
  description: string | null;
  media_url: string;
  media_type: 'video' | 'image';
  category: string;
  tags: string | null;
  upvotes: number;
  downvotes: number;
  score: number;
  user_vote: number | null;
}

export interface User {
  id: string;
  email: string;
  name: string;
  avatar: string | null;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface VoteResponse {
  id: string;
  user_id: string;
  ad_id: string;
  vote: number;
  created_at: string;
}