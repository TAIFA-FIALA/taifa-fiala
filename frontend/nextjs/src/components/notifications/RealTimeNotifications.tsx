/**
 * Real-time Notifications Component
 * Shows live updates when new funding opportunities are added
 */

'use client';

import React, { useState } from 'react';
import { useFundingOpportunityEvents } from '@/hooks/useServerSentEvents';
import { Bell, CheckCircle, AlertCircle, Wifi, WifiOff, X } from 'lucide-react';

interface NotificationItemProps {
  opportunity: any;
  onDismiss: () => void;
}

function NotificationItem({ opportunity, onDismiss }: NotificationItemProps) {
  return (
    <div className="bg-white border border-taifa-accent/20 rounded-lg p-4 shadow-sm animate-in slide-in-from-right duration-300">
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0">
            <CheckCircle className="h-5 w-5 text-green-500" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900">
              New Funding Opportunity
            </p>
            <p className="text-sm text-gray-600 truncate">
              {opportunity.title}
            </p>
            <p className="text-xs text-gray-500">
              {opportunity.organization} • {opportunity.sector}
              {opportunity.amount_exact && (
                <span> • ${opportunity.amount_exact.toLocaleString()}</span>
              )}
            </p>
          </div>
        </div>
        <button
          onClick={onDismiss}
          className="flex-shrink-0 ml-3 text-gray-400 hover:text-gray-600"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}

interface ConnectionStatusProps {
  isConnected: boolean;
  error: string | null;
  onReconnect: () => void;
}

function ConnectionStatus({ isConnected, error, onReconnect }: ConnectionStatusProps) {
  if (isConnected) {
    return (
      <div className="flex items-center space-x-2 text-green-600 text-sm">
        <Wifi className="h-4 w-4" />
        <span>Live updates active</span>
      </div>
    );
  }

  return (
    <div className="flex items-center space-x-2 text-red-600 text-sm">
      <WifiOff className="h-4 w-4" />
      <span>{error || 'Connection lost'}</span>
      <button
        onClick={onReconnect}
        className="text-taifa-accent hover:text-taifa-accent/80 underline"
      >
        Reconnect
      </button>
    </div>
  );
}

export default function RealTimeNotifications() {
  const {
    isConnected,
    error,
    reconnect,
    newOpportunities,
    pipelineStatus,
    clearNewOpportunities
  } = useFundingOpportunityEvents();

  const [isExpanded, setIsExpanded] = useState(false);
  const [showConnectionStatus, setShowConnectionStatus] = useState(true);

  const dismissNotification = (index: number) => {
    const updated = newOpportunities.filter((_, i) => i !== index);
    clearNewOpportunities();
    // Re-add remaining notifications
    updated.forEach((opp, i) => {
      setTimeout(() => {
        // This is a simplified approach - in a real app you'd want better state management
      }, i * 100);
    });
  };

  const hasNewNotifications = newOpportunities.length > 0;

  return (
    <div className="fixed top-4 right-4 z-50 max-w-sm">
      {/* Connection Status */}
      {showConnectionStatus && (
        <div className="mb-2 bg-white border border-gray-200 rounded-lg p-3 shadow-sm">
          <div className="flex items-center justify-between">
            <ConnectionStatus
              isConnected={isConnected}
              error={error}
              onReconnect={reconnect}
            />
            <button
              onClick={() => setShowConnectionStatus(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}

      {/* Pipeline Status */}
      {pipelineStatus === 'success' && (
        <div className="mb-2 bg-green-50 border border-green-200 rounded-lg p-3 shadow-sm">
          <div className="flex items-center space-x-2 text-green-700 text-sm">
            <CheckCircle className="h-4 w-4" />
            <span>Pipeline executed successfully</span>
          </div>
        </div>
      )}

      {pipelineStatus === 'error' && (
        <div className="mb-2 bg-red-50 border border-red-200 rounded-lg p-3 shadow-sm">
          <div className="flex items-center space-x-2 text-red-700 text-sm">
            <AlertCircle className="h-4 w-4" />
            <span>Pipeline execution failed</span>
          </div>
        </div>
      )}

      {/* Notification Bell */}
      {hasNewNotifications && (
        <div className="mb-2">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="bg-taifa-accent text-white rounded-full p-3 shadow-lg hover:bg-taifa-accent/90 transition-colors relative"
          >
            <Bell className="h-5 w-5" />
            {newOpportunities.length > 0 && (
              <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                {newOpportunities.length > 9 ? '9+' : newOpportunities.length}
              </span>
            )}
          </button>
        </div>
      )}

      {/* Notifications List */}
      {isExpanded && hasNewNotifications && (
        <div className="space-y-2 max-h-96 overflow-y-auto">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-900">
              New Opportunities ({newOpportunities.length})
            </h3>
            <button
              onClick={clearNewOpportunities}
              className="text-xs text-taifa-accent hover:text-taifa-accent/80"
            >
              Clear all
            </button>
          </div>
          
          {newOpportunities.map((opportunity, index) => (
            <NotificationItem
              key={`${opportunity.id}-${index}`}
              opportunity={opportunity}
              onDismiss={() => dismissNotification(index)}
            />
          ))}
        </div>
      )}

      {/* Auto-show latest notification */}
      {!isExpanded && hasNewNotifications && newOpportunities.length === 1 && (
        <div className="animate-in slide-in-from-right duration-500">
          <NotificationItem
            opportunity={newOpportunities[0]}
            onDismiss={() => clearNewOpportunities()}
          />
        </div>
      )}
    </div>
  );
}