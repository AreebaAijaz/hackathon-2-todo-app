import { betterAuth } from "better-auth";
import { Pool } from "pg";

// Create Postgres pool for Neon (only if DATABASE_URL is available)
const pool = process.env.DATABASE_URL
  ? new Pool({
      connectionString: process.env.DATABASE_URL,
      ssl: {
        rejectUnauthorized: false,
      },
    })
  : null;

export const auth = betterAuth({
  database: pool!,
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8,
  },
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // 1 day
    cookieCache: {
      enabled: true,
      maxAge: 60 * 5, // 5 minutes
    },
  },
  trustedOrigins: [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:30080",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:30080",
    // Minikube IP (common default)
    "http://192.168.49.2:30080",
    process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : "",
    process.env.NEXT_PUBLIC_APP_URL || "",
  ].filter(Boolean),
});

export type Session = typeof auth.$Infer.Session;
