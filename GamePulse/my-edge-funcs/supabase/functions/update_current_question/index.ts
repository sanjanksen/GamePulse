// @ts-ignore
import { serve } from "https://deno.land/std@0.177.0/http/server.ts";
// @ts-ignore
import { createClient } from "https://cdn.jsdelivr.net/npm/@supabase/supabase-js/+esm";

// Environment variables
// @ts-ignore
const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
// @ts-ignore
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);

// Example questions with timestamps and additional info
const questions = [
  { 
    time: 0, 
    Question: "If the next play is a pass, is the next pass going to be complete?", 
    Tip: "So far in this game, Brady has completed 43 of 62 pass attempts for a pass percantage of 69.4%", 
    Answer: "No",
    Choices: ["Yes", "No"]
  },
  { 
    time: 40, 
    Question: "Are the Patriots going to score this drive?", 
    Tip: "The Patriots have scored on 3 drives of their last 12 offensive drives (25%)", 
    Answer: "Yes",
    Choices: ["Yes", "No"]
  },
  { 
    time: 67, 
    Question: "Will there be a flag on the next play?", 
    Tip: "At the end of a game, defenders are more likely to commit penalties resulting in a flag.", 
    Answer: "No",
    Choices: ["Yes", "No"]
  },
  { 
    time: 105, 
    Question: "Is Brady going to rush on the next play?", 
    Tip: "Brady is rarely known to be a popular rushing quarterback.", 
    Answer: "No",
    Choices: ["Yes", "No"]
  },
  { 
    time: 123, 
    Question: "Is Brady going to celebrate for winning the Super Bowl?", 
    Tip: "Winning the Super Bowl is a big deal!", 
    Answer: "No",
    Choices: ["Yes", "No"]
  },
];

serve(async (req: Request) => {
  try {
    const { gameCode } = await req.json().catch(() => ({}));
    if (!gameCode) {
      return new Response(JSON.stringify({ error: "Missing gameCode" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    // Fetch the lobby row
    const { data: lobbies, error: fetchError } = await supabase
      .from("lobbies")
      .select("*")
      .eq("code", gameCode);

    if (fetchError) {
      return new Response(JSON.stringify({ error: fetchError.message }), { status: 500, headers: { "Content-Type": "application/json" } });
    }

    if (!lobbies || lobbies.length === 0) {
      return new Response(JSON.stringify({ error: "Game code not found" }), { status: 404, headers: { "Content-Type": "application/json" } });
    }

    const lobby = lobbies[0];
    if (!lobby.beginning_time) {
      return new Response(JSON.stringify({ error: "Lobby has no beginning_time set" }), { status: 400, headers: { "Content-Type": "application/json" } });
    }

    // Calculate elapsed time
    const now = new Date();
    const beginningTime = new Date(lobby.beginning_time);
    const elapsedSeconds = (now.getTime() - beginningTime.getTime()) / 1000;

    // Determine current question
    let currentQuestion = {
      Question: "N/A",
      Tip: "",
      Answer: "",
      Choices: ["Yes", "No"]
    };
    for (const q of questions) {
      if (elapsedSeconds >= q.time) currentQuestion = {
        Question: q.Question,
        Tip: q.Tip,
        Answer: q.Answer,
        Choices: q.Choices
      };
      else break;
    }

    // Update the lobby's current_question (as a JSON object)
    const { data, error } = await supabase
      .from("lobbies")
      .update({ current_question: currentQuestion })
      .eq("code", gameCode)
      .select();

    if (error) {
      return new Response(JSON.stringify({ error: error.message }), { status: 500, headers: { "Content-Type": "application/json" } });
    }

    return new Response(JSON.stringify({ message: "Current question updated", current_question: currentQuestion }), { status: 200, headers: { "Content-Type": "application/json" } });

  } catch (err) {
    // @ts-ignore
    return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: { "Content-Type": "application/json" } });
  }
});
