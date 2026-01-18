"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useSession, signOut } from "@/lib/auth-client";
import TaskList from "@/components/TaskList";

export default function TasksPage() {
  const router = useRouter();
  const { data: session, isPending } = useSession();
  const [showDropdown, setShowDropdown] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  useEffect(() => {
    if (!isPending && !session) {
      router.push("/login");
    }
  }, [session, isPending, router]);

  const handleLogout = async () => {
    setIsLoggingOut(true);
    try {
      await signOut();
      router.push("/login");
      router.refresh();
    } catch (error) {
      console.error("Logout failed:", error);
    } finally {
      setIsLoggingOut(false);
    }
  };

  if (isPending) {
    return (
      <div className="min-h-screen bg-[var(--background)] flex flex-col items-center justify-center">
        <div className="w-12 h-12 rounded-full border-4 border-[var(--muted)] border-t-[var(--gradient-start)] animate-spin" />
        <p className="mt-4 text-[var(--muted-foreground)]">Loading...</p>
      </div>
    );
  }

  if (!session) {
    return null;
  }

  const user = session.user;
  const userInitial = user?.name?.charAt(0).toUpperCase() || user?.email?.charAt(0).toUpperCase() || "U";

  return (
    <div className="min-h-screen bg-[var(--background)] pb-20">
      {/* TaskFlow logo - top left corner */}
      <div className="px-4 sm:px-6 lg:px-8 py-4">
        <Link href="/" className="inline-flex items-center gap-2 group">
          <div className="w-9 h-9 rounded-xl gradient-bg flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
          </div>
          <span className="text-xl font-bold group-hover:text-[var(--gradient-start)] transition-colors">
            TaskFlow
          </span>
        </Link>
      </div>

      {/* Welcome section with gradient */}
      <div className="gradient-bg">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-white mb-1">
                Welcome back, {user?.name?.split(" ")[0] || "there"}!
              </h1>
              <p className="text-white/70">
                Here&apos;s what&apos;s on your list today
              </p>
            </div>
            <div className="hidden sm:flex items-center gap-2 px-4 py-2 bg-white/10 rounded-xl backdrop-blur">
              <svg className="w-5 h-5 text-white/70" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span className="text-white/90 text-sm font-medium">
                {new Date().toLocaleDateString("en-US", {
                  weekday: "long",
                  month: "short",
                  day: "numeric",
                })}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 -mt-4">
        <TaskList />
      </main>

      {/* Profile badge - fixed bottom left */}
      <div className="fixed bottom-6 left-6 z-50">
        <div className="relative">
          <button
            onClick={() => setShowDropdown(!showDropdown)}
            className="w-12 h-12 rounded-full bg-[var(--gradient-start)] hover:bg-[var(--gradient-mid)] flex items-center justify-center shadow-lg hover:shadow-xl transition-all duration-200 ring-4 ring-white dark:ring-[var(--background)]"
          >
            <span className="text-white font-bold text-lg">{userInitial}</span>
          </button>

          {/* Dropdown menu */}
          {showDropdown && (
            <>
              <div className="fixed inset-0 z-10" onClick={() => setShowDropdown(false)} />
              <div className="absolute bottom-full left-0 mb-2 w-64 bg-[var(--card)] border border-[var(--border)] rounded-xl shadow-xl z-20 animate-scale-in overflow-hidden">
                <div className="px-4 py-3 bg-[var(--muted)]">
                  <p className="text-sm font-semibold truncate">{user?.name}</p>
                  <p className="text-xs text-[var(--muted-foreground)] truncate">{user?.email}</p>
                </div>
                <div className="border-t border-[var(--border)] py-1">
                  <button
                    onClick={handleLogout}
                    disabled={isLoggingOut}
                    className="flex items-center gap-3 w-full px-4 py-2.5 text-sm text-[var(--error)] hover:bg-[var(--error-light)] transition-colors"
                  >
                    {isLoggingOut ? (
                      <div className="spinner w-5 h-5" />
                    ) : (
                      <div className="w-6 h-6 rounded-full bg-[var(--gradient-start)] flex items-center justify-center">
                        <span className="text-white font-semibold text-xs">{userInitial}</span>
                      </div>
                    )}
                    {isLoggingOut ? "Signing out..." : "Sign out"}
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
