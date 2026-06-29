"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface Question {
  q: string;
  options: string[];
  correct: number;
  explanation: string;
}

const QUESTIONS: Question[] = [
  {
    q: "What savings rate does FinBro recommend for professionals?",
    options: ["10%", "15%", "20%", "25%"],
    correct: 2,
    explanation: "Professionals should aim to save 20% of their monthly salary.",
  },
  {
    q: "Which debt payoff method targets highest interest first?",
    options: ["Snowball", "Avalanche", "Minimum payment", "Balance transfer"],
    correct: 1,
    explanation: "The Avalanche method pays off debts with the highest interest rate first.",
  },
  {
    q: "How many FBT tokens do you earn for completing a goal?",
    options: ["25", "50", "75", "100"],
    correct: 3,
    explanation: "Completing a savings goal earns you 100 FBT tokens!",
  },
  {
    q: "At what spending percentage do students get a yellow warning?",
    options: ["50%", "70%", "80%", "95%"],
    correct: 2,
    explanation: "Students receive a yellow warning at 80% of their monthly spending limit.",
  },
  {
    q: "What type of retirement projection does FinBro use?",
    options: ["Monte Carlo", "Compound interest", "Random walk", "Linear extrapolation"],
    correct: 1,
    explanation: "FinBro uses compound interest formulas for retirement projections.",
  },
];

export default function QuizPage() {
  const [current, setCurrent] = useState(0);
  const [selected, setSelected] = useState<number | null>(null);
  const [score, setScore] = useState(0);
  const [finished, setFinished] = useState(false);

  const question = QUESTIONS[current];

  function handleAnswer(idx: number) {
    if (selected !== null) return;
    setSelected(idx);
    if (idx === question.correct) setScore((s) => s + 1);
  }

  function next() {
    if (current + 1 >= QUESTIONS.length) {
      setFinished(true);
    } else {
      setCurrent((c) => c + 1);
      setSelected(null);
    }
  }

  function restart() {
    setCurrent(0);
    setSelected(null);
    setScore(0);
    setFinished(false);
  }

  if (finished) {
    return (
      <div className="mx-auto max-w-lg space-y-6 text-center">
        <h1 className="text-3xl font-bold">Quiz Complete!</h1>
        <Card>
          <CardContent className="pt-8">
            <p className="text-5xl font-bold text-primary">{score}/{QUESTIONS.length}</p>
            <p className="mt-2 text-muted-foreground">
              {score === QUESTIONS.length ? "Perfect score! You're a finance pro!" : "Keep learning with FinBro!"}
            </p>
            <Button className="mt-6" onClick={restart}>Try Again</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-lg space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Finance Quiz</h1>
        <p className="text-muted-foreground">Question {current + 1} of {QUESTIONS.length}</p>
      </div>

      <AnimatePresence mode="wait">
        <motion.div key={current} initial={{ x: 20, opacity: 0 }} animate={{ x: 0, opacity: 1 }} exit={{ x: -20, opacity: 0 }}>
          <Card>
            <CardHeader><CardTitle>{question.q}</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              {question.options.map((opt, idx) => {
                let cls = "w-full rounded-lg border p-4 text-left transition-colors hover:bg-muted";
                if (selected !== null) {
                  if (idx === question.correct) cls += " border-primary bg-primary/10";
                  else if (idx === selected) cls += " border-secondary bg-secondary/10";
                }
                return (
                  <button key={idx} className={cls} onClick={() => handleAnswer(idx)} disabled={selected !== null}>
                    {opt}
                  </button>
                );
              })}
              {selected !== null && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mt-4 rounded-lg bg-muted p-4 text-sm">
                  {question.explanation}
                  <Button className="mt-3 w-full" onClick={next}>
                    {current + 1 >= QUESTIONS.length ? "See Results" : "Next Question"}
                  </Button>
                </motion.div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
