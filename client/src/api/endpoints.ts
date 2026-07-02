import { apiRequest, apiUpload } from './client';
import type { Ad, AdFeedItem, AuthResponse, User, VoteResponse } from './types';

// Auth
export async function register(email: string, name: string, password: string): Promise<AuthResponse> {
  return apiRequest<AuthResponse>('/auth/register', {
    method: 'POST',
    body: { email, name, password },
  });
}

export async function login(email: string, password: string): Promise<AuthResponse> {
  return apiRequest<AuthResponse>('/auth/login', {
    method: 'POST',
    body: { email, password },
  });
}

export async function getMe(): Promise<User> {
  return apiRequest<User>('/auth/me');
}

// Ads
export async function getFeed(limit = 20, exclude = ''): Promise<AdFeedItem[]> {
  const params = new URLSearchParams({ limit: String(limit) });
  if (exclude) params.set('exclude', exclude);
  return apiRequest<AdFeedItem[]>(`/ads/feed?${params}`);
}

export async function searchAds(q = '', tag = '', category = '', limit = 20): Promise<Ad[]> {
  const params = new URLSearchParams({ limit: String(limit) });
  if (q) params.set('q', q);
  if (tag) params.set('tag', tag);
  if (category) params.set('category', category);
  return apiRequest<Ad[]>(`/ads/search?${params}`);
}

export async function getAd(adId: string): Promise<Ad> {
  return apiRequest<Ad>(`/ads/${adId}`);
}

export async function uploadAd(formData: FormData): Promise<Ad> {
  return apiUpload<Ad>('/ads/upload', formData);
}

// Votes
export async function castVote(adId: string, vote: number): Promise<VoteResponse> {
  return apiRequest<VoteResponse>('/votes/', {
    method: 'POST',
    body: { ad_id: adId, vote },
  });
}

export async function getVoteHistory(): Promise<VoteResponse[]> {
  return apiRequest<VoteResponse[]>('/votes/history');
}