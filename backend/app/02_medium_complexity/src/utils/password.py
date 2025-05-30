from typing import Any



const SALT_ROUNDS = 10
/**
 * Hash a password using bcrypt
 * @param password Plain text password
 * @returns Hashed password
 */
async function hashPassword(password: str): Promise<string> {
  return bcrypt.hash(password, SALT_ROUNDS)
}
/**
 * Compare a plain text password with a hashed password
 * @param password Plain text password
 * @param hashedPassword Hashed password to compare against
 * @returns Whether the passwords match
 */
async function comparePassword(password: str, hashedPassword: str): Promise<boolean> {
  return bcrypt.compare(password, hashedPassword)
}