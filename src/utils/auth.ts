import * as jwt from 'jsonwebtoken';
import { User } from '../models/User';

const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';
const TOKEN_EXPIRY = '24h';

interface TokenPayload {
  userId: string;
  email: string;
  role: string;
}

/**
 * Generate a JWT token for a user
 * @param user User to generate token for
 * @returns JWT token
 */
export function generateToken(user: User): string {
  const payload: TokenPayload = {
    userId: String(user.id),
    email: user.email,
    role: user.role,
  };
  return jwt.sign(payload, JWT_SECRET, { expiresIn: TOKEN_EXPIRY });
}

/**
 * Verify and decode a JWT token
 * @param token JWT token to verify
 * @returns Decoded token payload
 */
export function verifyToken(token: string): TokenPayload {
  try {
    return jwt.verify(token, JWT_SECRET) as TokenPayload;
  } catch (error) {
    throw new Error('Invalid token');
  }
}

/**
 * Extract token from authorization header
 * @param authHeader Authorization header value
 * @returns JWT token
 */
export function extractToken(authHeader: string): string {
  if (!authHeader.startsWith('Bearer ')) {
    throw new Error('Invalid authorization header');
  }
  return authHeader.substring(7);
}
