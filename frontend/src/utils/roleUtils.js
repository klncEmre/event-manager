/**
 * Role utility functions for the application
 */

// Role constants
export const ROLES = {
  ADMIN: 'admin',
  PUBLISHER: 'publisher',
  USER: 'user'
};

/**
 * Check if the user is an admin
 * @param {Object} user - The user object
 * @returns {boolean} - True if user is an admin
 */
export const isAdmin = (user) => {
  return user && user.role === ROLES.ADMIN;
};

/**
 * Check if the user is a publisher/event manager
 * @param {Object} user - The user object
 * @returns {boolean} - True if user is a publisher
 */
export const isPublisher = (user) => {
  return user && user.role === ROLES.PUBLISHER;
};

/**
 * Check if the user is a regular user
 * @param {Object} user - The user object 
 * @returns {boolean} - True if user is a regular user
 */
export const isRegularUser = (user) => {
  return user && user.role === ROLES.USER;
};

/**
 * Check if the user can create/manage events
 * @param {Object} user - The user object
 * @returns {boolean} - True if user can create/manage events
 */
export const canManageEvents = (user) => {
  return isAdmin(user) || isPublisher(user);
};

/**
 * Get appropriate homepage for user based on role
 * @param {Object} user - The user object
 * @returns {string} - The appropriate homepage path
 */
export const getHomePageForUser = (user) => {
  if (isAdmin(user)) return '/admin';
  if (isPublisher(user)) return '/my-events';
  return '/events';
};

/**
 * Get readable role name for display
 * @param {string} role - The role value
 * @returns {string} - Human-readable role name
 */
export const getRoleName = (role) => {
  switch (role) {
    case ROLES.ADMIN:
      return 'Administrator';
    case ROLES.PUBLISHER:
      return 'Platform Manager';
    case ROLES.USER:
      return 'User';
    default:
      return 'Guest';
  }
}; 