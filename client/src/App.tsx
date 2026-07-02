import { useState } from 'react';
import SwipeFeed from './components/SwipeFeed';
import SearchPage from './components/SearchPage';
import UploadPage from './components/UploadPage';
import AuthModal from './components/AuthModal';
import { useAuth } from './hooks/useAuth';

type Tab = 'feed' | 'search' | 'upload' | 'profile';

export default function App() {
  const { user, loading, login, register, logout } = useAuth();
  const [activeTab, setActiveTab] = useState<Tab>('feed');
  const [showAuth, setShowAuth] = useState(false);

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center bg-dark">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-dark relative">
      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'feed' && <SwipeFeed isAuthenticated={!!user} />}
        {activeTab === 'search' && <SearchPage />}
        {activeTab === 'upload' && <UploadPage />}
        {activeTab === 'profile' && (
          <div className="h-full overflow-y-auto p-4 pt-12">
            <div className="max-w-lg mx-auto">
              <h1 className="text-2xl font-bold mb-6">Profile</h1>
              {user ? (
                <div className="space-y-4">
                  <div className="bg-surface rounded-xl p-6 text-center">
                    <div className="w-20 h-20 rounded-full bg-primary flex items-center justify-center text-3xl mx-auto mb-4">
                      {user.name.charAt(0).toUpperCase()}
                    </div>
                    <h2 className="text-xl font-semibold">{user.name}</h2>
                    <p className="text-gray-400">{user.email}</p>
                  </div>
                  <button
                    onClick={logout}
                    className="w-full py-3 bg-red-500/20 text-red-400 rounded-full font-semibold hover:bg-red-500/30 transition-colors"
                  >
                    Sign Out
                  </button>
                </div>
              ) : (
                <div className="text-center py-12">
                  <p className="text-gray-400 mb-4">Sign in to save your votes and preferences</p>
                  <button
                    onClick={() => setShowAuth(true)}
                    className="px-8 py-3 bg-primary text-white rounded-full font-semibold"
                  >
                    Sign In / Sign Up
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Bottom Navigation */}
      <nav className="flex-shrink-0 bg-surface border-t border-gray-800 safe-area-bottom">
        <div className="flex items-center justify-around py-2 max-w-md mx-auto">
          <TabButton
            icon="🏠"
            label="Feed"
            active={activeTab === 'feed'}
            onClick={() => setActiveTab('feed')}
          />
          <TabButton
            icon="🔍"
            label="Search"
            active={activeTab === 'search'}
            onClick={() => setActiveTab('search')}
          />
          <TabButton
            icon="📤"
            label="Upload"
            active={activeTab === 'upload'}
            onClick={() => setActiveTab('upload')}
          />
          <TabButton
            icon={user ? '👤' : '🔑'}
            label={user ? 'Profile' : 'Sign In'}
            active={activeTab === 'profile'}
            onClick={() => {
              if (!user && activeTab !== 'profile') {
                setShowAuth(true);
                return;
              }
              setActiveTab('profile');
            }}
          />
        </div>
      </nav>

      {/* Auth Modal */}
      {showAuth && (
        <AuthModal
          onClose={() => setShowAuth(false)}
          onLogin={login}
          onRegister={register}
        />
      )}
    </div>
  );
}

function TabButton({
  icon,
  label,
  active,
  onClick,
}: {
  icon: string;
  label: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex flex-col items-center gap-1 px-4 py-1 transition-colors ${
        active ? 'text-primary' : 'text-gray-500'
      }`}
    >
      <span className="text-xl">{icon}</span>
      <span className="text-xs font-medium">{label}</span>
    </button>
  );
}