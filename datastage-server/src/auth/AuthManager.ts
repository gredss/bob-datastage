/**
 * Authentication Manager for Cloud Pak for Data
 * Handles token generation, caching, and refresh
 */

import axios, { AxiosInstance } from 'axios';
import { ENV, API_ENDPOINTS, CACHE_KEYS } from '../config/constants.js';
import { CPDAuthResponse, AuthenticationError } from '../config/types.js';
import { SimpleCache } from '../utils/cache.js';
import { logger } from '../utils/logger.js';

export class AuthManager {
  private httpClient: AxiosInstance;
  private cache: SimpleCache;
  private tokenExpiration: number = 0;

  constructor() {
    this.httpClient = axios.create({
      baseURL: ENV.CPD_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.cache = new SimpleCache();
  }

  /**
   * Get a valid bearer token, refreshing if necessary
   */
  async getToken(): Promise<string> {
    // Check if we have a cached valid token
    const cachedToken = this.cache.get<string>(CACHE_KEYS.AUTH_TOKEN);
    if (cachedToken && this.isTokenValid()) {
      logger.debug('Using cached authentication token');
      return cachedToken;
    }

    // Authenticate to get a new token
    logger.info('Authenticating with Cloud Pak for Data');
    return await this.authenticate();
  }

  /**
   * Authenticate with CPD and get a bearer token
   */
  private async authenticate(): Promise<string> {
    try {
      const authPayload = this.buildAuthPayload();
      
      logger.debug('Sending authentication request to CPD');
      const response = await this.httpClient.post<CPDAuthResponse>(
        API_ENDPOINTS.AUTHORIZE,
        authPayload
      );

      const { token, expires_in, expiration } = response.data;

      // Cache the token
      this.tokenExpiration = expiration || Date.now() + expires_in * 1000;
      this.cache.set(CACHE_KEYS.AUTH_TOKEN, token, expires_in - 60); // Refresh 1 min before expiry

      logger.info('Successfully authenticated with CPD');
      return token;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || error.message;
        const statusCode = error.response?.status;
        
        logger.error('Authentication failed', { message, statusCode });
        
        throw new AuthenticationError(
          `Failed to authenticate with CPD: ${message}`,
          { statusCode, originalError: error }
        );
      }
      throw error;
    }
  }

  /**
   * Build authentication payload based on available credentials
   */
  private buildAuthPayload(): Record<string, string> {
    // Use username/password authentication
    if (ENV.CPD_USERNAME && ENV.CPD_PASSWORD) {
      logger.debug('Using username/password authentication');
      return {
        username: ENV.CPD_USERNAME,
        password: ENV.CPD_PASSWORD,
      };
    }

    throw new AuthenticationError(
      'No authentication credentials provided. Set CPD_API_KEY or CPD_USERNAME/CPD_PASSWORD environment variables.'
    );
  }

  /**
   * Check if the current token is still valid
   */
  private isTokenValid(): boolean {
    if (this.tokenExpiration === 0) {
      return false;
    }

    // Consider token invalid if it expires in less than 60 seconds
    const now = Date.now();
    const bufferTime = 60 * 1000; // 60 seconds
    return this.tokenExpiration > now + bufferTime;
  }

  /**
   * Force token refresh
   */
  async refreshToken(): Promise<string> {
    logger.info('Forcing token refresh');
    this.cache.delete(CACHE_KEYS.AUTH_TOKEN);
    this.tokenExpiration = 0;
    return await this.authenticate();
  }

  /**
   * Clear cached authentication data
   */
  clearCache(): void {
    logger.debug('Clearing authentication cache');
    this.cache.delete(CACHE_KEYS.AUTH_TOKEN);
    this.tokenExpiration = 0;
  }

  /**
   * Validate that CPD URL is configured
   */
  validateConfiguration(): void {
    if (!ENV.CPD_URL) {
      throw new AuthenticationError(
        'CPD_URL environment variable is required'
      );
    }

    if (!ENV.CPD_USERNAME || !ENV.CPD_PASSWORD) {
      throw new AuthenticationError(
        'CPD_USERNAME and CPD_PASSWORD must be provided'
      );
    }

    // Validate URL format
    try {
      new URL(ENV.CPD_URL);
    } catch {
      throw new AuthenticationError(
        `Invalid CPD_URL format: ${ENV.CPD_URL}`
      );
    }
  }
}

// Made with Bob
