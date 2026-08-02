"use client";

export default function EmployeeIntro({ name }) {
  return (
    <main className="max-w-4xl mx-auto p-6">
      <div className="rounded-xl bg-gradient-to-br from-navy to-steel text-white p-10 mb-8">
        <h1 className="text-3xl font-bold mb-2">Welcome, {name?.split(" ")[0] || "there"} 👋</h1>
        <p className="text-gray-200 max-w-2xl">
          OrgBrain AI preserves your team's hard-won knowledge before it walks out the door.
          Use the tabs above to share what you know, ask questions grounded in real
          organizational history, or browse documented procedures.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <FeatureCard
          emoji="🎙️"
          title="Interview Agent"
          description="Share your expertise through a short, guided conversation. Type or speak your answers — the AI asks 5-6 adaptive questions and turns your knowledge into a structured SOP."
          href="/interview"
          cta="Start an Interview"
        />
        <FeatureCard
          emoji="💬"
          title="AI Twin"
          description="Ask your department's AI Twin a question. Every answer is grounded in real, approved SOPs from your team — not guesses."
          href="/twin-chat"
          cta="Ask a Question"
        />
        <FeatureCard
          emoji="📋"
          title="SOP Library"
          description="Browse structured, step-by-step Standard Operating Procedures captured from your colleagues' interviews."
          href="/sop"
          cta="Browse SOPs"
        />
      </div>

      <div className="card mt-8">
        <h3 className="font-semibold text-navy mb-2">How it fits together</h3>
        <p className="text-sm text-gray-600 leading-relaxed">
          Every interview you complete is turned into a detailed SOP by AI, then embedded into a
          searchable knowledge base for your department. When any employee asks the AI Twin a
          question, it retrieves the most relevant SOPs and answers using only that grounded
          information — this is called <strong>Retrieval-Augmented Generation (RAG)</strong>,
          and it's what keeps the Twin's answers accurate instead of guessed.
        </p>
      </div>
    </main>
  );
}

function FeatureCard({ emoji, title, description, href, cta }) {
  return (
    <a href={href} className="card hover:shadow-lg hover:-translate-y-0.5 transition-all flex flex-col">
      <span className="text-3xl mb-3">{emoji}</span>
      <h3 className="font-semibold text-navy mb-2">{title}</h3>
      <p className="text-sm text-gray-500 flex-1">{description}</p>
      <span className="text-steel text-sm font-medium mt-4">{cta} →</span>
    </a>
  );
}
