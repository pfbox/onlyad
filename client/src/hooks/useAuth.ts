import { useState, useCallback, useEffect } from 'react';
import { setAuthToken, getAuthToken } from '../api/client';
import { getMe, login as apiLogin, register as apiRegister } from '../api/endpoints';
import type { User } from '../api/types';

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getAuthToken();
    if (token) {
      getMe()
        .then(setUser)
        .catch(() => {
          setAuthToken(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const res = await apiLogin(email, password);
    setAuthToken(res.access_token);
    setUser(res.user);
    return res.user;
  }, []);

  const register = useCallback(async (email: string, name: string, password: string) => {
    const res = await apiRegister(email, name, password);
    setAuthToken(res.access_token);
    setUser(res.user);
    return res.user;
  }, []);

  const logout = useCallback(() => {
    setAuthToken(null);
    setUser(null);
  }, []);

  return { user, loading, login, register, logout };
}