/**
 * React Hook for Server-Sent Events (SSE)
 * Provides real-time notifications from the backend
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import { getApiUrl } from '@/lib/api-config';

interface FundingOpportunityData {
  id: string;
  title: string;
  organization: string;
  sector: string;
  amount_exact?: number;
}

interface PipelineExecutionData {
  status: string;
  records_inserted?: number;
  message?: string;
}

interface DatabaseUpdateData {
  table: string;
  operation: string;
  count: number;
}

export interface SSEEvent {
  type: string;
  data: unknown;
  timestamp: string;
}

export interface SSEHookOptions {
  url: string;
  onEvent?: (event: SSEEvent) => void;
  onNewFundingOpportunity?: (data: FundingOpportunityData) => void;
  onPipelineExecution?: (data: PipelineExecutionData) => void;
  onCacheRefresh?: () => void;
  onDatabaseUpdate?: (data: DatabaseUpdateData) => void;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

export function useServerSentEvents(options: SSEHookOptions) {
  const {
    url,
    onEvent,
    onNewFundingOpportunity,
    onPipelineExecution,
    onCacheRefresh,
    onDatabaseUpdate,
    reconnectInterval = 5000,
    maxReconnectAttempts = 10
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [lastEvent, setLastEvent] = useState<SSEEvent | null>(null);
  const [connectionAttempts, setConnectionAttempts] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const handleEvent = useCallback((event: MessageEvent) => {
    try {
      const eventData: SSEEvent = JSON.parse(event.data);
      setLastEvent(eventData);
      setError(null);

      // Call generic event handler
      onEvent?.(eventData);

      // Call specific event handlers based on type
      switch (eventData.type) {
        case 'new_funding_opportunity':
          onNewFundingOpportunity?.(eventData.data as FundingOpportunityData);
          break;
        case 'pipeline_execution':
          onPipelineExecution?.(eventData.data as PipelineExecutionData);
          break;
        case 'cache_refresh':
          onCacheRefresh?.();
          break;
        case 'database_update':
          onDatabaseUpdate?.(eventData.data as DatabaseUpdateData);
          break;
        case 'connected':
          console.log('SSE connection established');
          break;
        case 'ping':
          // Keepalive ping - no action needed
          break;
        default:
          console.log('Unknown SSE event type:', eventData.type);
      }
    } catch (err) {
      console.error('Error parsing SSE event:', err);
      setError('Failed to parse event data');
    }
  }, [onEvent, onNewFundingOpportunity, onPipelineExecution, onCacheRefresh, onDatabaseUpdate]);

  const connect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    try {
      const eventSource = new EventSource(url);
      eventSourceRef.current = eventSource;

      eventSource.onopen = () => {
        setIsConnected(true);
        setConnectionAttempts(0);
        setError(null);
        console.log('SSE connection opened');
      };

      eventSource.onmessage = handleEvent;

      eventSource.onerror = (event) => {
        setIsConnected(false);
        setError('SSE connection error');
        console.error('SSE connection error:', event);

        // Use functional update to avoid stale closure
        setConnectionAttempts(currentAttempts => {
          if (currentAttempts < maxReconnectAttempts) {
            reconnectTimeoutRef.current = setTimeout(() => {
              console.log(`Attempting to reconnect SSE (attempt ${currentAttempts + 1}/${maxReconnectAttempts})`);
              connect();
            }, reconnectInterval);
            return currentAttempts + 1;
          } else {
            setError(`Failed to connect after ${maxReconnectAttempts} attempts`);
            return currentAttempts;
          }
        });
      };

    } catch (err) {
      setError('Failed to create SSE connection');
      console.error('Error creating SSE connection:', err);
    }
  }, [url, handleEvent, maxReconnectAttempts, reconnectInterval]);

  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    setIsConnected(false);
  }, []);

  const reconnect = useCallback(() => {
    disconnect();
    setConnectionAttempts(0);
    connect();
  }, [disconnect, connect]);

  useEffect(() => {
    // Prevent multiple connections by checking if one already exists
    if (!eventSourceRef.current || eventSourceRef.current.readyState === EventSource.CLOSED) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    isConnected,
    lastEvent,
    connectionAttempts,
    error,
    reconnect,
    disconnect
  };
}

// Convenience hook specifically for funding opportunities
export function useFundingOpportunityEvents() {
  const [newOpportunities, setNewOpportunities] = useState<FundingOpportunityData[]>([]);
  const [pipelineStatus, setPipelineStatus] = useState<string>('idle');

  const { isConnected, error, reconnect } = useServerSentEvents({
    url: getApiUrl('/api/v1/events/stream'),
    onNewFundingOpportunity: (data) => {
      setNewOpportunities(prev => [data, ...prev.slice(0, 9)]); // Keep last 10
      
      // Show notification
      if ('Notification' in window && Notification.permission === 'granted') {
        new Notification('New Funding Opportunity', {
          body: `${data.title} from ${data.organization}`,
          icon: '/favicon.ico'
        });
      }
    },
    onPipelineExecution: (data) => {
      setPipelineStatus(data.status);
      
      if (data.status === 'success' && data.records_inserted && data.records_inserted > 0) {
        console.log(`Pipeline success: ${data.records_inserted} new opportunities added`);
      }
    },
    onCacheRefresh: () => {
      // Trigger data refetch in components that use this hook
      window.dispatchEvent(new CustomEvent('taifa-cache-refresh'));
    }
  });

  // Request notification permission on mount
  useEffect(() => {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }, []);

  return {
    isConnected,
    error,
    reconnect,
    newOpportunities,
    pipelineStatus,
    clearNewOpportunities: () => setNewOpportunities([])
  };
}