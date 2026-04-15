/**
 * Retry utility with exponential backoff
 */

import { logger } from './logger.js';

interface RetryConfig {
  MAX_RETRIES: number;
  INITIAL_DELAY: number;
  MAX_DELAY: number;
  BACKOFF_MULTIPLIER: number;
}

/**
 * Retry a function with exponential backoff
 */
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  config: RetryConfig,
  attempt: number = 1
): Promise<T> {
  try {
    return await fn();
  } catch (error) {
    if (attempt >= config.MAX_RETRIES) {
      logger.error(`Max retries (${config.MAX_RETRIES}) exceeded`, { error });
      throw error;
    }

    const delay = Math.min(
      config.INITIAL_DELAY * Math.pow(config.BACKOFF_MULTIPLIER, attempt - 1),
      config.MAX_DELAY
    );

    logger.warn(`Retry attempt ${attempt}/${config.MAX_RETRIES} after ${delay}ms`, {
      error: error instanceof Error ? error.message : String(error),
    });

    await sleep(delay);
    return retryWithBackoff(fn, config, attempt + 1);
  }
}

/**
 * Sleep for specified milliseconds
 */
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// Made with Bob
