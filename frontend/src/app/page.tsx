import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-b from-blue-50 to-white">
      <main className="text-center px-4">
        <h1 className="text-5xl font-bold text-gray-900 mb-4">
          Todo App
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-md">
          A simple, powerful task management app to help you stay organized.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/login"
            className="px-8 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
          >
            Sign In
          </Link>
          <Link
            href="/signup"
            className="px-8 py-3 bg-white text-blue-600 font-medium rounded-lg border-2 border-blue-600 hover:bg-blue-50 transition-colors"
          >
            Create Account
          </Link>
        </div>
      </main>
      <footer className="absolute bottom-4 text-gray-500 text-sm">
        Phase II: Full-Stack Web Application
      </footer>
    </div>
  );
}
