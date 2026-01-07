/**
 * Backend API Client
 * T020: Complete implementation with all chat and conversation methods
 *
 * Implements API contract defined in specs/003-ai-chatbot/contracts/chat-api.yaml
 */

import type { ChatRequest, ChatResponse, Conversation, Message } from '../types/chat';

// Backend URL for proxy routes
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

/**
 * API Error class for structured error handling
 */
export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public code?: string,
    public details?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * Backend API Client
 * Handles all HTTP communication with the FastAPI backend
 */
class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  /**
   * Set JWT token for authenticated requests
   * @param token JWT token string or null to clear
   */
  setToken(token: string | null) {
    this.token = token;
  }

  /**
   * Get headers for API requests
   * @returns Headers object with Content-Type and Authorization
   */
  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  /**
   * Handle API response and parse errors
   * @param response Fetch response object
   * @returns Parsed JSON data
   * @throws ApiError if response is not ok
   */
  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      let errorMessage = 'An error occurred';
      let errorCode = 'UNKNOWN_ERROR';
      let errorDetails;

      try {
        const errorData = await response.json();
        errorMessage = errorData.message || errorData.detail || errorMessage;
        errorCode = errorData.code || errorData.error || errorCode;
        errorDetails = errorData.details;
      } catch {
        // If error response is not JSON, use status text
        errorMessage = response.statusText || errorMessage;
      }

      throw new ApiError(errorMessage, response.status, errorCode, errorDetails);
    }

    return response.json();
  }

  /**
   * Register a new user
   * @param email User email address
   * @param password User password (min 8 characters)
   * @param name Optional user name
   * @returns Object with access_token and token_type
   * @throws ApiError on validation or registration errors
   */
  async register(email: string, password: string, name?: string): Promise<{ access_token: string; token_type: string }> {
    // Use frontend's API route for proxying to backend
    const response = await fetch(`/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, name }),
    });

    return this.handleResponse<{ access_token: string; token_type: string }>(response);
  }

  /**
   * Login with existing credentials
   * @param email User email address
   * @param password User password
   * @returns Object with access_token and token_type
   * @throws ApiError on authentication errors
   */
  async login(email: string, password: string): Promise<{ access_token: string; token_type: string }> {
    // Use frontend's API route for proxying to backend
    const response = await fetch(`/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    return this.handleResponse<{ access_token: string; token_type: string }>(response);
  }

  /**
   * Get current user information
   * @returns User object with id, email, name, and created_at
   * @throws ApiError if not authenticated
   */
  async getCurrentUser(): Promise<{ id: number; email: string; name: string | null; created_at: string }> {
    // Use frontend's API route for proxying to backend
    const response = await fetch(`/api/auth/me`, {
      method: 'GET',
      headers: this.getHeaders(),
    });

    return this.handleResponse<{ id: number; email: string; name: string | null; created_at: string }>(response);
  }

  /**
   * Send a chat message to the AI
   * @param request Chat request with message and optional conversation_id
   * @returns Chat response with AI message and conversation_id
   * @throws ApiError on network or authentication errors
   */
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    // Use frontend's API route for proxying to backend
    const response = await fetch(`/api/chat`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(request),
    });

    return this.handleResponse<ChatResponse>(response);
  }

  /**
   * Send a chat message with streaming response
   * @param request Chat request with message and optional conversation_id
   * @returns ReadableStream of server-sent events
   * @throws ApiError on network or authentication errors
   */
  async sendMessageStream(request: ChatRequest): Promise<ReadableStream<Uint8Array>> {
    // Use frontend's API route for proxying to backend
    const response = await fetch(`/api/chat/stream`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      // For streaming, we need to read the error before throwing
      const errorText = await response.text();
      throw new ApiError(
        errorText || 'Streaming request failed',
        response.status
      );
    }

    if (!response.body) {
      throw new ApiError('No response body received', 500);
    }

    return response.body;
  }

  /**
   * Get all conversations for the authenticated user
   * @param limit Maximum number of conversations to return (1-100, default 50)
   * @param offset Pagination offset (default 0)
   * @returns Object with conversations array and total count
   * @throws ApiError on network or authentication errors
   */
  async getConversations(
    limit: number = 50,
    offset: number = 0
  ): Promise<{ conversations: Conversation[]; total: number }> {
    const params = new URLSearchParams({
      limit: String(limit),
      offset: String(offset),
    });

    // Use frontend's API route for proxying to backend
    const response = await fetch(
      `/api/conversations?${params.toString()}`,
      {
        method: 'GET',
        headers: this.getHeaders(),
      }
    );

    return this.handleResponse<{ conversations: Conversation[]; total: number }>(
      response
    );
  }

  /**
   * Get a specific conversation with its message history
   * @param id Conversation ID
   * @returns Object with conversation and messages array
   * @throws ApiError if conversation not found or access denied
   */
  async getConversation(
    id: string
  ): Promise<{ conversation: Conversation; messages: Message[] }> {
    // Use frontend's API route for proxying to backend
    const response = await fetch(
      `/api/conversations/${id}`,
      {
        method: 'GET',
        headers: this.getHeaders(),
      }
    );

    return this.handleResponse<{ conversation: Conversation; messages: Message[] }>(
      response
    );
  }

  /**
   * Delete a conversation and all its messages
   * @param id Conversation ID
   * @throws ApiError if conversation not found or access denied
   */
  async deleteConversation(id: string): Promise<void> {
    // Use frontend's API route for proxying to backend
    const response = await fetch(
      `/api/conversations/${id}`,
      {
        method: 'DELETE',
        headers: this.getHeaders(),
      }
    );

    await this.handleResponse<{ message: string }>(response);
  }

  /**
   * Check if the API is reachable
   * @returns true if API is healthy, false otherwise
   */
  async healthCheck(): Promise<boolean> {
    try {
      // Use frontend's API route for proxying to backend
      const response = await fetch(`/api/health`, {
        method: 'GET',
      });
      return response.ok;
    } catch {
      return false;
    }
  }
}

/**
 * Singleton API client instance
 * Import and use this instance throughout the application
 */
export const apiClient = new ApiClient(BACKEND_URL);