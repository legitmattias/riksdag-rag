// src/routes/+page.server.ts
import { redirect } from '@sveltejs/kit';

/**
 * Redirect root route (/) to /dashboard
 */
export function load() {
  throw redirect(307, '/dashboard');
}
