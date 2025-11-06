import React, { useState } from "react";

// Import Twitter Agent Components
import AgentDashboard from "./components/twitter/AgentDashboard";
import ManagerDashboard from "./components/twitter/ManagerDashboard";
import DirectorDashboard from "./components/twitter/DirectorDashboard";
import TwitterConversation from "./components/twitter/TwitterConversation";
import TwitterAnalytics from "./components/twitter/TwitterAnalytics";
import TwitterSettings from "./components/twitter/TwitterSettings";
import TwitterBackofficeSettings from "./components/twitter/TwitterBackofficeSettings";

type TwitterView = "dashboard" | "conversation" | "analytics" | "settings" | "backoffice";
type UserRole = "agent" | "manager" | "director";

interface Tweet {
  id: string;
  author: string;
  handle: string;
  content: string;
  timestamp: Date;
  status: 'pending' | 'in-progress' | 'resolved';
  priority: 'low' | 'medium' | 'high';
  category: string;
  sentiment: 'positive' | 'neutral' | 'negative';
}

export default function App() {
  // Twitter agent state
  const [twitterView, setTwitterView] = useState<TwitterView>("dashboard");
  const [selectedTweet, setSelectedTweet] = useState<Tweet | null>(null);
  const [userRole, setUserRole] = useState<UserRole>("agent");

  // Twitter handlers
  const handleTweetSelect = (tweet: Tweet) => {
    setSelectedTweet(tweet);
    setTwitterView("conversation");
  };

  const handleTwitterBack = () => {
    setTwitterView("dashboard");
    setSelectedTweet(null);
  };

  const handleTwitterStatusChange = (status: Tweet['status']) => {
    if (selectedTweet) {
      setSelectedTweet({ ...selectedTweet, status });
    }
  };

  const handleRoleSwitch = (role: string) => {
    setUserRole(role as UserRole);
    setTwitterView("dashboard");
    setSelectedTweet(null);
  };

  const renderTwitterView = () => {
    switch (twitterView) {
      case "dashboard":
        // Render different dashboard based on user role
        switch (userRole) {
          case "agent":
            return (
              <AgentDashboard
                onTweetSelect={handleTweetSelect}
                onViewAnalytics={() => setTwitterView("analytics")}
                onViewSettings={() => setTwitterView("settings")}
                onSwitchRole={handleRoleSwitch}
              />
            );
          case "manager":
            return (
              <ManagerDashboard
                onBack={handleTwitterBack}
                onViewSettings={() => setTwitterView("settings")}
                onSwitchRole={handleRoleSwitch}
              />
            );
          case "director":
            return (
              <DirectorDashboard
                onBack={handleTwitterBack}
                onViewSettings={() => setTwitterView("settings")}
                onSwitchRole={handleRoleSwitch}
              />
            );
          default:
            return null;
        }
      case "conversation":
        return selectedTweet ? (
          <TwitterConversation
            tweet={selectedTweet}
            onBack={handleTwitterBack}
            onStatusChange={handleTwitterStatusChange}
          />
        ) : null;
      case "analytics":
        return <TwitterAnalytics onBack={handleTwitterBack} />;
      case "settings":
        return (
          <TwitterSettings 
            onBack={handleTwitterBack}
            onViewBackoffice={() => setTwitterView("backoffice")}
          />
        );
      case "backoffice":
        return <TwitterBackofficeSettings onBack={handleTwitterBack} />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      {/* Desktop Container for Twitter Agent */}
      <div className="w-full max-w-7xl h-[852px] bg-[#ffffff] relative overflow-hidden rounded-lg shadow-2xl border">
        {renderTwitterView()}
      </div>
    </div>
  );
}
